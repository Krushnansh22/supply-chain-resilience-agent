"""
backend/tests/test_agent_controller.py
Tests the Autonomous Agent Service, Environment Scanner, Negative Stock Human Approval,
1-Click Disruption Injections, and Step-by-Step Resolution.
"""

import pytest
import mongomock
from datetime import datetime, timezone

from app.agent.agent_service import AgentService
from app.simulator.disruption_injector import inject_scenario, SCENARIO_DEFAULTS


@pytest.fixture
def mock_db():
    client = mongomock.MongoClient()
    db = client["scda_test_db"]

    # Seed basic inventory
    db["inventory"].insert_many([
        {"component_id": "COMP-104", "name": "Microcontroller MCU-8", "usable_stock": 390, "current_stock": 390, "safety_stock": 100, "daily_usage": 90.0},
        {"component_id": "COMP-102", "name": "Power Inductor 10uH", "usable_stock": 500, "current_stock": 500, "safety_stock": 80, "daily_usage": 40.0},
    ])

    # Seed suppliers
    db["suppliers"].insert_many([
        {"supplier_id": "SUP-18", "name": "Apex Global Express", "status": "ACTIVE", "quality_score": 95.0, "reliability_score": 92.0, "certifications": "ISO9001,RoHS"},
        {"supplier_id": "SUP-42", "name": "Standard Freight Co", "status": "ACTIVE", "quality_score": 85.0, "reliability_score": 80.0, "certifications": "RoHS"},
    ])

    return db


def test_agent_start_and_stop(mock_db):
    service = AgentService()
    assert service.status == "STOPPED"

    status = service.start_agent(mock_db)
    assert status["is_running"] is True
    assert service.status == "RUNNING"

    stopped = service.stop_agent()
    assert stopped["status"] == "STOPPED"
    assert service.status == "STOPPED"


def test_1click_negative_stock_injection_and_human_approval_flow(mock_db):
    service = AgentService()

    # 1. 1-Click Inject Negative Stock Disruption
    inc = inject_scenario("NEGATIVE_STOCK", mock_db)
    assert inc["type"] == "NEGATIVE_STOCK"
    assert inc["severity"] == "CRITICAL"

    # Verify inventory is actually negative in DB
    inv = mock_db["inventory"].find_one({"component_id": "COMP-104"})
    assert inv["usable_stock"] == -150

    # 2. Start agent and run scan
    service.start_agent(mock_db)
    assert inc["incident_id"] in service.queue

    # 3. Step 1: DETECTED -> INVESTIGATING
    res1 = service.process_one_step(mock_db)
    assert res1["step"] == "INVESTIGATING"
    inc_db = mock_db["incidents"].find_one({"incident_id": inc["incident_id"]})
    assert inc_db["status"] == "INVESTIGATING"

    # 4. Step 2: INVESTIGATING -> WAITING_APPROVAL (Mandatory Human Input)
    res2 = service.process_one_step(mock_db)
    assert res2["step"] == "WAITING_APPROVAL"
    inc_db = mock_db["incidents"].find_one({"incident_id": inc["incident_id"]})
    assert inc_db["status"] == "WAITING_APPROVAL"

    # Check recovery plan contains data anomaly info and requires approval
    plan = mock_db["recovery_plans"].find_one({"incident_id": inc["incident_id"]})
    assert plan["requires_human_approval"] is True
    assert plan["issue_type"] == "NEGATIVE_STOCK"
    assert plan["recorded_stock"] == -150

    # 5. Step 3: Agent pauses on WAITING_APPROVAL
    res3 = service.process_one_step(mock_db)
    assert res3["waiting_for_user"] is True

    # 6. Human Operator inputs verified physical count (450 units)
    corr = service.resolve_stock_correction(
        incident_id=inc["incident_id"],
        component_id="COMP-104",
        corrected_stock=450,
        reason="Physical warehouse count verified by operator",
        approver="Alex Whitfield",
        db=mock_db,
    )
    assert corr["status"] == "RESOLVED"
    assert corr["corrected_stock"] == 450

    # Check DB was updated with corrected physical count
    updated_inv = mock_db["inventory"].find_one({"component_id": "COMP-104"})
    assert updated_inv["usable_stock"] == 450
    assert updated_inv["current_stock"] == 450

    # Check audit log was written
    audit = mock_db["audit_logs"].find_one({"incident_id": inc["incident_id"], "decision": "STOCK_CORRECTED"})
    assert audit is not None
    assert "Alex Whitfield" in audit["action"]


def test_autonomous_supplier_delay_resolution(mock_db):
    service = AgentService()

    # 1. Inject supplier delay
    inc = inject_scenario("SUPPLIER_DELAY", mock_db)
    assert inc["type"] == "SUPPLIER_DELAY"

    # 2. Start agent
    service.start_agent(mock_db)

    # 3. Step 1: DETECTED -> INVESTIGATING
    res1 = service.process_one_step(mock_db)
    assert res1["step"] == "INVESTIGATING"

    # 4. Step 2: INVESTIGATING -> EVALUATING
    res2 = service.process_one_step(mock_db)
    assert res2["step"] == "EVALUATING"

    # 5. Step 3: EVALUATING -> EXECUTING (under $50k threshold)
    res3 = service.process_one_step(mock_db)
    assert res3["step"] == "EXECUTING"

    # 6. Step 4: EXECUTING -> RESOLVED (Creates PO & updates ERP)
    res4 = service.process_one_step(mock_db)
    assert res4["step"] == "RESOLVED"
    assert res4["solved"] is True

    inc_db = mock_db["incidents"].find_one({"incident_id": inc["incident_id"]})
    assert inc_db["status"] == "RESOLVED"


def test_budget_overrun_requires_human_approval(mock_db):
    service = AgentService()

    # 1. Inject budget overrun
    inc = inject_scenario("BUDGET_OVERRUN", mock_db)
    assert inc["type"] == "BUDGET_OVERRUN"

    # 2. Start agent
    service.start_agent(mock_db)

    # DETECTED -> INVESTIGATING -> EVALUATING -> WAITING_APPROVAL
    service.process_one_step(mock_db)
    service.process_one_step(mock_db)
    res = service.process_one_step(mock_db)

    assert res["step"] == "WAITING_APPROVAL"
    plan = mock_db["recovery_plans"].find_one({"incident_id": inc["incident_id"]})
    assert plan["requires_human_approval"] is True
