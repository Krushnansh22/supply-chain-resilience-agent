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
from sqlalchemy.orm import Session

from app.models.incidents import Incident

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


def inject_scenario(scenario: str, db: Session) -> Incident:
    """
    TODO (Dev2/Dev3): validate `scenario` against SCENARIO_DEFAULTS, raise a clean
    422 if unknown (handle in the router, not here). Extend SCENARIO_DEFAULTS with
    more/other components once seed_data.py has more than the hero chain.
    """
    defaults = SCENARIO_DEFAULTS.get(scenario, SCENARIO_DEFAULTS["SUPPLIER_DELAY"])
    incident = Incident(
        incident_id=f"INC-{uuid.uuid4().hex[:6].upper()}",
        status="DETECTED",
        **defaults,
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident
