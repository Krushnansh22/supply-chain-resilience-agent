"""
app/decision_engine/production_risk.py
Owner: Developer 3 (Decision Engine)

REQUIRED business rule (team doc Section 8 + PS Core Capability #1: "determine
impacted orders, inventory batches, and shipment corridors"):
    if days_of_supply < required_lead_time -> production risk = HIGH

RECEIVES: days_of_supply (from inventory_calc.py), production order deadline/priority
          (from app/models/production_orders.py)
DELIVERS: risk level consumed by:
  - tools/production_tools.get_production_orders() (agent-visible)
  - frontend PRODUCTION info card (Incident Command Center, docs Section 13)
"""

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class ProductionRiskResult:
    production_id: str
    risk_level: str          # LOW | MEDIUM | HIGH | CRITICAL
    days_of_supply: float
    required_lead_time_days: float
    reason: str


def assess_production_risk(
    production_id: str,
    days_of_supply: float,
    deadline: datetime,
    priority: str,
    now: datetime | None = None,
) -> ProductionRiskResult:
    """
    TODO (Dev3): implement full risk model. Starter logic below is intentionally
    simple — replace with whatever scoring the team agrees on, but keep the
    function signature stable since Dev1's agent + Dev2's tools already call it.
    """
    if now is None:
        now = datetime.now(timezone.utc)

    if deadline is not None:
        if now.tzinfo is not None and deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
        elif now.tzinfo is None and deadline.tzinfo is not None:
            now = now.replace(tzinfo=timezone.utc)

    required_lead_time_days = max((deadline - now).days, 0) if deadline else 0

    if days_of_supply < required_lead_time_days:
        risk = "CRITICAL" if priority == "HIGH" else "HIGH"
        reason = (
            f"Only {days_of_supply} days of supply remain but "
            f"{required_lead_time_days} days are needed before the deadline."
        )
    else:
        risk = "LOW"
        reason = "Inventory coverage exceeds required lead time."

    return ProductionRiskResult(
        production_id=production_id,
        risk_level=risk,
        days_of_supply=days_of_supply,
        required_lead_time_days=required_lead_time_days,
        reason=reason,
    )
