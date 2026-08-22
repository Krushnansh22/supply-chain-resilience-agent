"""
app/api/routes_agent.py
Owner: Developer 1 (Agent) defines behavior; Developer 2 wires the FastAPI plumbing.

This is the bridge between the frontend (Dev4) and the agent loop (Dev1).

RECEIVES:
  - POST /agent/trigger        -> frontend or simulator asks agent to start working an incident
  - POST /agent/approve        -> human coordinator approves a pending recovery plan
  - POST /agent/reject         -> human coordinator rejects a pending recovery plan
DELIVERS:
  - GET /agent/state/{incident_id} -> current agent state machine position (docs/AGENT_STATE_MACHINE.md)
  - GET /agent/plan/{incident_id}  -> current RecoveryPlan (schemas/recovery_plan.py) for Approval UI
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from pymongo.database import Database

from app.mongo_database import get_mongo_db
from app.agent.agent_loop import run_agent_for_incident, get_agent_state
from app.agent.states import AgentState

router = APIRouter()


class TriggerRequest(BaseModel):
    incident_id: str


class ApprovalDecision(BaseModel):
    incident_id: str
    approver: str = "human-coordinator"


@router.post("/trigger")
def trigger_agent(req: TriggerRequest, db: Database = Depends(get_mongo_db)):
    """
    Kick off (or resume) the agent loop for a given incident.
    TODO (Dev1): decide sync vs background-task execution. For an 18h hackathon,
    starting simple (blocking call, or a simple in-process background thread) is fine;
    do not over-engineer a task queue.
    """
    result = run_agent_for_incident(req.incident_id, db)
    return result


@router.get("/state/{incident_id}")
def agent_state(incident_id: str, db: Database = Depends(get_mongo_db)):
    return {"incident_id": incident_id, "state": get_agent_state(incident_id, db)}


@router.get("/plan/{incident_id}")
def agent_plan(incident_id: str, db: Database = Depends(get_mongo_db)):
    plan = db["recovery_plans"].find_one({"incident_id": incident_id}, {"_id": 0})
    if not plan:
        return {"incident_id": incident_id, "options": [], "recommended_option_id": "", "recommendation_reason": "No recovery plan has been generated.", "requires_human_approval": False, "approval_threshold_usd": 50000}
    return plan


@router.post("/approve")
def approve_plan(decision: ApprovalDecision, db: Database = Depends(get_mongo_db)):
    """
    TODO (Dev1): on approval, transition state WAITING_APPROVAL -> EXECUTING,
    call tools/erp_tools.update_erp(), write audit log, transition -> RESOLVED.
    """
    incident = db["incidents"].find_one({"incident_id": decision.incident_id}, {"_id": 0})
    if not incident:
        return {"error": "incident not found"}
    db["incidents"].update_one({"incident_id": decision.incident_id}, {"$set": {"status": AgentState.EXECUTING.value}})
    db["audit_logs"].insert_one({"incident_id": decision.incident_id, "action": "Recovery plan approved by coordinator.", "decision": "APPROVED"})
    return {"incident_id": decision.incident_id, "state": AgentState.EXECUTING.value}


@router.post("/reject")
def reject_plan(decision: ApprovalDecision, db: Database = Depends(get_mongo_db)):
    """TODO (Dev1): on rejection, trigger REPLANNING state with 'human rejected' as context."""
    incident = db["incidents"].find_one({"incident_id": decision.incident_id}, {"_id": 0})
    if not incident:
        return {"error": "incident not found"}
    db["incidents"].update_one({"incident_id": decision.incident_id}, {"$set": {"status": AgentState.REPLANNING.value}})
    db["audit_logs"].insert_one({"incident_id": decision.incident_id, "action": "Recovery plan rejected; replanning required.", "decision": "REJECTED"})
    return {"incident_id": decision.incident_id, "state": AgentState.REPLANNING.value}
