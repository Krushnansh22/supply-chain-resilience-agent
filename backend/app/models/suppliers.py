"""
app/models/suppliers.py
Owner: Developer 2 (Backend / Simulation)

RECEIVES: seed data (10-20 suppliers) from simulator/seed_data.py
DELIVERS: read by decision_engine/supplier_scoring.py and tools/supplier_tools.get_supplier()
"""

from sqlalchemy import Column, String, Float
from app.database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    supplier_id = Column(String, primary_key=True, index=True)  # e.g. "SUP-21"
    name = Column(String, nullable=False)
    quality_score = Column(Float, nullable=False, default=0.0)      # 0-100
    reliability_score = Column(Float, nullable=False, default=0.0)  # 0-100
    certifications = Column(String, nullable=True)  # comma-separated, e.g. "ISO9001,RoHS"

    # TODO (Dev3): decide if MOQ (minimum order qty) belongs here or only on RFQ responses.
    # Team doc doesn't fix this — treat as CHOSEN, document your decision in DB_SCHEMA.md.
