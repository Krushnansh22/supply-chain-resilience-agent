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

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.simulator.disruption_injector import inject_scenario

router = APIRouter()


class InjectRequest(BaseModel):
    scenario: str  # "SUPPLIER_DELAY" | "STALE_INVENTORY" | "SUPPLIER_LIE" | "QUALITY_FAILURE" | "BUDGET_OVERRUN"


@router.post("/inject")
def inject(req: InjectRequest, db: Session = Depends(get_db)):
    """POST /simulator/inject {"scenario": "SUPPLIER_DELAY"} -> creates a new incident."""
    incident = inject_scenario(req.scenario, db)
    return incident
