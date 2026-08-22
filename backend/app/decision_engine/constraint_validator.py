"""
app/decision_engine/constraint_validator.py
Owner: Developer 3 (Decision Engine)

REQUIRED (PS Core Capability #3): "Enforce strict constraints (e.g., maximum budget
overhead, hazardous material transport rules, customer priority tiers)."

RECEIVES: a candidate RecoveryPlanOption (schemas/recovery_plan.py) + business limits
DELIVERS: pass/fail + reason, consumed by recovery_planner.py to accept/reject options
          and shown verbatim in the frontend as e.g. "Rejected: quality certification failed"
"""

from dataclasses import dataclass


@dataclass
class ConstraintCheckResult:
    passed: bool
    reason: str = ""


def check_budget(total_cost: float, max_budget: float) -> ConstraintCheckResult:
    if total_cost > max_budget:
        return ConstraintCheckResult(False, f"Cost ${total_cost:,.0f} exceeds budget ${max_budget:,.0f}")
    return ConstraintCheckResult(True)


def check_quality_certification(supplier_certifications: str, required_cert: str) -> ConstraintCheckResult:
    certs = [c.strip() for c in (supplier_certifications or "").split(",")]
    if required_cert not in certs:
        return ConstraintCheckResult(False, f"Required quality certification missing: {required_cert}")
    return ConstraintCheckResult(True)


def check_delivery_deadline(delivery_days: int, required_by_days: int) -> ConstraintCheckResult:
    if delivery_days > required_by_days:
        return ConstraintCheckResult(
            False, f"Delivery in {delivery_days}d misses required {required_by_days}d deadline"
        )
    return ConstraintCheckResult(True)


def check_moq(quantity: int, moq: int) -> ConstraintCheckResult:
    if quantity < moq:
        return ConstraintCheckResult(False, f"Quantity {quantity} is below supplier MOQ {moq}")
    return ConstraintCheckResult(True)


# TODO (Dev3): add check_hazmat_rules() if the hero scenario ends up needing it
# (PS explicitly mentions hazardous material transport rules — confirm with team
# whether the hero scenario (COMP-104 chain) requires this; if not, mark OPTIONAL).
