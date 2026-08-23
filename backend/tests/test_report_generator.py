"""
backend/tests/test_report_generator.py
Unit and integration tests for LLM Operations Report & PDF Generation.
"""

from datetime import datetime, timezone
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import mongomock

from app.main import app
from app.config import settings
from app.mongo_database import get_mongo_db
from app.services.report_generator import (
    fetch_report_context,
    generate_report_narrative,
    build_operations_pdf,
    generate_report_bundle,
    sanitize_text,
)


@pytest.fixture
def mock_db():
    client = mongomock.MongoClient()
    db = client["test_db"]
    now = datetime.now(timezone.utc).isoformat()

    # Seed mock data
    db["incidents"].insert_one({
        "incident_id": "INC-101",
        "type": "SUPPLIER_DELAY",
        "severity": "HIGH",
        "status": "INVESTIGATING",
        "affected_component": "COMP-ALPHA",
        "affected_po": "PO-9001",
        "delay_days": 4,
        "created_at": now,
    })

    db["inventory"].insert_one({
        "component_id": "COMP-ALPHA",
        "current_stock": 200,
        "usable_stock": 150,
        "daily_usage": 30,
        "safety_stock": 100,
        "location": "Warehouse-1",
    })

    db["purchase_orders"].insert_one({
        "po_id": "PO-9001",
        "supplier_id": "SUP-77",
        "component_id": "COMP-ALPHA",
        "status": "DELAYED",
        "quantity": 500,
        "total_value": 25000.0,
    })

    db["suppliers"].insert_one({
        "supplier_id": "SUP-77",
        "name": "Global Silicon Ltd",
        "reliability_score": 0.88,
        "lead_time_days": 5,
        "min_order_qty": 100,
    })

    db["production_orders"].insert_one({
        "production_id": "PROD-501",
        "product": "Industrial Controller X",
        "component_id": "COMP-ALPHA",
        "status": "SCHEDULED",
        "priority": "HIGH",
    })

    db["recovery_plans"].insert_one({
        "incident_id": "INC-101",
        "recommended_option_id": "OPT-1",
        "recommendation_reason": "Expedited air freight with primary supplier",
        "requires_human_approval": False,
        "approval_threshold_usd": 50000.0,
        "options": [
            {
                "option_id": "OPT-1",
                "action": "Expedited air freight",
                "supplier_name": "Global Silicon Ltd",
                "total_cost": 4500.0,
                "lead_time_days": 2,
            },
            {
                "option_id": "OPT-2",
                "action": "Secondary local supplier",
                "supplier_name": "Apex Electronics",
                "total_cost": 8200.0,
                "lead_time_days": 4,
            },
        ],
    })

    db["audit_logs"].insert_one({
        "timestamp": now,
        "incident_id": "INC-101",
        "action": "Agent evaluated recovery alternatives",
        "decision": "OPTION_RECOMMENDED",
        "reason": "Option 1 provides fastest lead time under autonomous budget",
    })

    return db


@pytest.fixture
def client(mock_db):
    app.dependency_overrides[get_mongo_db] = lambda: mock_db
    settings.API_KEY = ""
    settings.BACKEND_API_KEY = ""
    settings.GENERAL_RATE_LIMIT_MAX = 1000

    # Create a test admin user and generate a JWT token for authentication
    from app.core.auth_security import create_access_token

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


def test_sanitize_text():
    raw = "Quote ‘smart’ and “double” — dash, bullet •, arrow →, check ✓, euro €"
    clean = sanitize_text(raw)
    assert "smart" in clean
    assert "double" in clean
    assert "EUR" in clean
    # Must be encodable to latin-1 without exception
    clean.encode("latin-1")


def test_fetch_report_context(mock_db):
    ctx = fetch_report_context(mock_db, incident_id="INC-101")
    assert ctx["summary_stats"]["scope"] == "INC-101"
    assert ctx["summary_stats"]["incident_count"] == 1
    assert ctx["summary_stats"]["min_days_of_supply"] == 5.0  # 150 / 30
    assert len(ctx["inventory"]) == 1
    assert len(ctx["purchase_orders"]) == 1
    assert len(ctx["recovery_plans"]) == 1
    assert ctx["summary_stats"]["requires_human_approval"] is False


def test_generate_report_narrative_deterministic(mock_db):
    ctx = fetch_report_context(mock_db, incident_id="INC-101")
    narrative = generate_report_narrative(ctx)
    assert "executive_summary" in narrative
    assert "impact_assessment" in narrative
    assert "recovery_strategy" in narrative
    assert "action_items" in narrative
    assert len(narrative["action_items"]) >= 3
    assert "INC-101" in narrative["executive_summary"] or "COMP-ALPHA" in narrative["executive_summary"]


def test_build_operations_pdf(mock_db):
    ctx = fetch_report_context(mock_db, incident_id="INC-101")
    narrative = generate_report_narrative(ctx)
    pdf_bytes = build_operations_pdf(ctx, narrative)
    
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 500
    assert pdf_bytes.startswith(b"%PDF")


def test_operator_report_preview_endpoint(client):
    resp = client.get("/audit/report/preview?incident_id=INC-101")
    assert resp.status_code == 200
    data = resp.json()
    assert "summary_stats" in data
    assert "narrative" in data
    assert data["summary_stats"]["scope"] == "INC-101"
    assert "executive_summary" in data["narrative"]


def test_operator_report_pdf_endpoint(client):
    resp = client.get("/audit/report/operator.pdf?incident_id=INC-101")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert resp.content.startswith(b"%PDF")
    assert "attachment" in resp.headers.get("content-disposition", "")


def test_operator_report_pdf_not_found(client):
    resp = client.get("/audit/report/operator.pdf?incident_id=NON_EXISTENT_INCIDENT")
    assert resp.status_code == 404


def test_operator_report_date_filtering(client, mock_db):
    resp = client.get("/audit/report/preview?start_date=2026-01-01&end_date=2026-12-31")
    assert resp.status_code == 200
    data = resp.json()
    assert data["summary_stats"]["incident_count"] >= 1


def test_individual_incident_report_narrative(client):
    resp = client.get("/incidents/INC-101/report")
    assert resp.status_code == 200
    data = resp.json()
    assert data["incident_id"] == "INC-101"
    assert "narrative" in data
    assert "executive_summary" in data["narrative"]
    assert "impact_assessment" in data["narrative"]
    assert "action_items" in data["narrative"]


def test_individual_incident_report_pdf(client):
    resp = client.get("/incidents/INC-101/report/pdf")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert resp.content.startswith(b"%PDF")
    assert "incident-report-INC-101" in resp.headers.get("content-disposition", "")


def test_individual_incident_report_not_found(client):
    resp = client.get("/incidents/INC-UNKNOWN/report")
    assert resp.status_code == 404
    resp_pdf = client.get("/incidents/INC-UNKNOWN/report/pdf")
    assert resp_pdf.status_code == 404

