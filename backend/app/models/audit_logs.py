"""
app/models/audit_logs.py
Owner: Developer 2 (Backend / Simulation), consumed heavily by Developer 1 (Agent) and Developer 3 (Decision Engine)

RECEIVES: EVERY tool call, decision, and state transition must be written here via
          app/audit/audit_logger.py:log_event(). This is the "explainability" backbone
          required by the official PS (10% of scoring: Audit Logging, Transparency, UX).
DELIVERS: read by /audit REST endpoint -> frontend Audit Timeline (docs Section 17).
"""

from sqlalchemy import Column, String, Integer, DateTime
from datetime import datetime
from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    incident_id = Column(String, nullable=True, index=True)
    action = Column(String, nullable=False)      # human-readable summary, e.g. "Checked inventory"
    tool = Column(String, nullable=True)         # which tool produced this, e.g. "get_inventory"
    result = Column(String, nullable=True)       # short result summary (NOT raw chain-of-thought)
    decision = Column(String, nullable=True)     # e.g. "EXECUTE" | "ESCALATE" | "REPLAN" | None
    reason = Column(String, nullable=True)       # human-readable justification
