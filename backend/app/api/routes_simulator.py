"""
app/api/routes_simulator.py
Owner: Developer 2 (Backend / Simulation)
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, field_validator

from app.database import get_db
from app.schemas.common import IncidentOut
from app.simulator.disruption_injector import inject_scenario, SCENARIO_DEFAULTS
from app.middleware.security import require_api_key
from app.middleware.rate_limiter import check_rate_limit

router = APIRouter()

VALID_SCENARIOS = set(SCENARIO_DEFAULTS.keys())


class InjectRequest(BaseModel):
    scenario: str

    @field_validator("scenario")
    @classmethod
    def validate_scenario(cls, v: str) -> str:
        # Strip whitespace and null bytes
        v = v.strip().replace("\x00", "")
        if not v:
            raise ValueError("scenario must not be empty")
        if len(v) > 64:
            raise ValueError("scenario name too long")
        return v.upper()

    class Config:
        extra = "forbid"  # Reject any unexpected JSON fields


@router.post("/inject", response_model=IncidentOut)
def inject(
    req: InjectRequest,
    request: Request,
    db: Session = Depends(get_db),
    _auth: None = Depends(require_api_key),
):
    """
    POST /simulator/inject {"scenario": "SUPPLIER_DELAY"} -> creates a new incident.
    Returns 422 if scenario name is unknown.
    Rate limited: 20 injections per 60 seconds per IP.
    """
    # Rate limit: max 20 injections per minute per IP
    check_rate_limit(request, bucket="simulator_inject", max_calls=20, window_seconds=60)

    if req.scenario not in VALID_SCENARIOS:
        raise HTTPException(
            status_code=422,
            detail=f"Unknown scenario '{req.scenario}'. Valid options: {sorted(VALID_SCENARIOS)}",
        )
    incident = inject_scenario(req.scenario, db)
    return IncidentOut.model_validate(incident)
