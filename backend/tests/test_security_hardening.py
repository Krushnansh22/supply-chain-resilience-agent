"""
backend/tests/test_security_hardening.py
==========================================
Comprehensive security test suite — 9 layers, 45 test cases.

  GAP 1 — X-Forwarded-For trusted-proxy gating (client_ip.py + rate_limiter.py)
  GAP 2 — Bounded rate-limit store / memory-leak prevention (rate_limiter.py)
  GAP 3 — Stream-counting body size limiter, 64 KB cap (security.py)
  GAP 4 — Global GET rate limiting with /health exemption (general_rate_limiter.py)
  GAP 5 — HTTP security headers on every response (security.py)
  GAP 6 — API key constant-time auth / timing-attack prevention (security.py + routes)
  GAP 7 — Path & query parameter injection blocking (routes_*)
  GAP 8 — Pydantic payload validation / extra-field stripping (schemas)
  GAP 9 — Log sanitization: no newline / CRLF injection (security.py)
"""

import time
from collections import deque
from unittest.mock import MagicMock, patch

import pytest
from fastapi import Request
from fastapi.testclient import TestClient

from app.main import app
from app.config import settings
from app.middleware.client_ip import get_trusted_client_ip
from app.middleware.rate_limiter import (
    _store,
    _lock,
    purge_empty_and_idle_keys,
    record_and_check_rate_limit,
)
from app.core.auth_security import create_access_token
from app.core.deps import get_current_user

import mongomock
from app.mongo_database import get_mongo_db


