"""
app/decision_engine/recovery_planner.py
Owner: Developer 3 (Decision Engine)

REQUIRED (PS Core Capability #2 + team doc Section 9: split sourcing support).
Builds one or more RecoveryPlanOption objects from available RFQs, scores/filters
them via supplier_scoring.py + constraint_validator.py, and recommends the best one.

RECEIVES: list of RFQ rows (from tools/rfq_tools.request_rfq results), shortfall
          quantity (from inventory_calc.py), production deadline, budget limit
DELIVERS: schemas/recovery_plan.RecoveryPlan, consumed by:
  - agent/agent_loop.py (decides EXECUTE vs ESCALATE using requires_human_approval)
  - api/routes_agent.py (GET /agent/plan/{incident_id})
  - frontend Recovery Plan UI + Approval UI
"""

from app.schemas.recovery_plan import RecoveryPlan, RecoveryPlanOption, SupplierAllocation
from app.decision_engine.supplier_scoring import score_supplier
from app.decision_engine import constraint_validator as cv
from app.config import settings


def build_recovery_plan(
    incident_id: str,
    required_quantity: int,
    rfq_candidates: list[dict],   # each dict: supplier_id, unit_price, delivery_days, certifications, moq
    required_cert: str | None,
    required_by_days: int,
) -> RecoveryPlan:
    """
    TODO (Dev3): this is a skeleton. Implement:
      1. Single-supplier options for each RFQ candidate that can cover full quantity alone.
      2. At least one split-sourcing option (team doc Section 9, e.g. 400+200) when no
         single supplier can fully/optimally cover the need.
      3. Run each option through constraint_validator checks; mark constraints_satisfied
         and rejection_reason accordingly (rejected options should still be returned,
         not silently dropped — judges want to see rejected alternatives, see docs
         Section 15 "OPTION C - Rejected").
      4. Pick the recommended_option_id = best constraint-passing option by score_supplier.
      5. Set requires_human_approval = total_cost > settings.AUTONOMOUS_APPROVAL_LIMIT_USD
         (REQUIRED by PS: >$50,000 impact threshold).
    """
    options: list[RecoveryPlanOption] = []

    # --- Placeholder: naive single-supplier-only logic, REPLACE with real algorithm ---
    for candidate in rfq_candidates:
        total_cost = candidate["unit_price"] * required_quantity
        allocation = SupplierAllocation(
            supplier_id=candidate["supplier_id"],
            quantity=required_quantity,
            unit_price=candidate["unit_price"],
            delivery_days=candidate["delivery_days"],
        )

        checks = [cv.check_budget(total_cost, max_budget=float("inf"))]
        if required_cert:
            checks.append(cv.check_quality_certification(candidate.get("certifications", ""), required_cert))
        checks.append(cv.check_delivery_deadline(candidate["delivery_days"], required_by_days))

        failed = next((c for c in checks if not c.passed), None)

        options.append(
            RecoveryPlanOption(
                option_id=chr(ord("A") + len(options)),
                allocations=[allocation],
                total_cost=total_cost,
                max_delivery_days=candidate["delivery_days"],
                constraints_satisfied=failed is None,
                rejection_reason=failed.reason if failed else None,
            )
        )

    valid_options = [o for o in options if o.constraints_satisfied]
    recommended = min(valid_options, key=lambda o: o.total_cost) if valid_options else None

    return RecoveryPlan(
        incident_id=incident_id,
        options=options,
        recommended_option_id=recommended.option_id if recommended else "",
        recommendation_reason=(
            "Lowest-cost option that satisfies all constraints."
            if recommended else "No option currently satisfies all constraints — replanning required."
        ),
        requires_human_approval=(recommended.total_cost > settings.AUTONOMOUS_APPROVAL_LIMIT_USD)
        if recommended else False,
        approval_threshold_usd=settings.AUTONOMOUS_APPROVAL_LIMIT_USD,
    )

# TODO (Dev3): add build_split_sourcing_option(candidates, required_quantity) -> RecoveryPlanOption
