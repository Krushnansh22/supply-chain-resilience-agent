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

from typing import Optional

from app.schemas.recovery_plan import RecoveryPlan, RecoveryPlanOption, SupplierAllocation
from app.decision_engine.supplier_scoring import score_supplier
from app.decision_engine import constraint_validator as cv
from app.config import settings


def _score_candidate(candidate: dict, required_quantity: int, required_by_days: int,
                     max_budget: float) -> float:
    """Compute composite score for a single candidate for ranking."""
    scored = score_supplier(
        supplier_id=candidate["supplier_id"],
        quality_score=candidate.get("quality_score", 50.0),
        reliability_score=candidate.get("reliability_score", 50.0),
        delivery_days=candidate["delivery_days"],
        unit_price=candidate["unit_price"],
        max_acceptable_delivery_days=max(required_by_days * 2, 1),
        max_acceptable_price=max_budget / max(required_quantity, 1),
    )
    return scored.score


def build_recovery_plan(
    incident_id: str,
    required_quantity: int,
    rfq_candidates: list[dict],
    required_cert: Optional[str],
    required_by_days: int,
    max_budget: Optional[float] = None,
) -> RecoveryPlan:
    """
    Builds a complete recovery plan with single-supplier and split-sourcing options.

    Implementation:
    1. Single-supplier options for each RFQ candidate that can cover full quantity.
    2. Split-sourcing option when multiple suppliers can fulfill portions of the order.
    3. Each option validated against constraints; rejected options kept with reasons.
    4. Best constraint-passing option recommended by composite score.
    5. Approval threshold enforced: >$50,000 requires human coordinator approval.
    """
    if max_budget is None:
        max_budget = float("inf")

    options: list[RecoveryPlanOption] = []

    if not rfq_candidates:
        return RecoveryPlan(
            incident_id=incident_id,
            options=[],
            recommended_option_id="",
            recommendation_reason="No supplier candidates available for this component.",
            requires_human_approval=False,
            approval_threshold_usd=settings.AUTONOMOUS_APPROVAL_LIMIT_USD,
        )

    # 1. Single-supplier options
    for candidate in rfq_candidates:
        total_cost = candidate["unit_price"] * required_quantity
        allocation = SupplierAllocation(
            supplier_id=candidate["supplier_id"],
            quantity=required_quantity,
            unit_price=candidate["unit_price"],
            delivery_days=candidate["delivery_days"],
        )

        # Constraint checks
        checks = [cv.check_budget(total_cost, max_budget=max_budget)]
        if required_cert:
            checks.append(
                cv.check_quality_certification(
                    candidate.get("certifications", ""), required_cert
                )
            )
        checks.append(
            cv.check_delivery_deadline(candidate["delivery_days"], required_by_days)
        )

        moq = candidate.get("moq", 0)
        if moq > 0:
            checks.append(cv.check_moq(required_quantity, moq))

        # Collect ALL failed reasons (not just first)
        failed_checks = [c for c in checks if not c.passed]
        rejection_reason = (
            "; ".join(c.reason for c in failed_checks) if failed_checks else None
        )

        options.append(
            RecoveryPlanOption(
                option_id=chr(ord("A") + len(options)),
                allocations=[allocation],
                total_cost=total_cost,
                max_delivery_days=candidate["delivery_days"],
                constraints_satisfied=len(failed_checks) == 0,
                rejection_reason=rejection_reason,
            )
        )

    # 2. Split-sourcing option (first-class option type)
    if len(rfq_candidates) >= 2:
        split_option = _build_split_option(
            rfq_candidates, required_quantity, required_cert,
            required_by_days, max_budget, chr(ord("A") + len(options)),
        )
        if split_option:
            options.append(split_option)

    # 3. Rank valid options by composite score, pick best
    valid_options = [o for o in options if o.constraints_satisfied]

    if valid_options:
        # Score each valid option
        scored_valid = []
        for opt in valid_options:
            if len(opt.allocations) == 1:
                candidate = next(
                    (c for c in rfq_candidates
                     if c["supplier_id"] == opt.allocations[0].supplier_id),
                    None,
                )
                if candidate:
                    score = _score_candidate(
                        candidate, required_quantity, required_by_days, max_budget
                    )
                else:
                    score = 0.0
            else:
                # Split-sourcing: weighted average of supplier scores
                scores = []
                for alloc in opt.allocations:
                    cand = next(
                        (c for c in rfq_candidates
                         if c["supplier_id"] == alloc.supplier_id),
                        None,
                    )
                    if cand:
                        scores.append(
                            _score_candidate(
                                cand, alloc.quantity, required_by_days, max_budget
                            )
                        )
                score = sum(scores) / len(scores) if scores else 0.0

            scored_valid.append((opt, score))

        # Sort by score descending (best first)
        scored_valid.sort(key=lambda x: x[1], reverse=True)
        recommended = scored_valid[0][0]
    else:
        recommended = None

    # 4. Build recommendation reason
    if recommended:
        if len(recommended.allocations) > 1:
            supplier_list = ", ".join(a.supplier_id for a in recommended.allocations)
            recommendation_reason = (
                f"Split-sourcing across {supplier_list} — "
                f"lowest risk satisfying all delivery & budget constraints."
            )
        else:
            recommendation_reason = (
                f"Best option from {recommended.allocations[0].supplier_id} — "
                f"lowest cost satisfying all constraints."
            )
    else:
        recommendation_reason = (
            "No option currently satisfies all constraints — replanning or escalation required."
        )

    # 5. Approval threshold check (PS REQUIRED: >$50,000)
    recommended_cost = recommended.total_cost if recommended else 0
    requires_human_approval = (recommended_cost > settings.AUTONOMOUS_APPROVAL_LIMIT_USD) or (recommended is None)

    return RecoveryPlan(
        incident_id=incident_id,
        options=options,
        recommended_option_id=recommended.option_id if recommended else "",
        recommendation_reason=recommendation_reason,
        requires_human_approval=requires_human_approval,
        approval_threshold_usd=settings.AUTONOMOUS_APPROVAL_LIMIT_USD,
    )


