"""
backend/tests/test_security_hardening.py
Tests for the 4 security gap fixes:
1. Spoofed X-Forwarded-For cannot bypass rate limiting without trusted proxy.
2. Rate-limit store does not grow unbounded after keys go idle.
3. Chunked encoding / unstated body > 64 KB is rejected with 413.
4. General rate limiting covers GET endpoints, exempting /health.
"""

import time
from collections import deque
import pytest
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


import mongomock
from app.mongo_database import get_mongo_db


@pytest.fixture(autouse=True)
def clean_rate_limit_and_mock_db():
    """Clear in-memory rate limit store and mock MongoDB for test isolation."""
    mock_db = mongomock.MongoClient()["test_scda"]
    app.dependency_overrides[get_mongo_db] = lambda: mock_db
    with _lock:
        _store.clear()
    yield
    with _lock:
        _store.clear()
    app.dependency_overrides.pop(get_mongo_db, None)


def test_gap1_spoofed_x_forwarded_for_not_trusted_by_default():
    """
    Gap 1: When TRUSTED_PROXY_IPS is empty, X-Forwarded-For is ignored.
    Sending spoofed X-Forwarded-For headers from the same client does NOT reset the bucket.
    """
    settings.TRUSTED_PROXY_IPS = ""
    client = TestClient(app)

    # Simulator inject has limit of 20 req/min
    # Send 20 requests with different fake X-Forwarded-For headers
    for i in range(20):
        resp = client.post(
            "/simulator/inject",
            json={"scenario": "SUPPLIER_DELAY"},
            headers={"X-Forwarded-For": f"192.168.1.{i}"},
        )
        assert resp.status_code == 200, f"Request {i} failed: {resp.text}"

    # 21st request from same client with yet another fake IP must be rejected with 429
    resp = client.post(
        "/simulator/inject",
        json={"scenario": "SUPPLIER_DELAY"},
        headers={"X-Forwarded-For": "10.99.99.99"},
    )
    assert resp.status_code == 429
    assert "Rate limit exceeded" in resp.json()["detail"]


def test_gap1_trusted_proxy_honors_forwarded_for():
    """
    Gap 1: When direct client IP is in TRUSTED_PROXY_IPS, X-Forwarded-For is trusted.
    """
    settings.TRUSTED_PROXY_IPS = "testclient"
    client = TestClient(app)

    # Requests from different forward IPs count in separate buckets
    resp1 = client.post(
        "/simulator/inject",
        json={"scenario": "SUPPLIER_DELAY"},
        headers={"X-Forwarded-For": "203.0.113.1"},
    )
    resp2 = client.post(
        "/simulator/inject",
        json={"scenario": "SUPPLIER_DELAY"},
        headers={"X-Forwarded-For": "203.0.113.2"},
    )
    assert resp1.status_code == 200
    assert resp2.status_code == 200

    # Reset config
    settings.TRUSTED_PROXY_IPS = ""


def test_gap2_rate_limit_store_evicts_idle_keys():
    """
    Gap 2: Expired and idle (ip, bucket) keys are purged from _store to prevent memory leaks.
    """
    now = time.monotonic()
    past_timestamp = now - 120.0  # 2 minutes ago

    # Simulate 500 distinct IPs that visited in the past and went idle
    with _lock:
        for i in range(500):
            _store[(f"10.0.0.{i}", "general")].append(past_timestamp)

        assert len(_store) == 500

    # Run purge
    purged = purge_empty_and_idle_keys(window_seconds=60)
    assert purged == 500

    with _lock:
        assert len(_store) == 0

    # Verify new request for returning IP works normally
    allowed, _ = record_and_check_rate_limit("10.0.0.1", "general", max_calls=60, window_seconds=60)
    assert allowed is True
    with _lock:
        assert len(_store) == 1


def test_gap3_chunked_oversized_body_rejected_with_413():
    """
    Gap 3: A chunked or unstated request body > 64 KB is rejected with 413 by stream counting.
    """
    client = TestClient(app)

    # 70 KB payload (exceeds 64 KB limit)
    large_chunk = b"A" * 1024  # 1 KB chunk

    def chunk_generator():
        for _ in range(70):
            yield large_chunk

    # Send chunked streaming request (TestClient / requests uses chunked encoding when content is generator)
    resp = client.post(
        "/simulator/inject",
        content=chunk_generator(),
        headers={"Content-Type": "application/json"},
    )

    assert resp.status_code == 413
    assert "Request body too large" in resp.json()["detail"]


def test_gap4_general_rate_limit_covers_get_endpoints():
    """
    Gap 4: GET /inventory/ is rate-limited after GENERAL_RATE_LIMIT_MAX requests.
    """
    settings.GENERAL_RATE_LIMIT_MAX = 5
    settings.GENERAL_RATE_LIMIT_WINDOW = 60
    client = TestClient(app)

    # 5 requests should pass
    for _ in range(5):
        resp = client.get("/inventory/")
        assert resp.status_code == 200

    # 6th request must return 429
    resp = client.get("/inventory/")
    assert resp.status_code == 429
    assert "Rate limit exceeded" in resp.json()["detail"]
    assert "Retry-After" in resp.headers

    # Reset config
    settings.GENERAL_RATE_LIMIT_MAX = 60
    settings.GENERAL_RATE_LIMIT_WINDOW = 60


def test_gap4_health_endpoint_is_exempt_from_rate_limit():
    """
    Gap 4: GET /health is exempt from rate limits so health checks never fail.
    """
    settings.GENERAL_RATE_LIMIT_MAX = 2
    settings.GENERAL_RATE_LIMIT_WINDOW = 60
    client = TestClient(app)

    # Exceed limit on /inventory/
    for _ in range(3):
        client.get("/inventory/")

    # /health should still return 200 ok
    for _ in range(10):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    # Reset config
    settings.GENERAL_RATE_LIMIT_MAX = 60
    settings.GENERAL_RATE_LIMIT_WINDOW = 60
