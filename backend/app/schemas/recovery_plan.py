"""
app/schemas/recovery_plan.py
Owner: Developer 3 (Decision Engine) defines the shape; Developer 1 (Agent) and
Developer 4 (Frontend) consume it as-is.

RECEIVES: built by decision_engine/recovery_planner.py from RFQ + constraint results
DELIVERS:
  - to Developer 1's agent loop, which decides EXECUTE vs ESCALATE
  - to Developer 4's Recovery Plan UI (docs Section 15) and Approval UI (Section 16)
"""

from pydantic import BaseModel
from typing import List, Optional


class SupplierAllocation(BaseModel):
    supplier_id: str
    quantity: int
    unit_price: float
    delivery_days: int


class RecoveryPlanOption(BaseModel):
    option_id: str                     # "A", "B", "C" ...
    allocations: List[SupplierAllocation]
    total_cost: float
    max_delivery_days: int
    constraints_satisfied: bool
    rejection_reason: Optional[str] = None  # e.g. "quality certification failed"


class RecoveryPlan(BaseModel):
    incident_id: str
    options: List[RecoveryPlanOption]
    recommended_option_id: str
    recommendation_reason: str
    requires_human_approval: bool
    approval_threshold_usd: float
