"""
app/audit/audit_logger.py
Owner: Developer 2 (Backend / Simulation), called from EVERYWHERE (Dev1's agent loop,
       every tool in app/tools/*, Dev3's decision engine indirectly via tool summaries)

REQUIRED by PS Core Capability #4: "Output human-readable reasoning logs" +
"Comprehensive Audit Trail & Explainability Output" (10% of scoring).

RECEIVES: every significant tool call / decision / state transition, as a single
          `log_event(...)` call.
DELIVERS: rows in app/models/audit_logs.py, surfaced via GET /audit to the frontend
          Audit Timeline (docs Section 17) and the Overview "AGENT ACTIVITY" feed.

IMPORTANT (team doc Section 14): action/result/reason must be safe, human-readable
summaries — NEVER paste raw LLM chain-of-thought here.
"""

from sqlalchemy.orm import Session
from datetime import datetime

from app.models.audit_logs import AuditLog


def log_event(
    db: Session,
    incident_id: str | None,
    action: str,
    tool: str | None = None,
    result: str | None = None,
    decision: str | None = None,
    reason: str | None = None,
) -> AuditLog:
    entry = AuditLog(
        timestamp=datetime.utcnow(),
        incident_id=incident_id,
        action=action,
        tool=tool,
        result=result,
        decision=decision,
        reason=reason,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
