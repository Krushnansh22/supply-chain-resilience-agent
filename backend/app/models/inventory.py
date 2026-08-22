"""
app/models/inventory.py
Owner: Developer 2 (Backend / Simulation)
Schema source: team design doc Section 6 (REQUIRED fields marked from PS where applicable)

RECEIVES: rows written by simulator/seed_data.py and updated by tools/erp_tools.update_erp()
DELIVERS: read by decision_engine/inventory_calc.py to compute days_of_supply, coverage, etc.
"""

from sqlalchemy import Column, String, Float, Integer
from app.database import Base


class Inventory(Base):
    __tablename__ = "inventory"

    component_id = Column(String, primary_key=True, index=True)  # e.g. "COMP-104"
    current_stock = Column(Integer, nullable=False, default=0)
    usable_stock = Column(Integer, nullable=False, default=0)   # excludes quarantined/defective
    daily_usage = Column(Float, nullable=False, default=0.0)
    safety_stock = Column(Integer, nullable=False, default=0)

    # TODO (Dev3): confirm whether days_of_supply should be a stored column
    # or always computed on the fly in decision_engine/inventory_calc.py.
    # Recommendation: compute on the fly to avoid stale data bugs during demo.
