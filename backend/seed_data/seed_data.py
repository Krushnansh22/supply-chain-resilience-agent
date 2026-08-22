"""
backend/seed_data/seed_data.py
Owner: Developer 2 (Backend / Simulation)

Populates MongoDB with comprehensive hero scenario data covering:
  - Normal, delayed, at-risk, blocked, cancelled, and resolved states
  - Multiple suppliers with varying quality/reliability/certification profiles
  - Inventory at normal, low, critical, and over-stock levels
  - Production orders at HIGH/MEDIUM/LOW priority with realistic deadlines
  - Pre-seeded incidents covering all agent workflow paths
  - Pre-seeded RFQ responses (accepted, rejected, expedite available)
  - Pre-seeded recovery plans (autonomous and approval-required)
  - Pre-seeded audit logs for dashboard demo
"""

from datetime import datetime, timedelta
from pymongo.database import Database
from app.repositories.inventory_repository import InventoryRepository

NOW = datetime.utcnow()


def run(db: Database) -> None:
    """Seeds the MongoDB with comprehensive realistic supply chain data."""
    inventory_repo = InventoryRepository(db)

    # Upserts below make startup additive: existing records are preserved while
    # missing demo records and newly introduced fields are backfilled.

    # ------------------------------------------------------------------
    # 1. INVENTORY  (8 items — normal, low, critical, over-stock, broken)
    # ------------------------------------------------------------------
    inventory_data = [
        # Normal stock — well above safety stock
        {
            "component_id": "COMP-101",
            "name": "Precision Resistor 100Ω",
            "current_stock": 2400,
            "usable_stock": 2400,
            "daily_usage": 120.0,
            "safety_stock": 360,
            "days_of_supply": 20,
            "location": "Warehouse-A",
            "last_updated": NOW.isoformat(),
        },
        # Low stock — approaching safety stock
        {
            "component_id": "COMP-102",
            "name": "Capacitor 10µF",
            "current_stock": 480,
            "usable_stock": 420,
            "daily_usage": 200.0,
            "safety_stock": 400,
            "days_of_supply": 2,
            "location": "Warehouse-A",
            "last_updated": NOW.isoformat(),
        },
        # Critical stock — below safety stock, production at risk
        {
            "component_id": "COMP-103",
            "name": "Microcontroller MCU-32X",
            "current_stock": 80,
            "usable_stock": 60,
            "daily_usage": 50.0,
            "safety_stock": 150,
            "days_of_supply": 1,
            "location": "Warehouse-B",
            "last_updated": NOW.isoformat(),
        },
        # Hero scenario component — being disrupted
        {
            "component_id": "COMP-104",
            "name": "Voltage Regulator VR-5A",
            "current_stock": 390,
            "usable_stock": 390,
            "daily_usage": 90.0,
            "safety_stock": 100,
            "days_of_supply": 4,
            "location": "Warehouse-A",
            "last_updated": NOW.isoformat(),
        },
        # Healthy stock
        {
            "component_id": "COMP-105",
            "name": "Inductor 47µH",
            "current_stock": 3000,
            "usable_stock": 3000,
            "daily_usage": 50.0,
            "safety_stock": 150,
            "days_of_supply": 60,
            "location": "Warehouse-C",
            "last_updated": NOW.isoformat(),
        },
        # Second hero scenario component — also disrupted
        {
            "component_id": "COMP-201",
            "name": "MOSFET Transistor N-Channel",
            "current_stock": 100,
            "usable_stock": 80,
            "daily_usage": 20.0,
            "safety_stock": 50,
            "days_of_supply": 4,
            "location": "Warehouse-B",
            "last_updated": NOW.isoformat(),
        },
        # Over-stock — excess that can be re-allocated
        {
            "component_id": "COMP-301",
            "name": "PCB Substrate FR4",
            "current_stock": 5000,
            "usable_stock": 5000,
            "daily_usage": 30.0,
            "safety_stock": 90,
            "days_of_supply": 166,
            "location": "Warehouse-D",
            "last_updated": NOW.isoformat(),
        },
        # Inconsistent entry — will be detected by LLM as anomaly
        {
            "component_id": "COMP-999",
            "name": "Unknown Component",
            "current_stock": 200,
            "usable_stock": 200,
            "daily_usage": 0.0,   # zero usage but stock exists — anomaly
            "safety_stock": 0,
            "days_of_supply": None,
            "location": "UNKNOWN",
            "last_updated": (NOW - timedelta(days=45)).isoformat(),  # stale
        },
    ]
    for item in inventory_data:
        inventory_repo.update({"component_id": item["component_id"]}, item)

    # ------------------------------------------------------------------
    # 2. SUPPLIERS  (8 — high/medium/low reliability, various certs)
    # ------------------------------------------------------------------
    suppliers = [
        # Primary delayed supplier (hero scenario)
        {
            "supplier_id": "SUP-21",
            "name": "Alpha Components Pvt Ltd",
            "contact_email": "orders@alpha-components.in",
            "quality_score": 88,
            "reliability_score": 72,
            "on_time_delivery_rate": 0.68,
            "certifications": "ISO9001",
            "lead_time_days": 14,
            "min_order_qty": 100,
            "country": "India",
            "status": "ACTIVE",
            "blacklisted": False,
        },
        # Alternative high-quality supplier
        {
            "supplier_id": "SUP-18",
            "name": "Beta Precision Supplies",
            "contact_email": "supply@beta-precision.com",
            "quality_score": 95,
            "reliability_score": 91,
            "on_time_delivery_rate": 0.94,
            "certifications": "ISO9001,RoHS",
            "lead_time_days": 7,
            "min_order_qty": 50,
            "country": "Germany",
            "status": "ACTIVE",
            "blacklisted": False,
        },
        # Expedite-capable supplier (higher cost)
        {
            "supplier_id": "SUP-42",
            "name": "Gamma Rapid Parts",
            "contact_email": "urgent@gamma-rapid.io",
            "quality_score": 80,
            "reliability_score": 85,
            "on_time_delivery_rate": 0.88,
            "certifications": "RoHS",
            "lead_time_days": 3,
            "min_order_qty": 200,
            "country": "Singapore",
            "status": "ACTIVE",
            "blacklisted": False,
        },
        # Budget supplier — lower reliability, no certs
        {
            "supplier_id": "SUP-55",
            "name": "Delta Bulk Electronics",
            "contact_email": "sales@deltabulk.net",
            "quality_score": 70,
            "reliability_score": 62,
            "on_time_delivery_rate": 0.60,
            "certifications": "",
            "lead_time_days": 21,
            "min_order_qty": 500,
            "country": "China",
            "status": "ACTIVE",
            "blacklisted": False,
        },
        # Premium fast supplier
        {
            "supplier_id": "SUP-09",
            "name": "Epsilon Fast-Track Supply",
            "contact_email": "vip@epsilon-supply.eu",
            "quality_score": 93,
            "reliability_score": 96,
            "on_time_delivery_rate": 0.97,
            "certifications": "ISO9001,RoHS,IATF16949",
            "lead_time_days": 5,
            "min_order_qty": 100,
            "country": "Netherlands",
            "status": "ACTIVE",
            "blacklisted": False,
        },
        # Suspended supplier — flagged for compliance issues
        {
            "supplier_id": "SUP-77",
            "name": "Zeta Discount Parts",
            "contact_email": "info@zetadiscount.cn",
            "quality_score": 55,
            "reliability_score": 40,
            "on_time_delivery_rate": 0.35,
            "certifications": "",
            "lead_time_days": 30,
            "min_order_qty": 1000,
            "country": "China",
            "status": "SUSPENDED",
            "blacklisted": True,
        },
        # New supplier — under evaluation
        {
            "supplier_id": "SUP-88",
            "name": "Eta Emerging Components",
            "contact_email": "hello@eta-components.in",
            "quality_score": 78,
            "reliability_score": None,  # no history — anomaly for LLM to flag
            "on_time_delivery_rate": None,
            "certifications": "ISO9001",
            "lead_time_days": 10,
            "min_order_qty": 100,
            "country": "India",
            "status": "UNDER_EVALUATION",
            "blacklisted": False,
        },
        # High-volume, slow delivery supplier
        {
            "supplier_id": "SUP-33",
            "name": "Theta Mass Producers",
            "contact_email": "bulk@theta-mass.com",
            "quality_score": 82,
            "reliability_score": 78,
            "on_time_delivery_rate": 0.75,
            "certifications": "ISO9001,RoHS",
            "lead_time_days": 28,
            "min_order_qty": 2000,
            "country": "Taiwan",
            "status": "ACTIVE",
            "blacklisted": False,
        },
    ]
    for s in suppliers:
        db["suppliers"].update_one({"supplier_id": s["supplier_id"]}, {"$set": s}, upsert=True)

    # ------------------------------------------------------------------
    # 3. PURCHASE ORDERS  (12 — all status variants for workflow testing)
    # ------------------------------------------------------------------
    purchase_orders = [
        # DELAYED — hero scenario trigger
        {
            "po_id": "PO-7712",
            "component_id": "COMP-104",
            "supplier_id": "SUP-21",
            "quantity": 600,
            "unit_price": 140.0,
            "total_value": 84000.0,
            "status": "DELAYED",
            "promised_delivery": (NOW - timedelta(days=3)).isoformat(),
            "current_expected_delivery": (NOW + timedelta(days=8)).isoformat(),
            "delay_days": 11,
            "last_erp_sync": NOW.isoformat(),
            "notes": "Supplier cited raw material shortage",
        },
        # OPEN — just placed
        {
            "po_id": "PO-8813",
            "component_id": "COMP-201",
            "supplier_id": "SUP-42",
            "quantity": 300,
            "unit_price": 45.0,
            "total_value": 13500.0,
            "status": "OPEN",
            "promised_delivery": (NOW + timedelta(days=5)).isoformat(),
            "current_expected_delivery": (NOW + timedelta(days=5)).isoformat(),
            "delay_days": 0,
            "last_erp_sync": NOW.isoformat(),
            "notes": "",
        },
        # IN_TRANSIT — on track
        {
            "po_id": "PO-4421",
            "component_id": "COMP-101",
            "supplier_id": "SUP-18",
            "quantity": 1200,
            "unit_price": 2.5,
            "total_value": 3000.0,
            "status": "IN_TRANSIT",
            "promised_delivery": (NOW + timedelta(days=2)).isoformat(),
            "current_expected_delivery": (NOW + timedelta(days=2)).isoformat(),
            "delay_days": 0,
            "last_erp_sync": NOW.isoformat(),
            "notes": "Tracking: in customs clearance",
        },
        # AT_RISK — may breach
        {
            "po_id": "PO-5530",
            "component_id": "COMP-102",
            "supplier_id": "SUP-55",
            "quantity": 2000,
            "unit_price": 0.8,
            "total_value": 1600.0,
            "status": "AT_RISK",
            "promised_delivery": (NOW + timedelta(days=1)).isoformat(),
            "current_expected_delivery": (NOW + timedelta(days=4)).isoformat(),
            "delay_days": 3,
            "last_erp_sync": NOW.isoformat(),
            "notes": "Supplier confirmed partial shipment only",
        },
        # RECEIVED — completed OK
        {
            "po_id": "PO-3310",
            "component_id": "COMP-105",
            "supplier_id": "SUP-09",
            "quantity": 500,
            "unit_price": 1.2,
            "total_value": 600.0,
            "status": "RECEIVED",
            "promised_delivery": (NOW - timedelta(days=5)).isoformat(),
            "current_expected_delivery": (NOW - timedelta(days=5)).isoformat(),
            "delay_days": 0,
            "last_erp_sync": NOW.isoformat(),
            "notes": "Delivered on time, quality inspection passed",
        },
        # CANCELLED — supplier suspended
        {
            "po_id": "PO-9901",
            "component_id": "COMP-103",
            "supplier_id": "SUP-77",
            "quantity": 1000,
            "unit_price": 12.0,
            "total_value": 12000.0,
            "status": "CANCELLED",
            "promised_delivery": (NOW + timedelta(days=20)).isoformat(),
            "current_expected_delivery": None,
            "delay_days": 0,
            "last_erp_sync": NOW.isoformat(),
            "notes": "Cancelled due to supplier suspension — compliance violation",
        },
        # DELAYED (high severity — over $50k, requires human approval)
        {
            "po_id": "PO-6601",
            "component_id": "COMP-103",
            "supplier_id": "SUP-33",
            "quantity": 5000,
            "unit_price": 12.0,
            "total_value": 60000.0,
            "status": "DELAYED",
            "promised_delivery": (NOW - timedelta(days=7)).isoformat(),
            "current_expected_delivery": (NOW + timedelta(days=14)).isoformat(),
            "delay_days": 21,
            "last_erp_sync": NOW.isoformat(),
            "notes": "Critical delay — production line at risk",
        },
        # AT_RISK (just placed — monitoring needed)
        {
            "po_id": "PO-7720",
            "component_id": "COMP-201",
            "supplier_id": "SUP-88",
            "quantity": 400,
            "unit_price": 48.0,
            "total_value": 19200.0,
            "status": "ORDERED",
            "promised_delivery": (NOW + timedelta(days=10)).isoformat(),
            "current_expected_delivery": (NOW + timedelta(days=10)).isoformat(),
            "delay_days": 0,
            "last_erp_sync": NOW.isoformat(),
            "notes": "New supplier — under evaluation, monitoring required",
        },
        # DELAYED — medium severity, autonomous resolution expected
        {
            "po_id": "PO-2250",
            "component_id": "COMP-101",
            "supplier_id": "SUP-21",
            "quantity": 300,
            "unit_price": 2.5,
            "total_value": 750.0,
            "status": "DELAYED",
            "promised_delivery": (NOW - timedelta(days=2)).isoformat(),
            "current_expected_delivery": (NOW + timedelta(days=3)).isoformat(),
            "delay_days": 5,
            "last_erp_sync": NOW.isoformat(),
            "notes": "Minor delay — supplier confirmed dispatch",
        },
        # IN_TRANSIT — partial shipment
        {
            "po_id": "PO-3398",
            "component_id": "COMP-301",
            "supplier_id": "SUP-18",
            "quantity": 1000,
            "unit_price": 3.2,
            "total_value": 3200.0,
            "status": "IN_TRANSIT",
            "promised_delivery": (NOW + timedelta(days=3)).isoformat(),
            "current_expected_delivery": (NOW + timedelta(days=3)).isoformat(),
            "delay_days": 0,
            "last_erp_sync": NOW.isoformat(),
            "notes": "Partial: 600/1000 units dispatched",
        },
        # OPEN — large order pending confirmation
        {
            "po_id": "PO-8890",
            "component_id": "COMP-105",
            "supplier_id": "SUP-09",
            "quantity": 2000,
            "unit_price": 1.2,
            "total_value": 2400.0,
            "status": "OPEN",
            "promised_delivery": (NOW + timedelta(days=7)).isoformat(),
            "current_expected_delivery": (NOW + timedelta(days=7)).isoformat(),
            "delay_days": 0,
            "last_erp_sync": NOW.isoformat(),
            "notes": "",
        },
        # Anomalous PO — missing supplier in system (for LLM inconsistency detection)
        {
            "po_id": "PO-0001",
            "component_id": "COMP-999",
            "supplier_id": "SUP-UNKNOWN",
            "quantity": 100,
            "unit_price": 0.0,
            "total_value": 0.0,
            "status": "OPEN",
            "promised_delivery": None,
            "current_expected_delivery": None,
            "delay_days": 0,
            "last_erp_sync": None,
            "notes": "AUTO-GENERATED: supplier reference not found in system",
        },
    ]
    for po in purchase_orders:
        db["purchase_orders"].update_one({"po_id": po["po_id"]}, {"$set": po}, upsert=True)

    # ------------------------------------------------------------------
    # 4. PRODUCTION ORDERS  (8 — all priority/status variants)
    # ------------------------------------------------------------------
    production_orders = [
        # Critical — blocked by COMP-103 shortage
        {
            "production_id": "PROD-771",
            "product": "Industrial Controller IC-7",
            "component_id": "COMP-103",
            "quantity": 300,
            "component_per_unit": 2,
            "components_needed": 600,
            "deadline": (NOW + timedelta(days=3)).isoformat(),
            "priority": "CRITICAL",
            "status": "BLOCKED",
            "notes": "Blocked: MCU stock 60, need 600",
        },
        # Hero scenario — high priority, at risk in 4 days
        {
            "production_id": "PROD-882",
            "product": "Widget-X Power Module",
            "component_id": "COMP-104",
            "quantity": 200,
            "component_per_unit": 3,
            "components_needed": 600,
            "deadline": (NOW + timedelta(days=6)).isoformat(),
            "priority": "HIGH",
            "status": "AT_RISK",
            "notes": "Will exhaust current stock in 4 days. PO-7712 delayed.",
        },
        # Medium — manageable buffer
        {
            "production_id": "PROD-990",
            "product": "Widget-Y Control Board",
            "component_id": "COMP-201",
            "quantity": 50,
            "component_per_unit": 1,
            "components_needed": 50,
            "deadline": (NOW + timedelta(days=12)).isoformat(),
            "priority": "MEDIUM",
            "status": "ON_TRACK",
            "notes": "On track; stock sufficient for 4 days, PO-8813 due in 5 days",
        },
        # Low priority — plenty of buffer
        {
            "production_id": "PROD-330",
            "product": "Passive Filter Unit",
            "component_id": "COMP-105",
            "quantity": 1000,
            "component_per_unit": 3,
            "components_needed": 3000,
            "deadline": (NOW + timedelta(days=45)).isoformat(),
            "priority": "LOW",
            "status": "ON_TRACK",
            "notes": "Plenty of stock; no action needed",
        },
        # At risk — capacitor supply low
        {
            "production_id": "PROD-445",
            "product": "Power Converter PC-10",
            "component_id": "COMP-102",
            "quantity": 100,
            "component_per_unit": 4,
            "components_needed": 400,
            "deadline": (NOW + timedelta(days=2)).isoformat(),
            "priority": "HIGH",
            "status": "AT_RISK",
            "notes": "Capacitor stock at 420, PO-5530 at risk — production may pause",
        },
        # Normal — all clear
        {
            "production_id": "PROD-560",
            "product": "Signal Amplifier SA-5",
            "component_id": "COMP-101",
            "quantity": 400,
            "component_per_unit": 5,
            "components_needed": 2000,
            "deadline": (NOW + timedelta(days=20)).isoformat(),
            "priority": "MEDIUM",
            "status": "ON_TRACK",
            "notes": "Stock sufficient; PO-4421 in transit",
        },
        # Completed recently
        {
            "production_id": "PROD-620",
            "product": "PCB Assembly Board V2",
            "component_id": "COMP-301",
            "quantity": 500,
            "component_per_unit": 2,
            "components_needed": 1000,
            "deadline": (NOW - timedelta(days=2)).isoformat(),
            "priority": "HIGH",
            "status": "COMPLETED",
            "notes": "Completed on schedule",
        },
        # Waiting on expedite approval
        {
            "production_id": "PROD-710",
            "product": "Servo Driver Module",
            "component_id": "COMP-103",
            "quantity": 150,
            "component_per_unit": 1,
            "components_needed": 150,
            "deadline": (NOW + timedelta(days=5)).isoformat(),
            "priority": "HIGH",
            "status": "WAITING_PARTS",
            "notes": "Waiting on expedite order from SUP-09 for COMP-103",
        },
    ]
    for p in production_orders:
        db["production_orders"].update_one({"production_id": p["production_id"]}, {"$set": p}, upsert=True)

    # ------------------------------------------------------------------
    # 5. INCIDENTS  (6 — covering all agent state machine paths)
    # ------------------------------------------------------------------
    incidents = [
        # DETECTED — not yet picked up by agent
        {
            "incident_id": "INC-001",
            "type": "SUPPLIER_DELAY",
            "severity": "HIGH",
            "affected_component": "COMP-104",
            "affected_po": "PO-7712",
            "supplier_id": "SUP-21",
            "status": "DETECTED",
            "created_at": (NOW - timedelta(hours=2)).isoformat(),
            "source": "erp_event",
            "delay_days": 11,
        },
        # INVESTIGATING — agent triggered, Groq reasoning in progress
        {
            "incident_id": "INC-002",
            "type": "DELIVERY_BREACH",
            "severity": "CRITICAL",
            "affected_component": "COMP-103",
            "affected_po": "PO-6601",
            "supplier_id": "SUP-33",
            "status": "INVESTIGATING",
            "created_at": (NOW - timedelta(hours=5)).isoformat(),
            "source": "delivery_monitor",
            "delay_days": 21,
        },
        # WAITING_APPROVAL — requires human approval (>$50k)
        {
            "incident_id": "INC-003",
            "type": "SUPPLIER_DELAY",
            "severity": "HIGH",
            "affected_component": "COMP-103",
            "affected_po": "PO-6601",
            "supplier_id": "SUP-33",
            "status": "WAITING_APPROVAL",
            "created_at": (NOW - timedelta(hours=8)).isoformat(),
            "source": "erp_event",
            "delay_days": 21,
            "estimated_recovery_cost": 72000.0,
            "plan_id": "PLAN-003",
        },
        # RESOLVED — autonomous recovery executed
        {
            "incident_id": "INC-004",
            "type": "DELIVERY_BREACH",
            "severity": "MEDIUM",
            "affected_component": "COMP-101",
            "affected_po": "PO-2250",
            "supplier_id": "SUP-21",
            "status": "RESOLVED",
            "created_at": (NOW - timedelta(days=2)).isoformat(),
            "resolved_at": (NOW - timedelta(hours=12)).isoformat(),
            "source": "delivery_monitor",
            "delay_days": 5,
            "resolution": "Alternative supplier SUP-18 dispatched 300 units. On-time.",
        },
        # REPLANNING — human rejected, agent replanning
        {
            "incident_id": "INC-005",
            "type": "SUPPLIER_DELAY",
            "severity": "MEDIUM",
            "affected_component": "COMP-102",
            "affected_po": "PO-5530",
            "supplier_id": "SUP-55",
            "status": "REPLANNING",
            "created_at": (NOW - timedelta(hours=3)).isoformat(),
            "source": "erp_event",
            "delay_days": 3,
            "rejection_reason": "Proposed recovery cost $18,000 approved limit $15,000 — need cheaper option",
        },
        # DATA_INCONSISTENCY — flagged by LLM during analysis
        {
            "incident_id": "INC-006",
            "type": "DATA_INCONSISTENCY",
            "severity": "LOW",
            "affected_component": "COMP-999",
            "affected_po": "PO-0001",
            "supplier_id": "SUP-UNKNOWN",
            "status": "DETECTED",
            "created_at": (NOW - timedelta(minutes=30)).isoformat(),
            "source": "groq_agent",
            "notes": "LLM detected: supplier SUP-UNKNOWN not registered, PO has no delivery date, component has zero daily usage",
        },
    ]
    for inc in incidents:
        db["incidents"].update_one({"incident_id": inc["incident_id"]}, {"$set": inc}, upsert=True)

    # ------------------------------------------------------------------
    # 6. RFQ RESPONSES  (5 — accepted, rejected, expedite, missing, partial)
    # ------------------------------------------------------------------
    rfq_responses = [
        {
            "rfq_id": "RFQ-001",
            "supplier_id": "SUP-18",
            "component_id": "COMP-104",
            "quantity": 600,
            "unit_price": 155.0,
            "delivery_days": 7,
            "total_cost": 93000.0,
            "expedite_available": False,
            "expedite_fee": None,
            "accepted": True,
            "received_at": (NOW - timedelta(hours=1)).isoformat(),
        },
        {
            "rfq_id": "RFQ-002",
            "supplier_id": "SUP-42",
            "component_id": "COMP-104",
            "quantity": 600,
            "unit_price": 165.0,
            "delivery_days": 3,
            "total_cost": 99000.0,
            "expedite_available": True,
            "expedite_fee": 4500.0,
            "accepted": None,  # pending decision
            "received_at": (NOW - timedelta(minutes=45)).isoformat(),
        },
        {
            "rfq_id": "RFQ-003",
            "supplier_id": "SUP-55",
            "component_id": "COMP-104",
            "quantity": 600,
            "unit_price": 125.0,
            "delivery_days": 21,
            "total_cost": 75000.0,
            "expedite_available": False,
            "expedite_fee": None,
            "accepted": False,  # rejected — lead time too long
            "rejection_reason": "21 days exceeds required delivery window of 8 days",
            "received_at": (NOW - timedelta(hours=2)).isoformat(),
        },
        {
            "rfq_id": "RFQ-004",
            "supplier_id": "SUP-09",
            "component_id": "COMP-103",
            "quantity": 5000,
            "unit_price": 13.5,
            "delivery_days": 5,
            "total_cost": 67500.0,
            "expedite_available": True,
            "expedite_fee": 2000.0,
            "accepted": None,
            "received_at": (NOW - timedelta(hours=3)).isoformat(),
        },
        # Partial/incomplete response — for error testing
        {
            "rfq_id": "RFQ-005",
            "supplier_id": "SUP-88",
            "component_id": "COMP-201",
            "quantity": None,  # missing quantity
            "unit_price": None,  # missing price
            "delivery_days": None,
            "total_cost": None,
            "expedite_available": False,
            "expedite_fee": None,
            "accepted": None,
            "notes": "Supplier acknowledged RFQ but could not provide quote",
            "received_at": NOW.isoformat(),
        },
    ]
    for rfq in rfq_responses:
        db["rfq_responses"].update_one(
            {"rfq_id": rfq["rfq_id"], "supplier_id": rfq["supplier_id"]},
            {"$set": rfq},
            upsert=True,
        )

    # ------------------------------------------------------------------
    # 7. RECOVERY PLANS  (3 — autonomous, approval-required, rejected)
    # ------------------------------------------------------------------
    recovery_plans = [
        {
            "plan_id": "PLAN-001",
            "incident_id": "INC-001",
            "component_id": "COMP-104",
            "created_at": (NOW - timedelta(hours=1)).isoformat(),
            "requires_human_approval": False,
            "approval_threshold_usd": 50000.0,
            "recommended_option_id": "A",
            "recommendation_reason": "Option A uses SUP-18 with 91% reliability and 7-day delivery within budget.",
            "options": [
                {
                    "option_id": "A",
                    "allocations": [{"supplier_id": "SUP-18", "quantity": 600, "unit_price": 155.0, "delivery_days": 7}],
                    "total_cost": 93000.0,
                    "max_delivery_days": 7,
                    "constraints_satisfied": True,
                    "rejection_reason": None,
                },
                {
                    "option_id": "B",
                    "allocations": [
                        {"supplier_id": "SUP-42", "quantity": 300, "unit_price": 165.0, "delivery_days": 3},
                        {"supplier_id": "SUP-18", "quantity": 300, "unit_price": 155.0, "delivery_days": 7},
                    ],
                    "total_cost": 96000.0,
                    "max_delivery_days": 7,
                    "constraints_satisfied": True,
                    "rejection_reason": None,
                },
            ],
        },
        {
            "plan_id": "PLAN-002",
            "incident_id": "INC-004",
            "component_id": "COMP-101",
            "created_at": (NOW - timedelta(days=2, hours=1)).isoformat(),
            "requires_human_approval": False,
            "approval_threshold_usd": 50000.0,
            "recommended_option_id": "A",
            "recommendation_reason": "Low cost, fast alternative from SUP-18. Autonomous approval granted.",
            "status": "EXECUTED",
            "executed_at": (NOW - timedelta(hours=12)).isoformat(),
            "options": [
                {
                    "option_id": "A",
                    "allocations": [{"supplier_id": "SUP-18", "quantity": 300, "unit_price": 2.7, "delivery_days": 5}],
                    "total_cost": 810.0,
                    "max_delivery_days": 5,
                    "constraints_satisfied": True,
                    "rejection_reason": None,
                },
            ],
        },
        {
            "plan_id": "PLAN-003",
            "incident_id": "INC-003",
            "component_id": "COMP-103",
            "created_at": (NOW - timedelta(hours=6)).isoformat(),
            "requires_human_approval": True,
            "approval_threshold_usd": 50000.0,
            "estimated_cost": 72000.0,
            "recommended_option_id": "A",
            "recommendation_reason": "Only option that meets quality and delivery requirements. Exceeds $50k approval threshold.",
            "status": "AWAITING_APPROVAL",
            "options": [
                {
                    "option_id": "A",
                    "allocations": [{"supplier_id": "SUP-09", "quantity": 5000, "unit_price": 13.5, "delivery_days": 5}],
                    "total_cost": 72000.0,
                    "max_delivery_days": 5,
                    "constraints_satisfied": True,
                    "rejection_reason": None,
                },
                {
                    "option_id": "B",
                    "allocations": [{"supplier_id": "SUP-55", "quantity": 5000, "unit_price": 10.0, "delivery_days": 30}],
                    "total_cost": 50000.0,
                    "max_delivery_days": 30,
                    "constraints_satisfied": False,
                    "rejection_reason": "Delivery window 30 days exceeds required 5 days",
                },
            ],
        },
    ]
    for plan in recovery_plans:
        db["recovery_plans"].update_one({"plan_id": plan["plan_id"]}, {"$set": plan}, upsert=True)

    # ------------------------------------------------------------------
    # 8. SEED AUDIT LOGS  (pre-populated for dashboard demo)
    # ------------------------------------------------------------------
    audit_logs = [
        {
            "event_id": "AUD-SEED-001",
            "timestamp": (NOW - timedelta(hours=8)).isoformat(),
            "source": "n8n",
            "workflow": "ERP_EVENT_SYNC",
            "event_type": "ERP_SYNC_COMPLETED",
            "incident_id": "INC-003",
            "entity_type": "PURCHASE_ORDER",
            "entity_id": "PO-6601",
            "action": "SYNC_ERP_EVENT",
            "status": "SUCCESS",
            "tool": "SYNC_ERP_EVENT",
            "result": "SUCCESS",
            "decision": "ERP_SYNC_COMPLETED",
            "reason": "n8n workflow: ERP_EVENT_SYNC",
            "retry_count": 0,
            "correlation_id": "CORR-ERP-001",
            "input": {"event_type": "STATUS_UPDATE", "status": "DELAYED"},
            "output": {"incident_id": "INC-003", "agent_trigger_required": True},
            "ingested_at": (NOW - timedelta(hours=8)).isoformat(),
        },
        {
            "event_id": "AUD-SEED-002",
            "timestamp": (NOW - timedelta(hours=7, minutes=55)).isoformat(),
            "source": "n8n",
            "workflow": "GROQ_AI_AGENT",
            "event_type": "AUTONOMOUS_APPROVAL",
            "incident_id": "INC-004",
            "entity_type": "INCIDENT",
            "entity_id": "INC-004",
            "action": "GROQ_REASONING_COMPLETE",
            "status": "SUCCESS",
            "tool": "GROQ_REASONING_COMPLETE",
            "result": "SUCCESS",
            "decision": "APPROVE_AUTONOMOUS",
            "reason": "Stock sufficient; cost $810 well below $50k threshold",
            "retry_count": 0,
            "correlation_id": "CORR-AGT-002",
            "input": {"incident_id": "INC-004"},
            "output": {"decision": "APPROVE_AUTONOMOUS", "recommended_action": "Place order with SUP-18"},
            "ingested_at": (NOW - timedelta(hours=7, minutes=55)).isoformat(),
        },
        {
            "event_id": "AUD-SEED-003",
            "timestamp": (NOW - timedelta(hours=7)).isoformat(),
            "source": "n8n",
            "workflow": "GROQ_AI_AGENT",
            "event_type": "HUMAN_APPROVAL_REQUIRED",
            "incident_id": "INC-003",
            "entity_type": "INCIDENT",
            "entity_id": "INC-003",
            "action": "GROQ_REASONING_COMPLETE",
            "status": "SUCCESS",
            "tool": "GROQ_REASONING_COMPLETE",
            "result": "ESCALATED",
            "decision": "NEEDS_HUMAN_APPROVAL",
            "reason": "Estimated recovery cost $72,000 exceeds $50,000 autonomous limit",
            "retry_count": 0,
            "correlation_id": "CORR-AGT-003",
            "input": {"incident_id": "INC-003"},
            "output": {"decision": "NEEDS_HUMAN_APPROVAL", "estimated_cost": 72000.0},
            "ingested_at": (NOW - timedelta(hours=7)).isoformat(),
        },
        {
            "event_id": "AUD-SEED-004",
            "timestamp": (NOW - timedelta(hours=6, minutes=30)).isoformat(),
            "source": "n8n",
            "workflow": "HUMAN_APPROVAL_ORCHESTRATOR",
            "event_type": "APPROVAL_REQUEST_SENT",
            "incident_id": "INC-003",
            "entity_type": "RECOVERY_PLAN",
            "entity_id": "PLAN-003",
            "action": "SEND_APPROVAL_EMAIL",
            "status": "SUCCESS",
            "tool": "SEND_APPROVAL_EMAIL",
            "result": "SUCCESS",
            "decision": "APPROVAL_REQUEST_SENT",
            "reason": "Email dispatched to procurement@yourcompany.com",
            "retry_count": 0,
            "correlation_id": "CORR-APR-003",
            "input": {"estimated_cost": 72000.0, "risk": "HIGH"},
            "output": {"channel": "email"},
            "ingested_at": (NOW - timedelta(hours=6, minutes=30)).isoformat(),
        },
        {
            "event_id": "AUD-SEED-005",
            "timestamp": (NOW - timedelta(hours=3)).isoformat(),
            "source": "n8n",
            "workflow": "SUPPLIER_RESPONSE_SYNC",
            "event_type": "SUPPLIER_RESPONSE_RECEIVED",
            "incident_id": "INC-001",
            "entity_type": "RFQ",
            "entity_id": "RFQ-001",
            "action": "SYNC_SUPPLIER_RESPONSE",
            "status": "SUCCESS",
            "tool": "SYNC_SUPPLIER_RESPONSE",
            "result": "SUCCESS",
            "decision": "SUPPLIER_RESPONSE_RECEIVED",
            "reason": "n8n workflow: SUPPLIER_RESPONSE_SYNC",
            "retry_count": 0,
            "correlation_id": "CORR-SUP-001",
            "input": {"supplier_id": "SUP-18", "component_id": "COMP-104", "delivery_days": 7},
            "output": {"rfq_id": "RFQ-001", "accepted": True},
            "ingested_at": (NOW - timedelta(hours=3)).isoformat(),
        },
        {
            "event_id": "AUD-SEED-006",
            "timestamp": (NOW - timedelta(hours=1)).isoformat(),
            "source": "n8n",
            "workflow": "DELIVERY_COMMITMENT_MONITOR",
            "event_type": "DELIVERY_COMMITMENT_BREACH",
            "incident_id": "INC-002",
            "entity_type": "PURCHASE_ORDER",
            "entity_id": "PO-6601",
            "action": "TRIGGER_GROQ_AGENT",
            "status": "SUCCESS",
            "tool": "TRIGGER_GROQ_AGENT",
            "result": "SUCCESS",
            "decision": "DELIVERY_COMMITMENT_BREACH",
            "reason": "n8n workflow: DELIVERY_COMMITMENT_MONITOR",
            "retry_count": 0,
            "correlation_id": "CORR-MON-002",
            "input": {"promised_date": (NOW - timedelta(days=7)).isoformat(), "delay_days": 21},
            "output": {"agent_triggered": True, "incident_id": "INC-002"},
            "ingested_at": (NOW - timedelta(hours=1)).isoformat(),
        },
        {
            "event_id": "AUD-SEED-007",
            "timestamp": (NOW - timedelta(minutes=30)).isoformat(),
            "source": "n8n",
            "workflow": "GROQ_AI_AGENT",
            "event_type": "DATA_INCONSISTENCY_DETECTED",
            "incident_id": "INC-006",
            "entity_type": "PURCHASE_ORDER",
            "entity_id": "PO-0001",
            "action": "GROQ_INCONSISTENCY_DETECTION",
            "status": "SUCCESS",
            "tool": "GROQ_INCONSISTENCY_DETECTION",
            "result": "ESCALATED",
            "decision": "DATA_INCONSISTENCY",
            "reason": "Supplier SUP-UNKNOWN not in system; missing delivery dates; zero unit price",
            "retry_count": 0,
            "correlation_id": "CORR-AGT-006",
            "input": {"incident_id": "INC-006"},
            "output": {"inconsistencies": ["unknown_supplier", "missing_delivery_date", "zero_unit_price"]},
            "ingested_at": (NOW - timedelta(minutes=30)).isoformat(),
        },
    ]
    for log in audit_logs:
        db["audit_logs"].update_one({"event_id": log["event_id"]}, {"$set": log}, upsert=True)

    # ------------------------------------------------------------------
    # 9. ERP LOGS  (tracking all ERP updates made by the agent)
    # ------------------------------------------------------------------
    erp_logs = [
        {
            "log_id": "ERP-LOG-001",
            "timestamp": (NOW - timedelta(hours=12)).isoformat(),
            "action": "PO_CREATED",
            "entity_type": "PURCHASE_ORDER",
            "entity_id": "PO-4421",
            "incident_id": "INC-004",
            "performed_by": "n8n:GROQ_AI_AGENT",
            "details": {"supplier_id": "SUP-18", "quantity": 300, "unit_price": 2.7},
            "status": "SUCCESS",
            "correlation_id": "CORR-AGT-002",
        },
        {
            "log_id": "ERP-LOG-002",
            "timestamp": (NOW - timedelta(hours=11)).isoformat(),
            "action": "INCIDENT_STATUS_UPDATE",
            "entity_type": "INCIDENT",
            "entity_id": "INC-004",
            "incident_id": "INC-004",
            "performed_by": "n8n:GROQ_AI_AGENT",
            "details": {"old_status": "INVESTIGATING", "new_status": "RESOLVED"},
            "status": "SUCCESS",
            "correlation_id": "CORR-AGT-002",
        },
    ]
    for log in erp_logs:
        db["erp_logs"].update_one({"log_id": log["log_id"]}, {"$set": log}, upsert=True)

    print("✅ Database seeded with comprehensive data successfully.")
    print(f"   Inventory:         {len(inventory_data)} items")
    print(f"   Suppliers:         {len(suppliers)} suppliers")
    print(f"   Purchase Orders:   {len(purchase_orders)} orders")
    print(f"   Production Orders: {len(production_orders)} orders")
    print(f"   Incidents:         {len(incidents)} incidents")
    print(f"   RFQ Responses:     {len(rfq_responses)} responses")
    print(f"   Recovery Plans:    {len(recovery_plans)} plans")
    print(f"   Audit Logs:        {len(audit_logs)} entries (pre-seeded)")
    print(f"   ERP Logs:          {len(erp_logs)} entries (pre-seeded)")
