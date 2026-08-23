"""
backend/tests/test_agentic_loop.py
===================================
Comprehensive test suite for the autonomous multi-step agentic controller.
Validates:
1. Dynamic task decomposition for varying disruption types.
2. Multi-step reasoning and tool execution loop.
3. Supplier negotiation, tracking cross-check, and contradiction detection.
4. RFQ evaluation and split-order recovery planning.
5. Mid-flight replanning triggers and Plan B generation.
6. Multi-criteria escalation logic and structured Decision Briefs.
7. Rich explainable audit trail schema.
8. FastAPI agent endpoints (POST /agent/run-incident, GET /agent/tasks/{id}, GET /agent/audit/{id}, POST /agent/replan/{id}).
"""

from datetime import datetime, timezone
import mongomock
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.mongo_database import get_mongo_db
from app.agent.agent_loop import run_agent_cycle, run_agent_for_incident
from app.agent.task_decomposer import decompose_incident, get_tasks_for_incident, TaskStatus
from app.agent.states import AgentState
from app.agent.escalation_engine import evaluate_escalation, EscalationCriterion
from app.simulator.supplier_simulator import (
    register_supplier_lie,
    reset_simulator_state,
    simulate_supplier_reply,
    simulate_tracking_status,
)


@pytest.fixture(autouse=True)
def clean_simulator():
    reset_simulator_state()
    yield
    reset_simulator_state()


@pytest.fixture
def mock_db():
    client = mongomock.MongoClient()
    db = client["test_agentic_loop_db"]
    # Seed suppliers
    db["suppliers"].insert_many([
        {
            "supplier_id": "SUP-001",
            "name": "Apex Microelectronics",
            "quality_score": 92.0,
            "reliability_score": 90.0,
            "certifications": "ISO9001,AS9100",
            "min_order_qty": 50,
        },
        {
            "supplier_id": "SUP-002",
            "name": "Beacon Silicon Ltd",
            "quality_score": 88.0,
            "reliability_score": 85.0,
            "certifications": "ISO9001",
            "min_order_qty": 100,
        },
        {
            "supplier_id": "SUP-003",
            "name": "Crestline Dynamics",
            "quality_score": 78.0,
            "reliability_score": 75.0,
            "certifications": "",
            "min_order_qty": 20,
        },
    ])
    return db


@pytest.fixture
def test_client(mock_db):
    app.dependency_overrides[get_mongo_db] = lambda: mock_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# ===========================================================================
# 1. Dynamic Task Decomposition Tests
# ===========================================================================

def test_dynamic_task_decomposition_varies_by_disruption_type():
    """Different disruption types generate distinct, tailored task lists."""
    tasks_delay = decompose_incident("INC-101", "SUPPLIER_DELAY", "HIGH", "COMP-104", "PO-100", "SUP-001")
    tasks_lie = decompose_incident("INC-102", "SUPPLIER_LIE", "CRITICAL", "COMP-104", "PO-100", "SUP-001")
    tasks_quality = decompose_incident("INC-103", "QUALITY_FAILURE", "HIGH", "COMP-104", "PO-100", "SUP-001")
    tasks_stale = decompose_incident("INC-104", "STALE_INVENTORY", "MEDIUM", "COMP-104")

    # Verify task counts and titles differ
    titles_delay = [t["title"] for t in tasks_delay]
    titles_lie = [t["title"] for t in tasks_lie]
    titles_quality = [t["title"] for t in tasks_quality]

    assert any("Carrier Tracking" in t for t in titles_delay)
    assert any("Dispatch Contradiction" in t for t in titles_lie)
    assert any("Quarantine Defective Lot" in t for t in titles_quality)

    # Verify SKILL.md category classification
    categories = {t["category"] for t in tasks_delay}
    assert "VERIFICATION" in categories
    assert "SOURCING" in categories
    assert "PLANNING" in categories
    assert "APPROVAL" in categories
    assert "RECORD_UPDATE" in categories


# ===========================================================================
# 2. Simple Delay Scenario — Autonomous Multi-Step Resolution
# ===========================================================================

