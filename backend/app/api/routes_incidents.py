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
from pymongo.database import Database

from app.mongo_database import get_mongo_db
from app.repositories.incident_repository import IncidentRepository
from app.schemas.common import IncidentOut

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

# TODO (Dev1/Dev2): GET /incidents/{id}/activity -> agent activity feed for this incident
#                    (join of audit_logs filtered by incident_id, human-readable only)
