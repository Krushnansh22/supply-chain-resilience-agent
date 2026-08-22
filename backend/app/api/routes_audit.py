"""
app/api/routes_audit.py
Owner: Developer 2 (Backend / Simulation)

RECEIVES: rows written by app/audit/audit_logger.py (called from every tool + agent decision)
DELIVERS: chronological timeline to the frontend Audit page (docs Section 17)
"""

from fastapi import APIRouter, Depends
from typing import Optional
from pymongo.database import Database

from app.mongo_database import get_mongo_db
from app.repositories.audit_log_repository import AuditLogRepository
from app.schemas.common import AuditLogOut

router = APIRouter()

def get_repo(db: Database = Depends(get_mongo_db)):
    return AuditLogRepository(db)


@router.get("/", response_model=list[AuditLogOut])
def list_audit_logs(incident_id: Optional[str] = None, repo: AuditLogRepository = Depends(get_repo)):
    """GET /audit?incident_id=INC-001 -> full or incident-scoped audit timeline."""
    if incident_id:
        return repo.get_by_incident_id(incident_id)
    return repo.list_all()