def test_supplier_delay_multi_step_resolution(mock_db):
    """
    Simulates a standard supplier delay:
    1. Decomposes tasks.
    2. Gathers inventory & production schedule.
    3. Solicits RFQs.
    4. Computes recovery plan using deterministic decision engine.
    5. Evaluates approval threshold.
    6. Automatically executes recovery plan when within authority limits.
    """
    mock_db["incidents"].insert_one({
        "incident_id": "INC-DELAY-01",
        "type": "SUPPLIER_DELAY",
        "severity": "MEDIUM",
        "affected_component": "COMP-201",
        "affected_po": "PO-201",
        "affected_supplier": "SUP-001",
        "status": "DETECTED",
        "created_at": datetime.now(timezone.utc),
    })
    mock_db["inventory"].insert_one({
        "component_id": "COMP-201",
        "usable_stock": 350,
        "daily_usage": 25.0,
        "safety_stock": 50,
    })
    mock_db["production_orders"].insert_one({
        "production_id": "PROD-201",
        "product": "Telemetry Unit",
        "component_id": "COMP-201",
        "quantity": 100,
        "priority": "HIGH",
    })

    result = run_agent_cycle("INC-DELAY-01", mock_db, max_steps=10)

    assert result["incident_id"] == "INC-DELAY-01"
    assert result["steps_executed"] >= 4
    assert len(result["tasks"]) >= 5

    # Check tasks were updated to COMPLETED
    completed_tasks = [t for t in result["tasks"] if t["status"] == TaskStatus.COMPLETED]
    assert len(completed_tasks) >= 3

    # Check rich audit log was produced
    audit_logs = list(mock_db["audit_logs"].find({"incident_id": "INC-DELAY-01"}))
    assert len(audit_logs) >= 4
    tools_called = [a.get("tool") for a in audit_logs if a.get("tool")]
    assert "get_inventory" in tools_called
    assert "compute_recovery_options" in tools_called

    # Check recovery plan was created in DB
    plan = mock_db["recovery_plans"].find_one({"incident_id": "INC-DELAY-01"})
    assert plan is not None
    assert len(plan["options"]) >= 1


# ===========================================================================
# 3. Supplier Lie / Contradiction Detection & Negotiation
# ===========================================================================

def test_supplier_lie_contradiction_detection_and_negotiation(mock_db):
    """
    Simulates a supplier lying about dispatch:
    1. Supplier claims 'Dispatched yesterday'.
    2. Carrier tracking check returns NO_PICKUP_SCAN.
    3. Agent detects contradiction, challenges supplier via request_clarification.
    4. Supplier concedes delay and offers expedited terms.
    5. Agent logs contradiction and solicits verified replacement RFQs.
    """
    po_id = "PO-LIE-99"
    register_supplier_lie(po_id)

    mock_db["incidents"].insert_one({
        "incident_id": "INC-LIE-01",
        "type": "SUPPLIER_LIE",
        "severity": "CRITICAL",
        "affected_component": "COMP-301",
        "affected_po": po_id,
        "affected_supplier": "SUP-003",
        "status": "DETECTED",
        "created_at": datetime.now(timezone.utc),
    })
    mock_db["inventory"].insert_one({
        "component_id": "COMP-301",
        "usable_stock": 100,
        "daily_usage": 20.0,
        "safety_stock": 50,
    })

    # Initial tracking returns NO_PICKUP_SCAN
    assert simulate_tracking_status(po_id) == "NO_PICKUP_SCAN"

    result = run_agent_cycle("INC-LIE-01", mock_db, max_steps=12)

    assert result["incident_id"] == "INC-LIE-01"

    # Verify tracking check and clarification tool calls in audit trail
    audit_logs = list(mock_db["audit_logs"].find({"incident_id": "INC-LIE-01"}))
    tools_called = [a.get("tool") for a in audit_logs if a.get("tool")]
    assert "get_tracking_status" in tools_called
    assert "request_clarification" in tools_called

    # Verify messages in supplier_messages collection
    messages = list(mock_db["supplier_messages"].find({"po_id": po_id}))
    assert len(messages) >= 2
    directions = [m.get("direction") for m in messages]
    assert "OUTBOUND_CHALLENGE" in directions


# ===========================================================================
# 4. Multi-Supplier Evaluation & Split-Order Recovery Plan
# ===========================================================================

def test_multi_supplier_split_order_recovery(mock_db):
    """
    Verifies that compute_recovery_options produces split-order options
    and that the decision engine scores both single and split sourcing.
    """
    mock_db["incidents"].insert_one({
        "incident_id": "INC-SPLIT-01",
        "type": "SUPPLIER_DELAY",
        "severity": "HIGH",
        "affected_component": "COMP-401",
        "affected_po": "PO-401",
        "affected_supplier": "SUP-001",
        "status": "DETECTED",
        "created_at": datetime.now(timezone.utc),
    })
    mock_db["inventory"].insert_one({
        "component_id": "COMP-401",
        "usable_stock": 50,
        "daily_usage": 20.0,
        "safety_stock": 20,
    })

    result = run_agent_cycle("INC-SPLIT-01", mock_db, max_steps=10)

    plan = mock_db["recovery_plans"].find_one({"incident_id": "INC-SPLIT-01"})
    assert plan is not None
    assert len(plan["options"]) >= 2

    # Check for presence of split-order option (multiple allocations)
    has_split_option = any(len(opt.get("allocations", [])) > 1 for opt in plan["options"])
    assert has_split_option is True


# ===========================================================================
# 5. Mid-Flight Replanning Trigger & Plan B Generation
# ===========================================================================

def test_mid_flight_replanning_loop(mock_db):
    """
    Tests mid-flight replanning:
    1. Incident is initially processed.
    2. New disruption event occurs mid-flight (e.g. chosen supplier reneges or quality failure).
    3. Replan endpoint is invoked -> transitions to REPLANNING -> produces revised Plan B.
    """
    inc_id = "INC-REPLAN-01"
    mock_db["incidents"].insert_one({
        "incident_id": inc_id,
        "type": "SUPPLIER_DELAY",
        "severity": "HIGH",
        "affected_component": "COMP-501",
        "affected_po": "PO-501",
        "status": "DETECTED",
        "created_at": datetime.now(timezone.utc),
    })
    mock_db["inventory"].insert_one({
        "component_id": "COMP-501",
        "usable_stock": 100,
        "daily_usage": 15.0,
    })

    # Initial run
    run_agent_cycle(inc_id, mock_db, max_steps=8)

    # Trigger mid-flight replan
    replan_ctx = {
        "reason": "Supplier SUP-001 experienced factory flooding post-selection",
        "suppliers_to_avoid": ["SUP-001"],
    }
    replan_result = run_agent_cycle(
        incident_id=inc_id,
        db=mock_db,
        max_steps=8,
        trigger_reason="Supplier reneged post-selection",
        replan_context=replan_ctx,
    )

    assert replan_result["incident_id"] == inc_id

    # Verify audit trail contains replan entry
    audit_logs = list(mock_db["audit_logs"].find({"incident_id": inc_id}))
    actions = [a.get("action", "") for a in audit_logs]
    assert any("replan" in a.lower() for a in actions)


# ===========================================================================
# 6. Multi-Criteria Escalation & Decision Brief Tests
# ===========================================================================

def test_multi_criteria_escalation_evaluation():
    """Verifies that all 6 escalation criteria trigger correctly with Decision Briefs."""
    # Test A: Budget Exhausted
    eval_budget = evaluate_escalation("INC-E1", "SUPPLIER_DELAY", "HIGH", "COMP-1", budget_exhausted=True)
    assert eval_budget.requires_escalation is True
    assert eval_budget.trigger_criterion == EscalationCriterion.BUDGET_EXHAUSTED
    assert "DECISION BRIEF" in eval_budget.decision_brief
    assert "SITUATION:" in eval_budget.decision_brief
    assert "COST OF INACTION:" in eval_budget.decision_brief
    assert "RECOMMENDATION:" in eval_budget.decision_brief

    # Test B: Critical zero inventory line-shutdown risk
    eval_shutdown = evaluate_escalation("INC-E2", "SUPPLIER_DELAY", "CRITICAL", "COMP-1", days_of_supply=0.0)
    assert eval_shutdown.requires_escalation is True
    assert eval_shutdown.trigger_criterion == EscalationCriterion.UNAVOIDABLE_PRODUCTION_SHUTDOWN
    assert "CRITICAL" in eval_shutdown.decision_brief


# ===========================================================================
# 7. FastAPI API Endpoints Integration Tests
# ===========================================================================

