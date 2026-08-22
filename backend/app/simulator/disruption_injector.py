"""
app/simulator/disruption_injector.py
Owner: Developer 2 (Backend / Simulation)

Implements the "Disruption Simulator" buttons (team doc Section 18) by writing a
new row into `incidents`. This is the entry point that starts the whole agent
pipeline for a demo.

RECEIVES: a scenario name string from api/routes_simulator.py
DELIVERS: a new Incident row, status=DETECTED, ready for the agent loop to pick up
"""

import uuid
from datetime import datetime
from pymongo.database import Database

SCENARIO_DEFAULTS = {
    "SUPPLIER_DELAY": {"type": "SUPPLIER_DELAY", "severity": "CRITICAL",
                        "affected_component": "COMP-104", "affected_po": "PO-7712"},
    "STALE_INVENTORY": {"type": "STALE_INVENTORY", "severity": "MEDIUM",
                         "affected_component": "COMP-104", "affected_po": None},
    "SUPPLIER_LIE": {"type": "SUPPLIER_LIE", "severity": "HIGH",
                      "affected_component": "COMP-104", "affected_po": "PO-7712"},
    "QUALITY_FAILURE": {"type": "QUALITY_FAILURE", "severity": "HIGH",
                         "affected_component": "COMP-104", "affected_po": "PO-7712"},
    "BUDGET_OVERRUN": {"type": "BUDGET_OVERRUN", "severity": "CRITICAL",
                        "affected_component": "COMP-104", "affected_po": "PO-7712"},
}


def inject_scenario(scenario: str, db: Database) -> dict:
    """
    Creates a new Incident row for the given scenario.
    Raises KeyError if scenario is unknown (caller in routes_simulator.py validates first).
    For SUPPLIER_LIE: registers the affected PO so supplier_simulator returns
    contradicting data (dispatch claim vs NO_PICKUP_SCAN tracking status).
    """
    defaults = SCENARIO_DEFAULTS[scenario]
    incident = {"incident_id": f"INC-{uuid.uuid4().hex[:6].upper()}", "status": "DETECTED", "created_at": datetime.utcnow(), **defaults}
    db["incidents"].insert_one(incident)

    # Register lie scenario so simulator returns contradicting data
    if scenario == "SUPPLIER_LIE" and incident["affected_po"]:
        from app.simulator.supplier_simulator import register_supplier_lie
        register_supplier_lie(incident["affected_po"])

    return incident
