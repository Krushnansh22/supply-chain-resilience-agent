"""
app/api/routes_agent.py
Owner: Developer 1 (Agent) defines behavior; Developer 2 wires the FastAPI plumbing.

SECURITY ADDITIONS (Dev2):
  - API key enforcement on all mutating endpoints (trigger, approve, reject)
  - Rate limiting: 10 agent triggers per minute per IP (prevents agent loop abuse)
  - Input validators on TriggerRequest and ApprovalDecision
"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, field_validator, Field

from app.database import get_db
from app.agent.agent_loop import run_agent_for_incident, get_agent_state
from app.agent.states import AgentState
from app.middleware.security import require_api_key
from app.middleware.rate_limiter import check_rate_limit

router = APIRouter()


class TriggerRequest(BaseModel):
    incident_id: str = Field(..., min_length=1, max_length=32, pattern=r"^[A-Za-z0-9_-]+$")

    @field_validator("incident_id")
    @classmethod
    def sanitize_id(cls, v: str) -> str:
        return v.strip().replace("\x00", "")

    class Config:
        extra = "forbid"


class ApprovalDecision(BaseModel):
    incident_id: str = Field(..., min_length=1, max_length=32, pattern=r"^[A-Za-z0-9_-]+$")
    approver: str = Field(default="human-coordinator", min_length=1, max_length=64)

    @field_validator("incident_id", "approver")
    @classmethod
    def sanitize_fields(cls, v: str) -> str:
        return v.strip().replace("\x00", "")

    class Config:
        extra = "forbid"


@router.post("/trigger")
def trigger_agent(
    req: TriggerRequest,
    request: Request,
    db: Session = Depends(get_db),
    _auth: None = Depends(require_api_key),
):
    """
    Kick off (or resume) the agent loop for a given incident.
    Rate limited: 10 triggers per minute per IP.
    """
    check_rate_limit(request, bucket="agent_trigger", max_calls=10, window_seconds=60)
    result = run_agent_for_incident(req.incident_id, db)
    return result


@router.get("/state/{incident_id}")
def agent_state(
    incident_id: str,
    db: Session = Depends(get_db),
):
    return {"incident_id": incident_id, "state": get_agent_state(incident_id, db)}


@router.post("/approve")
def approve_plan(
    decision: ApprovalDecision,
    request: Request,
    db: Session = Depends(get_db),
    _auth: None = Depends(require_api_key),
):
    """
    TODO (Dev1): on approval, transition WAITING_APPROVAL -> EXECUTING -> RESOLVED.
    Rate limited: 10 approvals per minute per IP.
    """
    check_rate_limit(request, bucket="agent_approve", max_calls=10, window_seconds=60)
    raise NotImplementedError("TODO: wire approval flow into agent_loop.py")


@router.post("/reject")
def reject_plan(
    decision: ApprovalDecision,
    request: Request,
    db: Session = Depends(get_db),
    _auth: None = Depends(require_api_key),
):
    """
    TODO (Dev1): on rejection, trigger REPLANNING state.
    Rate limited: 10 rejections per minute per IP.
    """
    check_rate_limit(request, bucket="agent_reject", max_calls=10, window_seconds=60)
    raise NotImplementedError("TODO: wire rejection flow into agent_loop.py")
