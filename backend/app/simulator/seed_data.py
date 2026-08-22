"""
app/simulator/seed_data.py
Owner: Developer 2 (Backend / Simulation)

Populates the DB with the hero scenario + surrounding filler data at target scale
(team doc Section 5): ~20 components, 10-20 suppliers, 20-40 POs, 5-10 production orders.

HERO CHAIN (must exist exactly as named so the demo script / frontend mockups line up):
    COMP-104 -> PO-7712 -> SUP-21 -> PROD-882

RECEIVES: a DB session (called once from database.init_db() at app startup)
DELIVERS: rows in inventory / suppliers / purchase_orders / production_orders tables
"""

from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.models.suppliers import Supplier
from app.models.purchase_orders import PurchaseOrder
from app.models.production_orders import ProductionOrder


def run(db: Session) -> None:
    """
    TODO (Dev2): flesh out to target data scale. Minimal hero-scenario seed below
    is enough to make the whole pipeline runnable end to end immediately.
    """
    if db.query(Inventory).count() > 0:
        return  # already seeded

    db.add(Inventory(component_id="COMP-104", current_stock=390, usable_stock=390,
                      daily_usage=90.0, safety_stock=100))

    db.add(Supplier(supplier_id="SUP-21", name="Alpha Components Pvt Ltd",
                     quality_score=88, reliability_score=72, certifications="ISO9001"))
    db.add(Supplier(supplier_id="SUP-18", name="Beta Precision Supplies",
                     quality_score=95, reliability_score=91, certifications="ISO9001,RoHS"))
    db.add(Supplier(supplier_id="SUP-42", name="Gamma Rapid Parts",
                     quality_score=80, reliability_score=85, certifications="RoHS"))

    db.add(PurchaseOrder(po_id="PO-7712", component_id="COMP-104", supplier_id="SUP-21",
                          quantity=600, status="DELAYED", unit_price=140.0))

    db.add(ProductionOrder(production_id="PROD-882", product="Widget-X", component_id="COMP-104",
                            quantity=200, component_per_unit=3, priority="HIGH", status="ON_TRACK"))

    db.commit()

    # TODO (Dev2): add remaining ~19 components, ~17 suppliers, ~35 POs, ~9 production
    # orders as filler data so the Inventory/Suppliers/Production pages don't look empty,
    # but keep the DEMO focused on the hero chain above (team doc Section 5).
