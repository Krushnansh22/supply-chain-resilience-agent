"""
tests/test_agent.py
Owner: Developer 1 (Agent) / Developer 2 (Backend)

Tests for app/agent/agent_loop.py state machine and context gathering.
"""

from datetime import datetime, timezone
import mongomock
import pytest

from app.agent.agent_loop import run_agent_for_incident, get_agent_state
from app.agent.states import AgentState


@pytest.fixture
def mock_db():
    return mongomock.MongoClient()["test_agent_db"]


def test_supplier_delay_scenario_reaches_investigating(mock_db):
    """Triggering the agent moves incident from DETECTED to INVESTIGATING and gathers context."""
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
    assert result["state"] == AgentState.INVESTIGATING.value
    assert result["context"]["component_id"] == "COMP-001"
    assert result["context"]["inventory"]["usable_stock"] == 200

    # Verify incident state in DB
    updated = mock_db["incidents"].find_one({"incident_id": "INC-001"})
    assert updated["status"] == AgentState.INVESTIGATING.value

    # Verify audit log was recorded
    audit = mock_db["audit_logs"].find_one({"incident_id": "INC-001"})
    assert audit is not None
    assert audit["decision"] == "INVESTIGATING"


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
