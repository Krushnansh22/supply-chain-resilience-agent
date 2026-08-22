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
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.agent.agent_loop import run_agent_for_incident, get_agent_state
from app.agent.states import AgentState

router = APIRouter()


class TriggerRequest(BaseModel):
    incident_id: str


class ApprovalDecision(BaseModel):
    incident_id: str
    approver: str = "human-coordinator"


@router.post("/trigger")
def trigger_agent(req: TriggerRequest, db: Session = Depends(get_db)):
    """
    Kick off (or resume) the agent loop for a given incident.
    TODO (Dev1): decide sync vs background-task execution. For an 18h hackathon,
    starting simple (blocking call, or a simple in-process background thread) is fine;
    do not over-engineer a task queue.
    """
    result = run_agent_for_incident(req.incident_id, db)
    return result


@router.get("/state/{incident_id}")
def agent_state(incident_id: str, db: Session = Depends(get_db)):
    return {"incident_id": incident_id, "state": get_agent_state(incident_id, db)}


@router.post("/approve")
def approve_plan(decision: ApprovalDecision, db: Session = Depends(get_db)):
    """
    TODO (Dev1): on approval, transition state WAITING_APPROVAL -> EXECUTING,
    call tools/erp_tools.update_erp(), write audit log, transition -> RESOLVED.
    """
    raise NotImplementedError("TODO: wire approval flow into agent_loop.py")


@router.post("/reject")
def reject_plan(decision: ApprovalDecision, db: Session = Depends(get_db)):
    """TODO (Dev1): on rejection, trigger REPLANNING state with 'human rejected' as context."""
    raise NotImplementedError("TODO: wire rejection flow into agent_loop.py")