def _build_split_option(
    candidates: list[dict],
    required_quantity: int,
    required_cert: Optional[str],
    required_by_days: int,
    max_budget: float,
    option_id: str,
) -> Optional[RecoveryPlanOption]:
    """
    Builds a split-sourcing option when multiple suppliers can fulfill portions of the order.
    Tries multiple split ratios and picks the best combination.
    """
    sorted_candidates = sorted(
        candidates, key=lambda c: c.get("unit_price", float("inf"))
    )

    best_valid_option = None
    best_valid_cost = float("inf")
    fallback_option = None

    for i in range(min(len(sorted_candidates), 4)):
        for j in range(i + 1, min(len(sorted_candidates), 4)):
            c1 = sorted_candidates[i]
            c2 = sorted_candidates[j]

            for split_pct in [0.4, 0.5, 0.6]:
                qty1 = int(required_quantity * split_pct)
                qty2 = required_quantity - qty1

                if qty1 <= 0 or qty2 <= 0:
                    continue

                cost1 = c1["unit_price"] * qty1
                cost2 = c2["unit_price"] * qty2
                total_cost = cost1 + cost2

                # Check all constraints
                rejection_reasons = []

                # MOQ check
                moq1 = c1.get("moq", 0)
                moq2 = c2.get("moq", 0)
                if moq1 > 0 and qty1 < moq1:
                    rejection_reasons.append(f"Supplier {c1['supplier_id']} MOQ {moq1} not met (ordered {qty1})")
                if moq2 > 0 and qty2 < moq2:
                    rejection_reasons.append(f"Supplier {c2['supplier_id']} MOQ {moq2} not met (ordered {qty2})")

                budget_check = cv.check_budget(total_cost, max_budget)
                if not budget_check.passed:
                    rejection_reasons.append(budget_check.reason)

                if required_cert:
                    for c in [c1, c2]:
                        cert_check = cv.check_quality_certification(
                            c.get("certifications", ""), required_cert
                        )
                        if not cert_check.passed:
                            rejection_reasons.append(
                                f"Supplier {c['supplier_id']}: {cert_check.reason}"
                            )

                max_delivery = max(c1["delivery_days"], c2["delivery_days"])
                deadline_check = cv.check_delivery_deadline(
                    max_delivery, required_by_days
                )
                if not deadline_check.passed:
                    rejection_reasons.append(deadline_check.reason)

                constraints_ok = len(rejection_reasons) == 0

                opt = RecoveryPlanOption(
                    option_id=option_id,
                    allocations=[
                        SupplierAllocation(
                            supplier_id=c1["supplier_id"],
                            quantity=qty1,
                            unit_price=c1["unit_price"],
                            delivery_days=c1["delivery_days"],
                        ),
                        SupplierAllocation(
                            supplier_id=c2["supplier_id"],
                            quantity=qty2,
                            unit_price=c2["unit_price"],
                            delivery_days=c2["delivery_days"],
                        ),
                    ],
                    total_cost=total_cost,
                    max_delivery_days=max_delivery,
                    constraints_satisfied=constraints_ok,
                    rejection_reason="; ".join(rejection_reasons) if rejection_reasons else None,
                )

                if constraints_ok and total_cost < best_valid_cost:
                    best_valid_cost = total_cost
                    best_valid_option = opt
                elif fallback_option is None:
                    fallback_option = opt

    return best_valid_option or fallback_option
