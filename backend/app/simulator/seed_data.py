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

from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.models.suppliers import Supplier
from app.models.purchase_orders import PurchaseOrder
from app.models.production_orders import ProductionOrder


def run(db: Session) -> None:
    if db.query(Inventory).count() > 0:
        return  # already seeded

    now = datetime.now(timezone.utc)

    # ─────────────────────────────────────────────
    # SUPPLIERS (10 total — 3 hero + 7 filler)
    # ─────────────────────────────────────────────
    suppliers = [
        # Hero chain suppliers
        Supplier(supplier_id="SUP-21", name="Alpha Components Pvt Ltd",
                 quality_score=88, reliability_score=72, certifications="ISO9001"),
        Supplier(supplier_id="SUP-18", name="Beta Precision Supplies",
                 quality_score=95, reliability_score=91, certifications="ISO9001,RoHS"),
        Supplier(supplier_id="SUP-42", name="Gamma Rapid Parts",
                 quality_score=80, reliability_score=85, certifications="RoHS"),
        # Filler suppliers
        Supplier(supplier_id="SUP-07", name="Delta Industrial Ltd",
                 quality_score=76, reliability_score=80, certifications="ISO9001"),
        Supplier(supplier_id="SUP-11", name="Epsilon Electronics",
                 quality_score=92, reliability_score=88, certifications="ISO9001,RoHS,CE"),
        Supplier(supplier_id="SUP-33", name="Zeta Fab Works",
                 quality_score=70, reliability_score=65, certifications="RoHS"),
        Supplier(supplier_id="SUP-55", name="Eta Supply Chain Co",
                 quality_score=85, reliability_score=90, certifications="ISO9001"),
        Supplier(supplier_id="SUP-63", name="Theta MFG Group",
                 quality_score=78, reliability_score=75, certifications="CE"),
        Supplier(supplier_id="SUP-72", name="Iota Tech Parts",
                 quality_score=91, reliability_score=83, certifications="ISO9001,CE"),
        Supplier(supplier_id="SUP-88", name="Kappa Global Sourcing",
                 quality_score=82, reliability_score=79, certifications="RoHS,CE"),
    ]
    db.add_all(suppliers)

    # ─────────────────────────────────────────────
    # INVENTORY (20 components)
    # ─────────────────────────────────────────────
    inventory_items = [
        # Hero component — intentionally tight supply to trigger demo
        Inventory(component_id="COMP-104", current_stock=390, usable_stock=390,
                  daily_usage=90.0, safety_stock=100),
        # Filler components
        Inventory(component_id="COMP-101", current_stock=1200, usable_stock=1200,
                  daily_usage=50.0, safety_stock=150),
        Inventory(component_id="COMP-102", current_stock=800,  usable_stock=750,
                  daily_usage=30.0, safety_stock=80),
        Inventory(component_id="COMP-103", current_stock=550,  usable_stock=550,
                  daily_usage=20.0, safety_stock=60),
        Inventory(component_id="COMP-105", current_stock=2000, usable_stock=1950,
                  daily_usage=100.0, safety_stock=200),
        Inventory(component_id="COMP-106", current_stock=450,  usable_stock=400,
                  daily_usage=15.0, safety_stock=50),
        Inventory(component_id="COMP-107", current_stock=300,  usable_stock=300,
                  daily_usage=25.0, safety_stock=75),
        Inventory(component_id="COMP-108", current_stock=1500, usable_stock=1500,
                  daily_usage=60.0, safety_stock=120),
        Inventory(component_id="COMP-109", current_stock=900,  usable_stock=880,
                  daily_usage=40.0, safety_stock=100),
        Inventory(component_id="COMP-110", current_stock=650,  usable_stock=600,
                  daily_usage=35.0, safety_stock=90),
        Inventory(component_id="COMP-111", current_stock=2500, usable_stock=2500,
                  daily_usage=120.0, safety_stock=250),
        Inventory(component_id="COMP-112", current_stock=400,  usable_stock=380,
                  daily_usage=18.0, safety_stock=55),
        Inventory(component_id="COMP-113", current_stock=750,  usable_stock=750,
                  daily_usage=45.0, safety_stock=110),
        Inventory(component_id="COMP-114", current_stock=1100, usable_stock=1050,
                  daily_usage=55.0, safety_stock=130),
        Inventory(component_id="COMP-115", current_stock=330,  usable_stock=330,
                  daily_usage=22.0, safety_stock=65),
        Inventory(component_id="COMP-116", current_stock=1800, usable_stock=1750,
                  daily_usage=80.0, safety_stock=180),
        Inventory(component_id="COMP-117", current_stock=500,  usable_stock=480,
                  daily_usage=28.0, safety_stock=70),
        Inventory(component_id="COMP-118", current_stock=220,  usable_stock=200,
                  daily_usage=12.0, safety_stock=40),
        Inventory(component_id="COMP-119", current_stock=960,  usable_stock=960,
                  daily_usage=48.0, safety_stock=115),
        Inventory(component_id="COMP-120", current_stock=3000, usable_stock=3000,
                  daily_usage=150.0, safety_stock=300),
    ]
    db.add_all(inventory_items)

    # ─────────────────────────────────────────────
    # PURCHASE ORDERS (25 POs)
    # ─────────────────────────────────────────────
    purchase_orders = [
        # Hero PO — DELAYED to trigger demo
        PurchaseOrder(po_id="PO-7712", component_id="COMP-104", supplier_id="SUP-21",
                      quantity=600, status="DELAYED", unit_price=140.0,
                      expected_delivery=now + timedelta(days=14)),
        # Filler POs
        PurchaseOrder(po_id="PO-7700", component_id="COMP-101", supplier_id="SUP-18",
                      quantity=500, status="OPEN", unit_price=85.0,
                      expected_delivery=now + timedelta(days=5)),
        PurchaseOrder(po_id="PO-7701", component_id="COMP-102", supplier_id="SUP-42",
                      quantity=300, status="OPEN", unit_price=120.0,
                      expected_delivery=now + timedelta(days=7)),
        PurchaseOrder(po_id="PO-7702", component_id="COMP-103", supplier_id="SUP-07",
                      quantity=400, status="DISPATCHED", unit_price=95.0,
                      expected_delivery=now + timedelta(days=3)),
        PurchaseOrder(po_id="PO-7703", component_id="COMP-105", supplier_id="SUP-11",
                      quantity=1000, status="OPEN", unit_price=200.0,
                      expected_delivery=now + timedelta(days=10)),
        PurchaseOrder(po_id="PO-7704", component_id="COMP-106", supplier_id="SUP-33",
                      quantity=200, status="OPEN", unit_price=75.0,
                      expected_delivery=now + timedelta(days=8)),
        PurchaseOrder(po_id="PO-7705", component_id="COMP-107", supplier_id="SUP-55",
                      quantity=350, status="RECEIVED", unit_price=110.0,
                      expected_delivery=now - timedelta(days=2)),
        PurchaseOrder(po_id="PO-7706", component_id="COMP-108", supplier_id="SUP-63",
                      quantity=800, status="OPEN", unit_price=55.0,
                      expected_delivery=now + timedelta(days=6)),
        PurchaseOrder(po_id="PO-7707", component_id="COMP-109", supplier_id="SUP-72",
                      quantity=450, status="OPEN", unit_price=130.0,
                      expected_delivery=now + timedelta(days=9)),
        PurchaseOrder(po_id="PO-7708", component_id="COMP-110", supplier_id="SUP-88",
                      quantity=250, status="DELAYED", unit_price=90.0,
                      expected_delivery=now + timedelta(days=15)),
        PurchaseOrder(po_id="PO-7709", component_id="COMP-111", supplier_id="SUP-18",
                      quantity=1200, status="OPEN", unit_price=40.0,
                      expected_delivery=now + timedelta(days=4)),
        PurchaseOrder(po_id="PO-7710", component_id="COMP-112", supplier_id="SUP-42",
                      quantity=180, status="DISPATCHED", unit_price=160.0,
                      expected_delivery=now + timedelta(days=2)),
        PurchaseOrder(po_id="PO-7711", component_id="COMP-113", supplier_id="SUP-07",
                      quantity=500, status="OPEN", unit_price=105.0,
                      expected_delivery=now + timedelta(days=11)),
        PurchaseOrder(po_id="PO-7713", component_id="COMP-114", supplier_id="SUP-11",
                      quantity=600, status="OPEN", unit_price=115.0,
                      expected_delivery=now + timedelta(days=7)),
        PurchaseOrder(po_id="PO-7714", component_id="COMP-115", supplier_id="SUP-33",
                      quantity=220, status="OPEN", unit_price=80.0,
                      expected_delivery=now + timedelta(days=12)),
        PurchaseOrder(po_id="PO-7715", component_id="COMP-116", supplier_id="SUP-55",
                      quantity=900, status="DISPATCHED", unit_price=65.0,
                      expected_delivery=now + timedelta(days=3)),
        PurchaseOrder(po_id="PO-7716", component_id="COMP-117", supplier_id="SUP-63",
                      quantity=280, status="OPEN", unit_price=145.0,
                      expected_delivery=now + timedelta(days=8)),
        PurchaseOrder(po_id="PO-7717", component_id="COMP-118", supplier_id="SUP-72",
                      quantity=150, status="OPEN", unit_price=175.0,
                      expected_delivery=now + timedelta(days=13)),
        PurchaseOrder(po_id="PO-7718", component_id="COMP-119", supplier_id="SUP-88",
                      quantity=550, status="OPEN", unit_price=98.0,
                      expected_delivery=now + timedelta(days=6)),
        PurchaseOrder(po_id="PO-7719", component_id="COMP-120", supplier_id="SUP-21",
                      quantity=1500, status="OPEN", unit_price=30.0,
                      expected_delivery=now + timedelta(days=5)),
        PurchaseOrder(po_id="PO-7720", component_id="COMP-104", supplier_id="SUP-18",
                      quantity=200, status="OPEN", unit_price=145.0,
                      expected_delivery=now + timedelta(days=6)),
        PurchaseOrder(po_id="PO-7721", component_id="COMP-101", supplier_id="SUP-42",
                      quantity=700, status="RECEIVED", unit_price=82.0,
                      expected_delivery=now - timedelta(days=5)),
        PurchaseOrder(po_id="PO-7722", component_id="COMP-105", supplier_id="SUP-07",
                      quantity=500, status="OPEN", unit_price=195.0,
                      expected_delivery=now + timedelta(days=9)),
        PurchaseOrder(po_id="PO-7723", component_id="COMP-108", supplier_id="SUP-11",
                      quantity=400, status="DELAYED", unit_price=58.0,
                      expected_delivery=now + timedelta(days=20)),
        PurchaseOrder(po_id="PO-7724", component_id="COMP-113", supplier_id="SUP-55",
                      quantity=300, status="OPEN", unit_price=108.0,
                      expected_delivery=now + timedelta(days=10)),
    ]
    db.add_all(purchase_orders)

    # ─────────────────────────────────────────────
    # PRODUCTION ORDERS (8 orders)
    # ─────────────────────────────────────────────
    production_orders = [
        # Hero production order — depends on COMP-104
        ProductionOrder(production_id="PROD-882", product="Widget-X",
                        component_id="COMP-104", quantity=200, component_per_unit=3,
                        priority="HIGH", status="ON_TRACK",
                        deadline=now + timedelta(days=5)),
        # Filler production orders
        ProductionOrder(production_id="PROD-801", product="Module-Alpha",
                        component_id="COMP-101", quantity=150, component_per_unit=2,
                        priority="MEDIUM", status="ON_TRACK",
                        deadline=now + timedelta(days=10)),
        ProductionOrder(production_id="PROD-812", product="Assembly-Beta",
                        component_id="COMP-105", quantity=80, component_per_unit=5,
                        priority="HIGH", status="ON_TRACK",
                        deadline=now + timedelta(days=7)),
        ProductionOrder(production_id="PROD-823", product="Unit-Gamma",
                        component_id="COMP-108", quantity=300, component_per_unit=1,
                        priority="LOW", status="ON_TRACK",
                        deadline=now + timedelta(days=20)),
        ProductionOrder(production_id="PROD-834", product="Board-Delta",
                        component_id="COMP-111", quantity=500, component_per_unit=2,
                        priority="MEDIUM", status="AT_RISK",
                        deadline=now + timedelta(days=4)),
        ProductionOrder(production_id="PROD-845", product="Frame-Epsilon",
                        component_id="COMP-116", quantity=120, component_per_unit=4,
                        priority="HIGH", status="ON_TRACK",
                        deadline=now + timedelta(days=8)),
        ProductionOrder(production_id="PROD-856", product="Pack-Zeta",
                        component_id="COMP-102", quantity=200, component_per_unit=3,
                        priority="MEDIUM", status="ON_TRACK",
                        deadline=now + timedelta(days=15)),
        ProductionOrder(production_id="PROD-867", product="Kit-Eta",
                        component_id="COMP-113", quantity=60, component_per_unit=6,
                        priority="LOW", status="ON_TRACK",
                        deadline=now + timedelta(days=25)),
    ]
    db.add_all(production_orders)

    db.commit()
