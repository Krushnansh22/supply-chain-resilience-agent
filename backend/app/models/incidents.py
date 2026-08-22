"""
app/models/incidents.py
Owner: Developer 2 (Backend / Simulation)

RECEIVES: created by simulator/disruption_injector.py (manual "Inject X" buttons) and
          in future could be created by an automated event feed poller.
DELIVERS: primary input to agent/agent_loop.py — the agent watches for status=DETECTED
          incidents and begins the DETECTED -> INVESTIGATING -> ... state machine
          (see docs/AGENT_STATE_MACHINE.md).
"""

from sqlalchemy import Column, String, Integer, DateTime
from datetime import datetime
from app.database import Base


class Incident(Base):
    __tablename__ = "incidents"

    incident_id = Column(String, primary_key=True, index=True)  # e.g. "INC-001"
    type = Column(String, nullable=False)          # SUPPLIER_DELAY | SUPPLIER_LIE | QUALITY_FAILURE | BUDGET_OVERRUN | STALE_INVENTORY
    severity = Column(String, nullable=False)       # LOW | MEDIUM | HIGH | CRITICAL
    affected_component = Column(String, nullable=True, index=True)
    affected_po = Column(String, nullable=True, index=True)
    status = Column(String, nullable=False, default="DETECTED")  # mirrors agent state machine
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