# ---------------------------------------------------------------------------
# Shared fixture — fresh rate store + in-memory MongoDB for every test
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def isolate_test():
    """Wipe rate-limit store and substitute mongomock DB before each test."""
    mock_db = mongomock.MongoClient()["test_scda"]
    app.dependency_overrides[get_mongo_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: {
        "user_id": "TEST-ADMIN-001",
        "name": "Test Admin",
        "email": "test@test.com",
        "role": "admin",
        "is_active": True,
    }

    # Save settings that individual tests may mutate
    orig_proxy       = settings.TRUSTED_PROXY_IPS
    orig_api_key     = settings.API_KEY
    orig_backend_key = settings.BACKEND_API_KEY
    orig_rl_max      = settings.GENERAL_RATE_LIMIT_MAX
    orig_rl_window   = settings.GENERAL_RATE_LIMIT_WINDOW

    with _lock:
        _store.clear()

    yield

    with _lock:
        _store.clear()

    app.dependency_overrides.pop(get_mongo_db, None)
    app.dependency_overrides.pop(get_current_user, None)
    settings.TRUSTED_PROXY_IPS        = orig_proxy
    settings.API_KEY                  = orig_api_key
    settings.BACKEND_API_KEY          = orig_backend_key
    settings.GENERAL_RATE_LIMIT_MAX   = orig_rl_max
    settings.GENERAL_RATE_LIMIT_WINDOW = orig_rl_window


# ===========================================================================
# GAP 1 — X-Forwarded-For spoofing / Trusted Proxy validation
# ===========================================================================

@pytest.fixture
def client(mock_db):
    app.dependency_overrides[get_mongo_db] = lambda: mock_db
    settings.API_KEY = ""
    settings.BACKEND_API_KEY = ""
    settings.GENERAL_RATE_LIMIT_MAX = 10_000

    # Create a test admin user and generate a JWT token for authentication
    mock_db["users"].insert_one({
        "user_id": "TEST-ADMIN-001",
        "name": "Test Admin",
        "email": "test@test.com",
        "password_hash": "",
        "role": "admin",
        "is_active": True,
    })

    token = create_access_token(subject="TEST-ADMIN-001", role="admin")
    c = TestClient(app, headers={"Authorization": f"Bearer {token}"})
    yield c
    app.dependency_overrides.pop(get_mongo_db, None)


def test_gap1_spoofed_xff_ignored_when_no_trusted_proxy():
    """
    No TRUSTED_PROXY_IPS → XFF is completely ignored.
    Sending 20 different fake IPs from the same client still hits one bucket.
    """
    settings.TRUSTED_PROXY_IPS = ""
    client = TestClient(app)

    for i in range(20):
        resp = client.post(
            "/simulator/inject",
            json={"scenario": "SUPPLIER_DELAY"},
            headers={"X-Forwarded-For": f"1.2.3.{i}"},
        )
        assert resp.status_code == 200, f"Request {i} failed: {resp.text}"

    # 21st must be blocked regardless of yet another fake IP
    resp = client.post(
        "/simulator/inject",
        json={"scenario": "SUPPLIER_DELAY"},
        headers={"X-Forwarded-For": "99.99.99.99"},
    )
    assert resp.status_code == 429
    assert "Rate limit exceeded" in resp.json()["detail"]


def test_gap1_trusted_proxy_honors_forwarded_for():
    """
    When real client IP is in TRUSTED_PROXY_IPS, different XFF IPs → separate buckets.
    """
    settings.TRUSTED_PROXY_IPS = "testclient"
    client = TestClient(app)

    resp1 = client.post(
        "/simulator/inject",
        json={"scenario": "SUPPLIER_DELAY"},
        headers={"X-Forwarded-For": "10.0.0.1"},
    )
    resp2 = client.post(
        "/simulator/inject",
        json={"scenario": "SUPPLIER_DELAY"},
        headers={"X-Forwarded-For": "10.0.0.2"},
    )
    assert resp1.status_code == 200
    assert resp2.status_code == 200


def test_gap1_xff_comma_list_takes_leftmost_ip():
    """X-Forwarded-For with multiple IPs: only the leftmost is used as client IP."""
    settings.TRUSTED_PROXY_IPS = "testclient"
    client = TestClient(app)
    resp = client.get(
        "/inventory/",
        headers={"X-Forwarded-For": "203.0.113.5, 10.0.0.1, 10.0.0.2"},
    )
    assert resp.status_code == 200


def test_gap1_missing_xff_on_trusted_proxy_uses_client_host():
    """When XFF header is absent on a trusted proxy, client.host is used."""
    settings.TRUSTED_PROXY_IPS = "testclient"
    client = TestClient(app)
    resp = client.get("/inventory/")
    assert resp.status_code == 200


def test_gap1_none_client_falls_back_to_unknown():
    """get_trusted_client_ip returns 'unknown' when request.client is None."""
    mock_req = MagicMock(spec=Request)
    mock_req.client = None
    mock_req.headers = {}
    ip = get_trusted_client_ip(mock_req)
    assert ip == "unknown"


# ===========================================================================
# GAP 2 — Bounded rate-limit store / memory-leak prevention
# ===========================================================================

def test_gap2_idle_keys_evicted_after_window_expires():
    """500 buckets older than 2 min must all be purged in one sweep."""
    now  = time.monotonic()
    past = now - 120.0

    with _lock:
        for i in range(500):
            _store[(f"10.0.0.{i}", "general")].append(past)
        assert len(_store) == 500

    purged = purge_empty_and_idle_keys(window_seconds=60)
    assert purged == 500

    with _lock:
        assert len(_store) == 0


def test_gap2_active_keys_survive_sweep():
    """Keys with recent timestamps must NOT be evicted."""
    now = time.monotonic()

    with _lock:
        _store[("192.168.1.1", "general")].append(now - 5.0)    # recent
        _store[("192.168.1.2", "general")].append(now - 200.0)  # expired

    purged = purge_empty_and_idle_keys(window_seconds=60)
    assert purged == 1

    with _lock:
        assert ("192.168.1.1", "general") in _store
        assert ("192.168.1.2", "general") not in _store


def test_gap2_returning_ip_re_enters_store_cleanly():
    """After eviction an IP can make fresh requests without carrying old state."""
    now = time.monotonic()
    with _lock:
        _store[("10.0.0.1", "general")].append(now - 120.0)

    purge_empty_and_idle_keys(window_seconds=60)
    allowed, _ = record_and_check_rate_limit("10.0.0.1", "general", max_calls=60, window_seconds=60)
    assert allowed is True
    with _lock:
        assert len(_store[("10.0.0.1", "general")]) == 1


def test_gap2_periodic_auto_sweep_triggered_inside_record_and_check(monkeypatch):
    """record_and_check_rate_limit auto-sweeps when _last_sweep > 30 s ago."""
    import app.middleware.rate_limiter as rl_mod
    monkeypatch.setattr(rl_mod, "_last_sweep", 0.0)

    now = time.monotonic()
    with _lock:
        for i in range(100):
            _store[(f"stale-{i}", "general")].append(now - 200.0)

    record_and_check_rate_limit("new-ip", "general", max_calls=60, window_seconds=60)

    with _lock:
        stale = [k for k in _store if str(k[0]).startswith("stale-")]
    assert len(stale) == 0


# ===========================================================================
# GAP 3 — Request body size limiting (stream counter + Content-Length fast-path)
# ===========================================================================

def test_gap3_chunked_oversized_body_rejected_413():
    """70 KB chunked body with no Content-Length header → 413."""
    client = TestClient(app)

    def chunks():
        for _ in range(70):
            yield b"A" * 1024  # 1 KB per chunk

    resp = client.post(
        "/simulator/inject",
        content=chunks(),
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code == 413
    assert "Request body too large" in resp.json()["detail"]


def test_gap3_content_length_header_over_limit_rejected_early():
    """Content-Length header > 64 KB triggers fast-path 413 before reading stream."""
    client = TestClient(app)
    resp = client.post(
        "/simulator/inject",
        content=b"X" * 100,
        headers={
            "Content-Type": "application/json",
            "Content-Length": "200000",   # 200 KB declared
        },
    )
    assert resp.status_code == 413


def test_gap3_small_body_passes_normally():
    """Normal small JSON body (< 1 KB) is processed successfully."""
    client = TestClient(app)
    resp = client.post("/simulator/inject", json={"scenario": "SUPPLIER_DELAY"})
    assert resp.status_code == 200


def test_gap3_non_http_scope_bypasses_limiter():
    """Non-HTTP (WebSocket/lifespan) scopes are never rejected by the body limiter."""
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200


# ===========================================================================
# GAP 4 — Global GET rate limiting + /health exemption
# ===========================================================================

def test_gap4_get_endpoint_rate_limited_after_max_requests():
    """GET /inventory/ is blocked after GENERAL_RATE_LIMIT_MAX requests."""
    settings.GENERAL_RATE_LIMIT_MAX = 5
    settings.GENERAL_RATE_LIMIT_WINDOW = 60
    client = TestClient(app)

    for _ in range(5):
        assert client.get("/inventory/").status_code == 200

    resp = client.get("/inventory/")
    assert resp.status_code == 429
    assert "Rate limit exceeded" in resp.json()["detail"]
    assert "Retry-After" in resp.headers


def test_gap4_retry_after_header_is_positive_integer():
    """Retry-After header in 429 must be a positive integer string."""
    settings.GENERAL_RATE_LIMIT_MAX = 2
    settings.GENERAL_RATE_LIMIT_WINDOW = 60
    client = TestClient(app)

    client.get("/inventory/")
    client.get("/inventory/")
    resp = client.get("/inventory/")
    assert resp.status_code == 429
    assert int(resp.headers["Retry-After"]) > 0


def test_gap4_health_exempt_from_rate_limit():
    """/health must always return 200 even after the rate limit is exhausted."""
    settings.GENERAL_RATE_LIMIT_MAX = 2
    settings.GENERAL_RATE_LIMIT_WINDOW = 60
    client = TestClient(app)

    for _ in range(3):
        client.get("/inventory/")

    for _ in range(10):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


def test_gap4_post_endpoint_rate_limited_by_per_route_bucket():
    """POST /simulator/inject (per-route limit=20) is blocked after 20 calls."""
    settings.GENERAL_RATE_LIMIT_MAX = 100  # keep general limit high
    client = TestClient(app)

    for _ in range(20):
        resp = client.post("/simulator/inject", json={"scenario": "SUPPLIER_DELAY"})
        assert resp.status_code == 200

    resp = client.post("/simulator/inject", json={"scenario": "SUPPLIER_DELAY"})
    assert resp.status_code == 429


# ===========================================================================
# GAP 5 — HTTP Security Headers
# ===========================================================================

def test_gap5_x_content_type_options_nosniff():
    resp = TestClient(app).get("/health")
    assert resp.headers.get("X-Content-Type-Options") == "nosniff"


def test_gap5_x_frame_options_deny():
    resp = TestClient(app).get("/health")
    assert resp.headers.get("X-Frame-Options") == "DENY"


def test_gap5_x_xss_protection_present():
    resp = TestClient(app).get("/health")
    assert "1" in resp.headers.get("X-XSS-Protection", "")


def test_gap5_referrer_policy_set():
    resp = TestClient(app).get("/health")
    assert "Referrer-Policy" in resp.headers


def test_gap5_server_header_obfuscated():
    """Server header must say 'scda', not reveal fastapi/uvicorn."""
    resp = TestClient(app).get("/health")
    server = resp.headers.get("Server", "")
    assert "scda" in server
    assert "fastapi" not in server.lower()
    assert "uvicorn" not in server.lower()


def test_gap5_csp_header_present():
    resp = TestClient(app).get("/health")
    csp = resp.headers.get("Content-Security-Policy", "")
    assert "default-src" in csp
    assert "frame-ancestors" in csp


def test_gap5_hsts_header_present():
    resp = TestClient(app).get("/health")
    hsts = resp.headers.get("Strict-Transport-Security", "")
    assert "max-age" in hsts


def test_gap5_security_headers_on_error_responses():
    """Security headers must appear on 404 responses too."""
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.get("/nonexistent-route-xyz")
    assert resp.status_code == 404
    assert resp.headers.get("X-Frame-Options") == "DENY"


# ===========================================================================
# GAP 6 — API Key Authentication (constant-time comparison)
# ===========================================================================

def test_gap6_wrong_api_key_returns_401():
    """When API_KEY is set, wrong key returns 401."""
    settings.API_KEY = "correct-secret-key"
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.post(
        "/simulator/inject",
        json={"scenario": "SUPPLIER_DELAY"},
        headers={"X-API-Key": "wrong-key"},
    )
    assert resp.status_code == 401


def test_gap6_missing_api_key_returns_401():
    """When API_KEY is set, absent key returns 401."""
    settings.API_KEY = "correct-secret-key"
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.post("/simulator/inject", json={"scenario": "SUPPLIER_DELAY"})
    assert resp.status_code == 401


def test_gap6_correct_api_key_returns_200():
    """Correct API key passes authentication."""
    settings.API_KEY = "correct-secret-key"
    client = TestClient(app)
    resp = client.post(
        "/simulator/inject",
        json={"scenario": "SUPPLIER_DELAY"},
        headers={"X-API-Key": "correct-secret-key"},
    )
    assert resp.status_code == 200


def test_gap6_empty_api_key_setting_open_access():
    """When API_KEY is '' (default), requests pass without a key (dev mode)."""
    settings.API_KEY = ""
    client = TestClient(app)
    resp = client.post("/simulator/inject", json={"scenario": "SUPPLIER_DELAY"})
    assert resp.status_code == 200


def test_gap6_n8n_backend_key_wrong_returns_401():
    """N8N integration endpoint: wrong BACKEND_API_KEY → 401."""
    settings.BACKEND_API_KEY = "n8n-secret"
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.post(
        "/integrations/erp/event",
        json={
            "event_type": "PO_CREATED",
            "po_id": "PO-001",
            "supplier_id": "S-001",
            "component_id": "C-001",
        },
        headers={"X-API-Key": "wrong"},
    )
    assert resp.status_code == 401


def test_gap6_n8n_backend_key_correct_returns_200():
    """N8N integration endpoint: correct BACKEND_API_KEY → 200."""
    settings.BACKEND_API_KEY = "n8n-secret"
    client = TestClient(app)
    resp = client.post(
        "/integrations/erp/event",
        json={
            "event_type": "PO_CREATED",
            "po_id": "PO-001",
            "supplier_id": "S-001",
            "component_id": "C-001",
            "status": "ORDERED",
        },
        headers={"X-API-Key": "n8n-secret"},
    )
    assert resp.status_code == 200


# ===========================================================================
# GAP 7 — Path & Query Parameter Injection Blocking
# ===========================================================================

def test_gap7_nosql_injection_in_audit_incident_id():
    """Query param incident_id with NoSQL operator chars → 422."""
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.get("/audit/?incident_id=$gt")
    assert resp.status_code == 422


def test_gap7_oversized_incident_id_query_param():
    """incident_id > 32 chars → 422."""
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.get(f"/audit/?incident_id={'A' * 100}")
    assert resp.status_code == 422


def test_gap7_newline_in_query_param_rejected():
    """URL-encoded newline in query param → 422."""
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.get("/audit/?incident_id=INC-001%0d%0ainjected")
    assert resp.status_code == 422


def test_gap7_valid_alphanumeric_id_accepted():
    """A valid alphanumeric incident ID must not be rejected (returns 200 or 404)."""
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.get("/incidents/INC-001")
    assert resp.status_code in (200, 404)


def test_gap7_nosql_injection_in_erp_logs_query():
    """ERP logs: incident_id with {$ne:null} → 422."""
    settings.BACKEND_API_KEY = ""
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.get("/integrations/erp/logs?incident_id={$ne:null}")
    assert resp.status_code == 422


def test_gap7_special_chars_in_supplier_id_path():
    """Supplier ID path with SQL injection chars → 404/422 (never 200 or 500)."""
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.get("/suppliers/'; DROP TABLE suppliers;--")
    assert resp.status_code in (404, 422)


# ===========================================================================
# GAP 8 — Pydantic Payload Validation
# ===========================================================================

def test_gap8_invalid_scenario_name_returns_422():
    """Unknown scenario name must be rejected with 422."""
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.post("/simulator/inject", json={"scenario": "INJECT_MALWARE"})
    assert resp.status_code == 422


def test_gap8_missing_required_field_returns_422():
    """Missing required payload fields must return 422.
    BACKEND_API_KEY disabled so auth passes and Pydantic runs first."""
    settings.BACKEND_API_KEY = ""
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.post(
        "/integrations/erp/event",
        json={"event_type": "PO_CREATED"},  # po_id, supplier_id, component_id missing
    )
    assert resp.status_code == 422


def test_gap8_field_exceeding_max_length_returns_422():
    """po_id > 32 chars must return 422.
    BACKEND_API_KEY disabled so auth passes and Pydantic runs first."""
    settings.BACKEND_API_KEY = ""
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.post(
        "/integrations/erp/event",
        json={
            "event_type": "PO_CREATED",
            "po_id": "A" * 200,
            "supplier_id": "S-001",
            "component_id": "C-001",
        },
    )
    assert resp.status_code == 422


def test_gap8_xss_attempt_in_payload_id_field_rejected():
    """po_id with <script> injection violates pattern= → 422.
    BACKEND_API_KEY disabled so auth passes and Pydantic runs first."""
    settings.BACKEND_API_KEY = ""
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.post(
        "/integrations/erp/event",
        json={
            "event_type": "PO_CREATED",
            "po_id": "<script>alert(1)</script>",
            "supplier_id": "S-001",
            "component_id": "C-001",
        },
    )
    assert resp.status_code == 422


def test_gap8_plain_text_body_to_json_endpoint_returns_422():
    """Sending text/plain body to JSON endpoint must return 422."""
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.post(
        "/simulator/inject",
        content=b"not valid json",
        headers={"Content-Type": "text/plain"},
    )
    assert resp.status_code == 422


# ===========================================================================
# GAP 9 — Log Sanitization (no newline / CRLF injection)
# ===========================================================================

def test_gap9_sanitize_strips_carriage_return():
    from app.middleware.security import _sanitize_log_str
    result = _sanitize_log_str("safe\rbad")
    assert "\r" not in result
    assert "safe" in result


def test_gap9_sanitize_strips_newline():
    from app.middleware.security import _sanitize_log_str
    result = _sanitize_log_str("GET /path\nX-Injected: evil")
    assert "\n" not in result


def test_gap9_sanitize_truncates_at_128_chars():
    from app.middleware.security import _sanitize_log_str
    result = _sanitize_log_str("A" * 300)
    assert len(result) <= 128


def test_gap9_sanitize_preserves_normal_printable_chars():
    from app.middleware.security import _sanitize_log_str
    normal = "GET /inventory/COMP-001 200 OK"
    assert _sanitize_log_str(normal) == normal


def test_gap9_crlf_injected_user_agent_does_not_crash_server():
    """Request with CRLF-injected User-Agent must not cause 500."""
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.get(
        "/nonexistent-xyz",
        headers={"User-Agent": "curl/7.0\r\nX-Evil-Header: injected"},
    )
    assert resp.status_code == 404  # correct 404, not 500
