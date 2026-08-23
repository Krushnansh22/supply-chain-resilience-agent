"""
app/simulator/disruption_injector.py
Owner: Developer 2 (Backend / Simulation)

Implements the "Disruption Simulator" buttons (team doc Section 18) by writing a
new row into `incidents` and applying direct data mutations to MongoDB.
"""

import uuid
from datetime import datetime, timedelta, timezone
from pymongo.database import Database

SCENARIO_DEFAULTS = {
    "NEGATIVE_STOCK": {
        "type": "NEGATIVE_STOCK",
        "severity": "CRITICAL",
        "affected_component": "COMP-104",
        "affected_po": None,
        "notes": "Corrupted inventory audit: usable stock recorded as -150 units. Physical verification required."
    },
    "MISSING_STOCK": {
        "type": "MISSING_STOCK_DATA",
        "severity": "HIGH",
        "affected_component": "COMP-102",
        "affected_po": None,
        "notes": "Missing stock telemetry: usable stock record is null. Manual count required."
    },
    "SUPPLIER_DELAY": {
        "type": "SUPPLIER_DELAY",
        "severity": "CRITICAL",
        "affected_component": "COMP-104",
        "affected_po": "PO-7712",
        "notes": "Supplier delayed PO-7712 by 14 days due to logistics bottleneck."
    },
    "STALE_INVENTORY": {
        "type": "STALE_INVENTORY",
        "severity": "MEDIUM",
        "affected_component": "COMP-104",
        "affected_po": None,
        "notes": "Cycle count expired for batch. Quarantine inspection needed."
    },
    "SUPPLIER_LIE": {
        "type": "SUPPLIER_LIE",
        "severity": "HIGH",
        "affected_component": "COMP-104",
        "affected_po": "PO-7712",
        "notes": "Supplier claims shipment dispatched, but carrier reports NO_PICKUP_SCAN."
    },
    "QUALITY_FAILURE": {
        "type": "QUALITY_FAILURE",
        "severity": "HIGH",
        "affected_component": "COMP-104",
        "affected_po": "PO-7712",
        "notes": "Quality inspection rejected incoming batch. Alternative sourcing required."
    },
    "AUTONOMOUS_RESOLVE": {
        "type": "SUPPLIER_DELAY",
        "severity": "MEDIUM",
        "affected_component": "COMP-101",
        "affected_po": "PO-7711",
        "notes": "Low-impact transit delay on Resistor 10k. Agent autonomously re-routes order to backup vendor within $18,000 budget."
    },
    "BUDGET_OVERRUN": {
        "type": "BUDGET_OVERRUN",
        "severity": "CRITICAL",
        "affected_component": "COMP-104",
        "affected_po": "PO-7712",
        "notes": "Expedited recovery option exceeds $50,000 threshold ($75,000 estimated)."
    },
}


def inject_scenario(scenario: str, db: Database) -> dict:
    """
    Creates a new Incident row for the given scenario and applies DB disruptions.
    - NEGATIVE_STOCK: Mutates usable_stock and current_stock to -150 in MongoDB.
    - MISSING_STOCK: Sets usable_stock to None in MongoDB.
    - SUPPLIER_LIE: Registers contradiction with supplier simulator.
    """
    defaults = SCENARIO_DEFAULTS[scenario]
    incident_id = f"INC-{uuid.uuid4().hex[:6].upper()}"
    incident = {
        "incident_id": incident_id,
        "status": "DETECTED",
        "created_at": datetime.now(timezone.utc),
        **defaults,
    }
    db["incidents"].insert_one(incident)

    # Apply actual disruptions into the database so the environment scan & UI observe them
    comp_id = defaults.get("affected_component")
    if scenario == "NEGATIVE_STOCK" and comp_id:
        db["inventory"].update_one(
            {"component_id": comp_id},
            {"$set": {"usable_stock": -150, "current_stock": -150, "last_cycle_count": datetime.now(timezone.utc).isoformat()}}
        )
    elif scenario == "MISSING_STOCK" and comp_id:
        db["inventory"].update_one(
            {"component_id": comp_id},
            {"$set": {"usable_stock": None, "current_stock": None, "last_cycle_count": datetime.now(timezone.utc).isoformat()}}
        )
    elif scenario == "SUPPLIER_DELAY" and defaults.get("affected_po"):
        # Make the PO overdue/delayed in the DB
        db["purchase_orders"].update_one(
            {"po_id": defaults["affected_po"]},
            {"$set": {"expected_delivery": datetime.now(timezone.utc) - timedelta(days=2), "status": "DELAYED"}}
        )

    # Register lie scenario so simulator returns contradicting data
    if scenario == "SUPPLIER_LIE" and incident.get("affected_po"):
        from app.simulator.supplier_simulator import register_supplier_lie
        register_supplier_lie(incident["affected_po"])

    return incident
