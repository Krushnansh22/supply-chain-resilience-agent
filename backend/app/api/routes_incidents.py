"""
app/api/routes_incidents.py
Owner: Developer 2 (Backend / Simulation)

RECEIVES: incidents created by simulator/disruption_injector.py
DELIVERS:
  - list to Overview dashboard "ACTIVE INCIDENTS" section (Dev4)
  - single incident to Incident Command Center screen (Dev4)
  - /incidents/{id}/activity -> agent activity feed for this incident
  - is the thing agent/agent_loop.py polls or subscribes to, to know what to work on
"""

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.incidents import Incident
from app.models.audit_logs import AuditLog
from app.schemas.common import IncidentOut, AuditLogOut

router = APIRouter()

_INCIDENT_ID_PATTERN = r"^[A-Za-z0-9_-]+$"


@router.get("/", response_model=list[IncidentOut])
def list_incidents(db: Session = Depends(get_db)):
    """GET /incidents -> supports frontend polling for the Overview page."""
    return db.query(Incident).order_by(Incident.created_at.desc()).all()


@router.get("/{incident_id}", response_model=IncidentOut)
def get_incident(
    incident_id: str = Path(..., pattern=_INCIDENT_ID_PATTERN, min_length=1, max_length=32),
    db: Session = Depends(get_db),
):
    row = db.query(Incident).filter(Incident.incident_id == incident_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="incident not found")
    return row


@router.get("/{incident_id}/activity", response_model=List[AuditLogOut])
def get_incident_activity(
    incident_id: str = Path(..., pattern=_INCIDENT_ID_PATTERN, min_length=1, max_length=32),
    db: Session = Depends(get_db),
):
    """
    GET /incidents/{incident_id}/activity
    Returns the chronological audit log for this incident —
    the Agent Activity feed shown in the Incident Command Center (docs Section 14).
    """
    incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="incident not found")

    logs = (
        db.query(AuditLog)
        .filter(AuditLog.incident_id == incident_id)
        .order_by(AuditLog.timestamp.asc())
        .all()
    )
    return logs
