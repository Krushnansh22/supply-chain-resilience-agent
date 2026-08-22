"""
app/decision_engine/routing_evaluator.py
Owner: Developer 3 (Decision Engine)

REQUIRED (PS Core Capability #2): "evaluate multi-modal re-routing options against
SLA commitments and cost budgets" — for the 18h scope, "multi-modal" is simplified
to multi-supplier sourcing (multiple suppliers can cover the same component need).

This module evaluates candidate routing options and scores them on SLA compliance,
cost efficiency, and risk. It is called by recovery_planner.py to rank options.

RECEIVES: list of candidate supplier allocations + SLA/cost constraints
DELIVERS: ranked list of routing options with SLA/cost scores
"""

from dataclasses import dataclass, field
from typing import Optional

from app.decision_engine.supplier_scoring import score_supplier, ScoredSupplier
from app.decision_engine import constraint_validator as cv
from app.schemas.recovery_plan import SupplierAllocation


@dataclass
class RoutingOption:
    """A single routing configuration (single or multi-supplier)."""
    option_id: str
    allocations: list[SupplierAllocation]
    total_cost: float
    max_delivery_days: int
    sla_score: float              # 0-1, how well it meets SLA
    cost_score: float             # 0-1, cost efficiency
    composite_score: float        # weighted combination
    sla_met: bool
    budget_met: bool
    rejection_reasons: list[str] = field(default_factory=list)


def evaluate_sla_compliance(
    delivery_days: int,
    required_by_days: int,
) -> tuple[bool, float]:
    """
    Returns (sla_met, sla_score).
    sla_score = 1.0 if delivery is early, degrades linearly if late.
    """
    if required_by_days <= 0:
        return delivery_days == 0, 1.0 if delivery_days == 0 else 0.0

    if delivery_days <= required_by_days:
        # Early or on time — score 1.0 with bonus for being early
        margin = (required_by_days - delivery_days) / required_by_days
        return True, min(1.0, 0.8 + margin * 0.2)
    else:
        # Late — score degrades
        lateness_ratio = (delivery_days - required_by_days) / required_by_days
        score = max(0.0, 1.0 - lateness_ratio)
        return False, score


def evaluate_cost_efficiency(
    total_cost: float,
    max_budget: float,
) -> tuple[bool, float]:
    """
    Returns (budget_met, cost_score).
    cost_score = 1.0 if cost is 0, degrades linearly to 0 at max_budget.
    """
    if max_budget <= 0:
        return total_cost == 0, 1.0 if total_cost == 0 else 0.0

    if total_cost <= max_budget:
        # Within budget — score based on how much headroom remains
        efficiency = 1.0 - (total_cost / max_budget)
        return True, 0.5 + efficiency * 0.5  # 0.5-1.0 range
    else:
        # Over budget
        return False, 0.0


