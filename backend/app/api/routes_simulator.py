"""
app/api/routes_simulator.py
Owner: Developer 2 (Backend / Simulation)

Powers the "Disruption Simulator" buttons (team doc Section 18):
[Inject Supplier Delay] [Inject Stale Inventory] [Inject Supplier Lie]
[Inject Quality Failure] [Inject Budget Overrun] [Inject New Disruption]

RECEIVES: button clicks from frontend/src/components/simulator/DisruptionSimulatorPanel.jsx
DELIVERS: creates a row in `incidents` (and any supporting fake data, e.g. a supplier
          message that contradicts tracking for the "lie" scenario) via
          simulator/disruption_injector.py
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from pymongo.database import Database

from app.mongo_database import get_mongo_db
from app.schemas.common import IncidentOut
from app.simulator.disruption_injector import inject_scenario, SCENARIO_DEFAULTS

router = APIRouter()

VALID_SCENARIOS = set(SCENARIO_DEFAULTS.keys())


class InjectRequest(BaseModel):
    scenario: str  # "SUPPLIER_DELAY" | "STALE_INVENTORY" | "SUPPLIER_LIE" | "QUALITY_FAILURE" | "BUDGET_OVERRUN"


@router.post("/inject", response_model=IncidentOut)
def inject(req: InjectRequest, db: Database = Depends(get_mongo_db)):
    """POST /simulator/inject {"scenario": "SUPPLIER_DELAY"} -> creates a new incident.
    Returns 422 if scenario name is unknown.
    """
    if req.scenario not in VALID_SCENARIOS:
        raise HTTPException(
            status_code=422,
            detail=f"Unknown scenario '{req.scenario}'. Valid options: {sorted(VALID_SCENARIOS)}",
        )
    incident = inject_scenario(req.scenario, db)
    return IncidentOut.model_validate(incident)