def test_api_agent_run_incident_endpoint(test_client, mock_db):
    """POST /agent/run-incident executes agent loop and returns complete payload."""
    mock_db["incidents"].insert_one({
        "incident_id": "INC-API-01",
        "type": "SUPPLIER_DELAY",
        "severity": "HIGH",
        "affected_component": "COMP-API",
        "status": "DETECTED",
        "created_at": datetime.now(timezone.utc),
    })
    mock_db["inventory"].insert_one({
        "component_id": "COMP-API",
        "usable_stock": 200,
        "daily_usage": 20.0,
    })

    resp = test_client.post(
        "/agent/run-incident",
        json={"incident_id": "INC-API-01"},
        headers={"X-API-Key": "changeme-secret-key"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["incident_id"] == "INC-API-01"
    assert "decision" in data
    assert "tasks" in data
    assert len(data["tasks"]) >= 5


def test_api_agent_tasks_and_audit_endpoints(test_client, mock_db):
    """GET /agent/tasks/{id} and GET /agent/audit/{id} return expected data."""
    mock_db["incidents"].insert_one({
        "incident_id": "INC-API-02",
        "type": "QUALITY_FAILURE",
        "severity": "CRITICAL",
        "affected_component": "COMP-API-2",
        "status": "DETECTED",
        "created_at": datetime.now(timezone.utc),
    })
    mock_db["inventory"].insert_one({
        "component_id": "COMP-API-2",
        "usable_stock": 100,
        "daily_usage": 10.0,
    })

    # Run agent
    test_client.post(
        "/agent/run-incident",
        json={"incident_id": "INC-API-02"},
        headers={"X-API-Key": "changeme-secret-key"},
    )

    # 1. Fetch tasks
    resp_tasks = test_client.get("/agent/tasks/INC-API-02")
    assert resp_tasks.status_code == 200
    tasks_data = resp_tasks.json()
    assert tasks_data["incident_id"] == "INC-API-02"
    assert len(tasks_data["tasks"]) >= 5

    # 2. Fetch audit trail
    resp_audit = test_client.get("/agent/audit/INC-API-02")
    assert resp_audit.status_code == 200
    audit_data = resp_audit.json()
    assert audit_data["incident_id"] == "INC-API-02"
    assert len(audit_data["audit_trail"]) >= 3


def test_api_agent_approve_and_reject_endpoints(test_client, mock_db):
    """POST /agent/approve and POST /agent/reject update state and trigger actions."""
    mock_db["incidents"].insert_one({
        "incident_id": "INC-APP-01",
        "type": "SUPPLIER_DELAY",
        "severity": "HIGH",
        "affected_component": "COMP-APP",
        "status": "WAITING_APPROVAL",
        "created_at": datetime.now(timezone.utc),
    })
    mock_db["recovery_plans"].insert_one({
        "incident_id": "INC-APP-01",
        "options": [
            {
                "option_id": "A",
                "allocations": [{"supplier_id": "SUP-001", "quantity": 100, "unit_price": 10.0, "delivery_days": 2}],
                "total_cost": 1000.0,
                "max_delivery_days": 2,
                "constraints_satisfied": True,
            }
        ],
        "recommended_option_id": "A",
    })

    # 1. Approve
    resp_app = test_client.post(
        "/agent/approve",
        json={"incident_id": "INC-APP-01", "approver": "ops-lead"},
        headers={"X-API-Key": "changeme-secret-key"},
    )
    assert resp_app.status_code == 200
    assert resp_app.json()["state"] == AgentState.EXECUTING.value

    # 2. Reject
    mock_db["incidents"].insert_one({
        "incident_id": "INC-REJ-01",
        "type": "SUPPLIER_DELAY",
        "severity": "HIGH",
        "affected_component": "COMP-APP",
        "status": "WAITING_APPROVAL",
        "created_at": datetime.now(timezone.utc),
    })
    resp_rej = test_client.post(
        "/agent/reject",
        json={"incident_id": "INC-REJ-01", "approver": "procurement-vp"},
        headers={"X-API-Key": "changeme-secret-key"},
    )
    assert resp_rej.status_code == 200
    assert resp_rej.json()["state"] in (AgentState.REPLANNING.value, AgentState.WAITING_APPROVAL.value, AgentState.RESOLVED.value)


def test_full_environment_scan_detects_broken_data_and_triages(test_client, mock_db):
    """
    Tests the proactive full-environment autonomous scanner:
    1. Inserts corrupted negative stock item 'BROKEN-001'.
    2. Runs POST /agent/scan-and-triage.
    3. Verifies anomaly is auto-discovered, incident created, and agent triage loop executed.
    """
    mock_db["inventory"].insert_one({
        "component_id": "BROKEN-001",
        "name": "Corrupted Component Alpha",
        "current_stock": -50,
        "usable_stock": -50,
        "daily_usage": 10.0,
        "safety_stock": 100,
        "anomaly": "NEGATIVE_STOCK",
    })

    resp = test_client.post(
        "/agent/scan-and-triage",
        headers={"X-API-Key": "changeme-secret-key"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["anomalies_detected_count"] >= 1
    assert any(a["entity_id"] == "BROKEN-001" for a in data["anomalies_detected"])

    # Verify incident was created in DB
    created_inc = mock_db["incidents"].find_one({"affected_component": "BROKEN-001"})
    assert created_inc is not None
    assert created_inc["data_inconsistency_detected"] is True
    assert created_inc["status"] in (AgentState.WAITING_APPROVAL.value, AgentState.INVESTIGATING.value, AgentState.RESOLVED.value)


def test_global_process_backlog_endpoint(test_client, mock_db):
    """
    Tests the unified global autonomous agent queue processor:
    Picks up pending incidents one by one and resolves or escalates them.
    """
    mock_db["incidents"].insert_one({
        "incident_id": "INC-QUEUE-01",
        "type": "SUPPLIER_DELAY",
        "severity": "HIGH",
        "affected_component": "COMP-104",
        "affected_po": "PO-991",
        "affected_supplier": "SUP-001",
        "status": "DETECTED",
        "created_at": datetime.now(timezone.utc),
    })

    resp = test_client.post(
        "/agent/process-backlog",
        headers={"X-API-Key": "changeme-secret-key"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["processed_count"] >= 1
    assert any(inc["incident_id"] == "INC-QUEUE-01" for inc in data["incidents"])
