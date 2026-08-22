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

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from pymongo.database import Database

from app.mongo_database import get_mongo_db
from app.repositories.incident_repository import IncidentRepository
from app.schemas.common import IncidentOut
from app.schemas.common import AuditLogOut

router = APIRouter()

def get_repo(db: Database = Depends(get_mongo_db)):
    return IncidentRepository(db)


@router.get("/", response_model=list[IncidentOut])
def list_incidents(repo: IncidentRepository = Depends(get_repo)):
    """GET /incidents -> supports frontend polling for the Overview page."""
    return repo.list_all_ordered("created_at", -1)


@router.get("/{incident_id}", response_model=IncidentOut)
def get_incident(incident_id: str, repo: IncidentRepository = Depends(get_repo)):
    row = repo.get_by_incident_id(incident_id)
    if not row:
        raise HTTPException(status_code=404, detail="incident not found")
    return row


@router.get("/{incident_id}/activity", response_model=List[AuditLogOut])
def get_incident_activity(incident_id: str, db: Database = Depends(get_mongo_db)):
    """
    GET /incidents/{incident_id}/activity
    Returns the chronological audit log for this incident —
    the Agent Activity feed shown in the Incident Command Center (docs Section 14).
    """
    incident = IncidentRepository(db).get_by_incident_id(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="incident not found")
    return list(db["audit_logs"].find({"incident_id": incident_id}, {"_id": 0}).sort("timestamp", 1))
