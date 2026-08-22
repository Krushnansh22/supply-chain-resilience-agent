"""
app/api/routes_audit.py
Owner: Developer 2 (Backend / Simulation)

RECEIVES: rows written by app/audit/audit_logger.py (called from every tool + agent decision)
DELIVERS: chronological timeline to the frontend Audit page (docs Section 17)
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.audit_logs import AuditLog
from app.schemas.common import AuditLogOut

router = APIRouter()


@router.get("/", response_model=list[AuditLogOut])
def list_audit_logs(incident_id: Optional[str] = None, db: Session = Depends(get_db)):
    """GET /audit?incident_id=INC-001 -> full or incident-scoped audit timeline."""
    q = db.query(AuditLog).order_by(AuditLog.timestamp.asc())
    if incident_id:
        q = q.filter(AuditLog.incident_id == incident_id)
    return q.all()
