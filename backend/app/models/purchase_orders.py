"""
app/models/purchase_orders.py
Owner: Developer 2 (Backend / Simulation)

RECEIVES: created by seed data + by tools/erp_tools.update_erp() when a recovery plan executes
DELIVERS: read by tools/inventory_tools + decision_engine to link component -> supplier -> PO
"""

from sqlalchemy import Column, String, Integer, Float, DateTime
from app.database import Base


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    po_id = Column(String, primary_key=True, index=True)  # e.g. "PO-7712"
    component_id = Column(String, nullable=False, index=True)
    supplier_id = Column(String, nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    expected_delivery = Column(DateTime, nullable=True)
    status = Column(String, nullable=False, default="OPEN")  # OPEN | DELAYED | DISPATCHED | RECEIVED | CANCELLED
    unit_price = Column(Float, nullable=False, default=0.0)
