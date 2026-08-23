"""
tests/test_agent.py
Owner: Developer 1 (Agent) / Developer 2 (Backend)

Tests for app/agent/agent_loop.py autonomous multi-step reasoning, state machine, and tool execution.
"""

from datetime import datetime, timezone
import mongomock
import pytest

from app.agent.agent_loop import run_agent_for_incident, get_agent_state
from app.agent.states import AgentState


@pytest.fixture
def mock_db():
    return mongomock.MongoClient()["test_agent_db"]


def test_supplier_delay_scenario_runs_full_agent_loop(mock_db):
    """Triggering the agent runs dynamic task decomposition, multi-step investigation, and recovery planning."""
    mock_db["incidents"].insert_one({
        "incident_id": "INC-001",
        "type": "SUPPLIER_DELAY",
        "severity": "HIGH",
        "affected_component": "COMP-001",
        "status": "DETECTED",
        "created_at": datetime.now(timezone.utc),
    })
    mock_db["inventory"].insert_one({
        "component_id": "COMP-001",
        "usable_stock": 200,
        "daily_usage": 20.0,
    })

    result = run_agent_for_incident("INC-001", mock_db)

    assert result["incident_id"] == "INC-001"
    assert result["state"] in (AgentState.WAITING_APPROVAL.value, AgentState.RESOLVED.value)
    assert result["context"]["component_id"] == "COMP-001"
    assert len(result["tasks"]) >= 5
    assert result["audit_trail_count"] > 0

    # Verify incident state in DB
    updated = mock_db["incidents"].find_one({"incident_id": "INC-001"})
    assert updated["status"] == result["state"]

    # Verify audit logs were recorded
    audit_count = mock_db["audit_logs"].count_documents({"incident_id": "INC-001"})
    assert audit_count >= 3


def test_agent_trigger_nonexistent_incident(mock_db):
    """Triggering for missing incident returns error without crashing."""
    result = run_agent_for_incident("INC-NONEXISTENT", mock_db)
    assert "error" in result
    assert result["incident_id"] == "INC-NONEXISTENT"


def test_get_agent_state(mock_db):
    """get_agent_state retrieves the current lifecycle status of an incident."""
    mock_db["incidents"].insert_one({
        "incident_id": "INC-002",
        "status": AgentState.WAITING_APPROVAL.value,
    })

    state = get_agent_state("INC-002", mock_db)
    assert state == AgentState.WAITING_APPROVAL.value

    # Unknown incident returns UNKNOWN
    assert get_agent_state("INC-UNKNOWN", mock_db) == "UNKNOWN"


def test_execute_tool_success_and_error_handling(mock_db):
    """execute_tool executes valid tools and gracefully handles errors/missing params."""
    from app.agent.tool_executor import execute_tool

    # 1. Successful execution
    mock_db["inventory"].insert_one({
        "component_id": "COMP-EXEC-1",
        "usable_stock": 300,
        "daily_usage": 30.0,
    })
    res = execute_tool("get_inventory", {"component_id": "COMP-EXEC-1"}, mock_db)
    assert res.success is True
    assert res.data["usable_stock"] == 300

    # 2. Missing parameter returns failure instead of raising KeyError
    res_missing_param = execute_tool("get_inventory", {}, mock_db)
    assert res_missing_param.success is False
    assert "missing" in res_missing_param.error.lower()

    # 3. Unknown tool returns failure instead of crashing
    res_unknown = execute_tool("nonexistent_tool", {}, mock_db)
    assert res_unknown.success is False
    assert "unknown" in res_unknown.error.lower()

    # 4. Successful execution of compute_recovery_options / build_recovery_plan
    mock_db["suppliers"].insert_one({"supplier_id": "SUP-001", "name": "Apex", "quality_score": 90, "reliability_score": 95})
    res_plan = execute_tool("compute_recovery_options", {"component_id": "COMP-EXEC-1", "required_quantity": 100, "required_by_days": 5}, mock_db)
    assert res_plan.success is True
    assert "options" in res_plan.data