def evaluate_routing_options(
    candidates: list[dict],
    required_quantity: int,
    required_cert: Optional[str],
    required_by_days: int,
    max_budget: float,
    supplier_scores: Optional[dict[str, ScoredSupplier]] = None,
) -> list[RoutingOption]:
    """
    Evaluates all possible routing configurations from the candidate suppliers.

    For multi-supplier (split-sourcing) support, generates combinations where
    multiple suppliers can split the required quantity.

    Args:
        candidates: list of dicts with keys:
            supplier_id, unit_price, delivery_days, certifications, moq,
            quality_score, reliability_score
        required_quantity: total units needed
        required_cert: optional required certification (e.g., "ISO9001")
        required_by_days: SLA deadline in days
        max_budget: maximum allowed cost
        supplier_scores: optional pre-computed ScoredSupplier objects

    Returns: list of RoutingOption, sorted by composite_score descending
    """
    options: list[RoutingOption] = []
    option_counter = 0

    # Sort candidates by delivery_days (fastest first) as primary heuristic
    sorted_candidates = sorted(candidates, key=lambda c: c.get("delivery_days", 999))

    # 1. Single-supplier options
    for candidate in sorted_candidates:
        option_counter += 1
        option_id = chr(ord("A") + option_counter - 1)

        supplier_id = candidate["supplier_id"]
        unit_price = candidate["unit_price"]
        delivery_days = candidate["delivery_days"]

        total_cost = unit_price * required_quantity

        allocation = SupplierAllocation(
            supplier_id=supplier_id,
            quantity=required_quantity,
            unit_price=unit_price,
            delivery_days=delivery_days,
        )

        # Evaluate SLA
        sla_met, sla_score = evaluate_sla_compliance(delivery_days, required_by_days)

        # Evaluate cost
        budget_met, cost_score = evaluate_cost_efficiency(total_cost, max_budget)

        # Check constraints
        rejection_reasons = []
        budget_result = cv.check_budget(total_cost, max_budget)
        if not budget_result.passed:
            rejection_reasons.append(budget_result.reason)

        if required_cert:
            cert_result = cv.check_quality_certification(
                candidate.get("certifications", ""), required_cert
            )
            if not cert_result.passed:
                rejection_reasons.append(cert_result.reason)

        deadline_result = cv.check_delivery_deadline(delivery_days, required_by_days)
        if not deadline_result.passed:
            rejection_reasons.append(deadline_result.reason)

        # MOQ check if provided
        moq = candidate.get("moq", 0)
        if moq > 0:
            moq_result = cv.check_moq(required_quantity, moq)
            if not moq_result.passed:
                rejection_reasons.append(moq_result.reason)

        # Get supplier quality/reliability for scoring
        quality_score = candidate.get("quality_score", 50.0)
        reliability_score = candidate.get("reliability_score", 50.0)

        # Use pre-computed supplier score if available
        if supplier_scores and supplier_id in supplier_scores:
            supplier_score_obj = supplier_scores[supplier_id]
            composite = supplier_score_obj.score
        else:
            # Compute supplier quality score
            scored = score_supplier(
                supplier_id=supplier_id,
                quality_score=quality_score,
                reliability_score=reliability_score,
                delivery_days=delivery_days,
                unit_price=unit_price,
                max_acceptable_delivery_days=required_by_days * 2,
                max_acceptable_price=max_budget / max(required_quantity, 1),
            )
            composite = scored.score

        # Weighted composite: 40% supplier quality, 30% SLA, 30% cost
        final_score = (composite * 0.4) + (sla_score * 0.3) + (cost_score * 0.3)

        options.append(RoutingOption(
            option_id=option_id,
            allocations=[allocation],
            total_cost=total_cost,
            max_delivery_days=delivery_days,
            sla_score=round(sla_score, 4),
            cost_score=round(cost_score, 4),
            composite_score=round(final_score, 4),
            sla_met=sla_met,
            budget_met=budget_met,
            rejection_reasons=rejection_reasons,
        ))

    # 2. Split-sourcing options (when no single supplier can optimally cover the need)
    # Generate combinations of 2 suppliers that split the quantity
    if len(sorted_candidates) >= 2:
        for i in range(len(sorted_candidates)):
            for j in range(i + 1, len(sorted_candidates)):
                c1 = sorted_candidates[i]
                c2 = sorted_candidates[j]

                # Try different split ratios
                for split_pct in [0.4, 0.5, 0.6]:
                    qty1 = int(required_quantity * split_pct)
                    qty2 = required_quantity - qty1

                    if qty1 <= 0 or qty2 <= 0:
                        continue

                    # Check MOQ for each portion
                    moq1 = c1.get("moq", 0)
                    moq2 = c2.get("moq", 0)
                    if (moq1 > 0 and qty1 < moq1) or (moq2 > 0 and qty2 < moq2):
                        continue

                    cost1 = c1["unit_price"] * qty1
                    cost2 = c2["unit_price"] * qty2
                    total_cost = cost1 + cost2

                    if total_cost > max_budget * 1.2:  # allow 20% over for split options
                        continue

                    # Max delivery is the slower of the two
                    max_delivery = max(c1["delivery_days"], c2["delivery_days"])

                    option_counter += 1
                    option_id = chr(ord("A") + option_counter - 1)

                    alloc1 = SupplierAllocation(
                        supplier_id=c1["supplier_id"],
                        quantity=qty1,
                        unit_price=c1["unit_price"],
                        delivery_days=c1["delivery_days"],
                    )
                    alloc2 = SupplierAllocation(
                        supplier_id=c2["supplier_id"],
                        quantity=qty2,
                        unit_price=c2["unit_price"],
                        delivery_days=c2["delivery_days"],
                    )

                    # Evaluate SLA (uses max delivery)
                    sla_met, sla_score = evaluate_sla_compliance(max_delivery, required_by_days)

                    # Evaluate cost
                    budget_met, cost_score = evaluate_cost_efficiency(total_cost, max_budget)

                    # Check constraints for both suppliers
                    rejection_reasons = []
                    budget_result = cv.check_budget(total_cost, max_budget)
                    if not budget_result.passed:
                        rejection_reasons.append(budget_result.reason)

                    if required_cert:
                        for c in [c1, c2]:
                            cert_result = cv.check_quality_certification(
                                c.get("certifications", ""), required_cert
                            )
                            if not cert_result.passed:
                                rejection_reasons.append(
                                    f"Supplier {c['supplier_id']}: {cert_result.reason}"
                                )

                    deadline_result = cv.check_delivery_deadline(max_delivery, required_by_days)
                    if not deadline_result.passed:
                        rejection_reasons.append(deadline_result.reason)

                    # Composite score for split option
                    # Use average of supplier scores, with slight penalty for complexity
                    s1_score = score_supplier(
                        supplier_id=c1["supplier_id"],
                        quality_score=c1.get("quality_score", 50.0),
                        reliability_score=c1.get("reliability_score", 50.0),
                        delivery_days=c1["delivery_days"],
                        unit_price=c1["unit_price"],
                        max_acceptable_delivery_days=required_by_days * 2,
                        max_acceptable_price=max_budget / max(required_quantity, 1),
                    ).score
                    s2_score = score_supplier(
                        supplier_id=c2["supplier_id"],
                        quality_score=c2.get("quality_score", 50.0),
                        reliability_score=c2.get("reliability_score", 50.0),
                        delivery_days=c2["delivery_days"],
                        unit_price=c2["unit_price"],
                        max_acceptable_delivery_days=required_by_days * 2,
                        max_acceptable_price=max_budget / max(required_quantity, 1),
                    ).score
                    avg_supplier_score = (s1_score + s2_score) / 2

                    # Split-sourcing penalty: 5% for complexity
                    final_score = (
                        (avg_supplier_score * 0.4)
                        + (sla_score * 0.3)
                        + (cost_score * 0.3)
                    ) * 0.95

                    options.append(RoutingOption(
                        option_id=option_id,
                        allocations=[alloc1, alloc2],
                        total_cost=total_cost,
                        max_delivery_days=max_delivery,
                        sla_score=round(sla_score, 4),
                        cost_score=round(cost_score, 4),
                        composite_score=round(final_score, 4),
                        sla_met=sla_met,
                        budget_met=budget_met,
                        rejection_reasons=rejection_reasons,
                    ))

    # Sort by composite_score descending (best first)
    options.sort(key=lambda o: o.composite_score, reverse=True)

    return options
