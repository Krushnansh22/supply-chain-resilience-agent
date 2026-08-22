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

from dataclasses import dataclass
from typing import Optional

from app.schemas.recovery_plan import RecoveryPlan


@dataclass
class ReplanningCheckResult:
    """Result of replanning invalidation check."""
    is_invalid: bool
    reason: str
    affected_suppliers: list[str]
    affected_components: list[str]


def is_plan_invalidated(
    plan: RecoveryPlan,
    new_incident_affected_component: Optional[str] = None,
    new_incident_affected_supplier: Optional[str] = None,
    new_incident_type: Optional[str] = None,
) -> tuple[bool, str]:
    """
    Checks if a recovery plan is invalidated by a new disruption.

    Invalidation triggers:
    1. The newly disrupted supplier is in the recommended option's allocations
    2. The incident affects the same component as the plan
    3. The incident type is severe enough to warrant replanning (SUPPLIER_LIE, QUALITY_FAILURE)

    Returns: (is_invalid, reason) tuple
    """
    result = check_plan_invalidation(
        plan,
        new_incident_affected_component,
        new_incident_affected_supplier,
        new_incident_type,
    )
    return result.is_invalid, result.reason


def check_plan_invalidation(
    plan: RecoveryPlan,
    new_incident_affected_component: Optional[str] = None,
    new_incident_affected_supplier: Optional[str] = None,
    new_incident_type: Optional[str] = None,
) -> ReplanningCheckResult:
    """
    Comprehensive invalidation check with detailed result.
    """
    affected_suppliers = []
    affected_components = []

    if not plan.options:
        return ReplanningCheckResult(
            is_invalid=False,
            reason="",
            affected_suppliers=[],
            affected_components=[],
        )

    # Find the recommended option
    recommended_option = None
    for option in plan.options:
        if option.option_id == plan.recommended_option_id:
            recommended_option = option
            break

    if not recommended_option:
        return ReplanningCheckResult(
            is_invalid=True,
            reason="No recommended option found in the plan.",
            affected_suppliers=[],
            affected_components=[],
        )

    # Check 1: Supplier in the plan is directly affected
    if new_incident_affected_supplier:
        for alloc in recommended_option.allocations:
            if alloc.supplier_id == new_incident_affected_supplier:
                affected_suppliers.append(alloc.supplier_id)
                return ReplanningCheckResult(
                    is_invalid=True,
                    reason=(
                        f"Supplier {alloc.supplier_id} in the active plan "
                        f"is now unavailable due to {new_incident_type or 'disruption'}."
                    ),
                    affected_suppliers=affected_suppliers,
                    affected_components=affected_components,
                )

    # Check 2: Incident affects the same component (may invalidate sourcing assumptions)
    if new_incident_affected_component:
        # Check if any allocation in the plan is for this component
        # (We store component context externally, but the plan itself doesn't track it.
        #  The agent loop should pass component context when calling this.)
        # For now, flag if the component matches any known context.
        affected_components.append(new_incident_affected_component)

    # Check 3: Severe incident types always trigger replanning
    severe_types = {"SUPPLIER_LIE", "QUALITY_FAILURE"}
    if new_incident_type and new_incident_type in severe_types:
        return ReplanningCheckResult(
            is_invalid=True,
            reason=(
                f"Incident type '{new_incident_type}' requires replanning — "
                f"supplier trust compromised or quality standards not met."
            ),
            affected_suppliers=affected_suppliers or [a.supplier_id for a in recommended_option.allocations],
            affected_components=affected_components,
        )

    # Check 4: Component mismatch check (if we have component context)
    if affected_components:
        return ReplanningCheckResult(
            is_invalid=True,
            reason=(
                f"New disruption affects component {affected_components[0]}, "
                f"which may impact the sourcing plan."
            ),
            affected_suppliers=affected_suppliers,
            affected_components=affected_components,
        )

    return ReplanningCheckResult(
        is_invalid=False,
        reason="",
        affected_suppliers=[],
        affected_components=[],
    )


def get_replanning_context(
    plan: RecoveryPlan,
    new_incident_affected_component: Optional[str] = None,
    new_incident_affected_supplier: Optional[str] = None,
) -> dict:
    """
    Gathers context needed for the agent to build a new plan.
    Called after invalidation is detected to provide the agent with
    information about what failed and what to avoid in the new plan.
    """
    result = check_plan_invalidation(
        plan, new_incident_affected_component, new_incident_affected_supplier
    )

    # Get suppliers to avoid in new plan
    suppliers_to_avoid = set(result.affected_suppliers)

    # Also add suppliers from the failed recommended option
    for option in plan.options:
        if option.option_id == plan.recommended_option_id:
            for alloc in option.allocations:
                suppliers_to_avoid.add(alloc.supplier_id)

    return {
        "is_invalid": result.is_invalid,
        "reason": result.reason,
        "suppliers_to_avoid": list(suppliers_to_avoid),
        "affected_components": result.affected_components,
        "previous_option_id": plan.recommended_option_id,
        "previous_cost": next(
            (o.total_cost for o in plan.options
             if o.option_id == plan.recommended_option_id),
            0,
        ),
    }
