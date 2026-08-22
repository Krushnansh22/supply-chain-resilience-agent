"""
app/decision_engine/replanning.py
Owner: Developer 3 (Decision Engine), triggered by Developer 1's agent loop

REQUIRED demo capability (team doc Section 19E, "one of the most important advanced
features"): if a chosen supplier in an active plan becomes unavailable / a new
disruption invalidates the plan, detect invalidation and produce a new plan.

RECEIVES: current RecoveryPlan + a reason the plan may be invalid (e.g. new incident
          affecting the same component/supplier)
DELIVERS: bool (is_plan_invalid) + reason, consumed by agent/agent_loop.py to transition
          into the REPLANNING state, and then calls recovery_planner.build_recovery_plan()
          again with updated RFQ candidates to produce "Plan B".
"""

from app.schemas.recovery_plan import RecoveryPlan


def is_plan_invalidated(plan: RecoveryPlan, new_incident_affected_component: str | None,
                         new_incident_affected_supplier: str | None) -> tuple[bool, str]:
    """
    TODO (Dev3): implement real invalidation logic. Starter check below only looks
    at whether any allocation's supplier_id matches the newly-disrupted supplier.
    """
    if not new_incident_affected_supplier:
        return False, ""

    for option in plan.options:
        if option.option_id != plan.recommended_option_id:
            continue
        for alloc in option.allocations:
            if alloc.supplier_id == new_incident_affected_supplier:
                return True, f"Supplier {alloc.supplier_id} in the active plan is now unavailable."

    return False, ""
