"""
app/api/routes_incidents.py
Owner: Developer 2 (Backend / Simulation)

RECEIVES: incidents created by simulator/disruption_injector.py
DELIVERS:
  - list to Overview dashboard "ACTIVE INCIDENTS" section (Dev4)
  - single incident to Incident Command Center screen (Dev4)
  - is the thing agent/agent_loop.py polls or subscribes to, to know what to work on
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.incidents import Incident
from app.schemas.common import IncidentOut

router = APIRouter()


@router.get("/", response_model=list[IncidentOut])
def list_incidents(db: Session = Depends(get_db)):
    """GET /incidents -> supports frontend polling for the Overview page."""
    return db.query(Incident).order_by(Incident.created_at.desc()).all()


@router.get("/{incident_id}", response_model=IncidentOut)
def get_incident(incident_id: str, db: Session = Depends(get_db)):
    row = db.query(Incident).filter(Incident.incident_id == incident_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="incident not found")
    return row

# TODO (Dev1/Dev2): GET /incidents/{id}/activity -> agent activity feed for this incident
#                    (join of audit_logs filtered by incident_id, human-readable only)
