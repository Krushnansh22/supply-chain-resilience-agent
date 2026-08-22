"""
app/models/supplier_messages.py
Owner: Developer 2 (Backend / Simulation)

RECEIVES: written by tools/supplier_tools.send_supplier_message() and the simulated
          supplier's reply (see simulator/supplier_simulator.py) — including scenario
          "B: SUPPLIER LIE" where the message text may contradict tracking status.
DELIVERS: read by the Agent Activity feed (frontend) and by decision_engine's
          contradiction-detection logic for the supplier-lie scenario.
"""

from sqlalchemy import Column, String, Integer, DateTime
from datetime import datetime
from app.database import Base


class SupplierMessage(Base):
    __tablename__ = "supplier_messages"

    message_id = Column(Integer, primary_key=True, autoincrement=True)
    supplier_id = Column(String, nullable=False, index=True)
    po_id = Column(String, nullable=True, index=True)
    message = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
