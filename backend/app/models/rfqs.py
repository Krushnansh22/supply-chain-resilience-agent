"""
app/models/rfqs.py
Owner: Developer 2 (Backend / Simulation)

RECEIVES: written by tools/rfq_tools.request_rfq() -> simulator/supplier_simulator.py
          generates a synthetic quote response.
DELIVERS: read by decision_engine/recovery_planner.py to build recovery plan options.
"""

from sqlalchemy import Column, String, Integer, Float, Boolean
from app.database import Base


class RFQ(Base):
    __tablename__ = "rfqs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    supplier_id = Column(String, nullable=False, index=True)
    component_id = Column(String, nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    delivery_days = Column(Integer, nullable=False)
    expedite_available = Column(Boolean, nullable=False, default=False)
    expedite_fee = Column(Float, nullable=True, default=0.0)
