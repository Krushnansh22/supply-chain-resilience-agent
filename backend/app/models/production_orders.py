"""
app/models/production_orders.py
Owner: Developer 2 (Backend / Simulation)

RECEIVES: seed data (5-10 production orders)
DELIVERS: read by decision_engine/production_risk.py to determine production-at-risk status
"""

from sqlalchemy import Column, String, Integer, DateTime
from app.database import Base


class ProductionOrder(Base):
    __tablename__ = "production_orders"

    production_id = Column(String, primary_key=True, index=True)  # e.g. "PROD-882"
    product = Column(String, nullable=False)
    component_id = Column(String, nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    component_per_unit = Column(Integer, nullable=False, default=1)
    deadline = Column(DateTime, nullable=True)
    priority = Column(String, nullable=False, default="MEDIUM")  # LOW | MEDIUM | HIGH
    status = Column(String, nullable=False, default="ON_TRACK")  # ON_TRACK | AT_RISK | BLOCKED
