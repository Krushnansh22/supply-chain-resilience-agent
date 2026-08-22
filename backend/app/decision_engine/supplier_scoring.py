"""
app/decision_engine/supplier_scoring.py
Owner: Developer 3 (Decision Engine)

RECOMMENDED (team doc Section 8): score combines delivery, reliability, quality, cost.
Exact weights are a CHOSEN implementation detail — tune during testing, document
final weights in docs/DB_SCHEMA.md or a new docs/SCORING.md.

RECEIVES: Supplier row (quality_score, reliability_score) + RFQ row (unit_price, delivery_days)
DELIVERS: a comparable score used by recovery_planner.py to rank/choose between suppliers
"""

from dataclasses import dataclass


# TODO (Dev3): tune these weights during testing; they must sum to 1.0
WEIGHTS = {
    "quality": 0.30,
    "reliability": 0.30,
    "delivery": 0.20,
    "cost": 0.20,
}


@dataclass
class ScoredSupplier:
    supplier_id: str
    score: float
    breakdown: dict


def score_supplier(
    supplier_id: str,
    quality_score: float,       # 0-100
    reliability_score: float,   # 0-100
    delivery_days: int,
    unit_price: float,
    max_acceptable_delivery_days: int,
    max_acceptable_price: float,
) -> ScoredSupplier:
    """
    Normalizes each factor to 0-1 (higher is better) and applies WEIGHTS.
    TODO (Dev3): replace naive linear normalization below with whatever the team
    agrees is fair; keep return shape (ScoredSupplier) stable for recovery_planner.py.
    """
    quality_norm = quality_score if 0 <= quality_score <= 1.0 else min(1.0, quality_score / 100)
    reliability_norm = reliability_score if 0 <= reliability_score <= 1.0 else min(1.0, reliability_score / 100)
    delivery_norm = max(0.0, 1 - (delivery_days / max(max_acceptable_delivery_days, 1)))
    cost_norm = (
        max(0.0, 1 - (unit_price / max(max_acceptable_price, 1)))
        if max_acceptable_price != float("inf")
        else 1.0
    )

    breakdown = {
        "quality": quality_norm * WEIGHTS["quality"],
        "reliability": reliability_norm * WEIGHTS["reliability"],
        "delivery": delivery_norm * WEIGHTS["delivery"],
        "cost": cost_norm * WEIGHTS["cost"],
    }
    total = round(sum(breakdown.values()), 4)

    return ScoredSupplier(supplier_id=supplier_id, score=total, breakdown=breakdown)
