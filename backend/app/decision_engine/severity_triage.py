"""
app/decision_engine/severity_triage.py
Owner: Developer 3 (Decision Engine)

REQUIRED (PS Core Capability #1): "determine impacted orders, inventory batches,
and shipment corridors" — this is the triage/classification step that assigns
severity levels to incidents based on multiple factors.

RECEIVES: incident type, affected component data, production impact, financial exposure
DELIVERS: severity classification (LOW | MEDIUM | HIGH | CRITICAL) consumed by:
  - agent/agent_loop.py (determines response urgency)
  - frontend incident display (UI color coding)
  - audit logging (decision trail)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.decision_engine.inventory_calc import compute_days_of_supply, is_below_safety_stock


@dataclass
class TriageInput:
    """All data needed for severity classification."""
    incident_type: str                          # SUPPLIER_DELAY, SUPPLIER_LIE, QUALITY_FAILURE, etc.
    affected_component: Optional[str] = None    # component_id
    affected_po: Optional[str] = None          # po_id

    # Inventory context
    usable_stock: int = 0
    daily_usage: float = 0.0
    safety_stock: int = 0

    # Production context
    production_quantity: int = 0                # total units needed by affected production orders
    production_deadline_days: int = 0           # days until earliest affected deadline
    production_priority: str = "LOW"            # LOW | MEDIUM | HIGH

    # Financial context
    po_value_usd: float = 0.0                   # value of affected purchase order(s)

    # Supplier context
    supplier_quality_score: float = 100.0       # 0-100
    supplier_reliability_score: float = 100.0   # 0-100


@dataclass
class TriageResult:
    severity: str                              # LOW | MEDIUM | HIGH | CRITICAL
    classification_reason: str
    factors: dict                              # breakdown of what contributed to the severity


# --- Incident type base weights (PS-mandated types) ---
INCIDENT_TYPE_WEIGHTS = {
    "SUPPLIER_DELAY": 0.5,
    "SUPPLIER_LIE": 0.8,      # deliberate deception is severe
    "QUALITY_FAILURE": 0.7,
    "BUDGET_OVERRUN": 0.4,
    "STALE_INVENTORY": 0.3,
}

# --- Thresholds for severity escalation ---
STOCK_BELOW_SAFETY_MULTPLIER = 0.5     # < 50% of safety stock -> escalate
CRITICAL_DAYS_OF_SUPPLY = 3.0           # < 3 days -> escalate
HIGH_VALUE_THRESHOLD = 25000.0          # PO value > $25K -> escalate
CRITICAL_VALUE_THRESHOLD = 75000.0      # PO value > $75K -> escalate


def triage_incident(inp: TriageInput) -> TriageResult:
    """
    Classifies incident severity using a multi-factor scoring model.

    The model combines:
    1. Incident type base weight (supplier lie > quality failure > delay > budget > stale)
    2. Inventory pressure (days of supply, safety stock breach)
    3. Production impact (deadline urgency, priority)
    4. Financial exposure (PO value)
    5. Supplier risk (low quality/reliability scores)

    Returns a TriageResult with severity classification and human-readable explanation.
    """
    factors = {}
    score = 0.0

    # Factor 1: Incident type base weight
    type_weight = INCIDENT_TYPE_WEIGHTS.get(inp.incident_type, 0.3)
    factors["incident_type_weight"] = type_weight
    score += type_weight * 10  # scale to 0-10 range contribution

    # Factor 2: Inventory pressure
    days_of_supply = compute_days_of_supply(inp.usable_stock, inp.daily_usage)
    below_safety = is_below_safety_stock(inp.usable_stock, inp.safety_stock)

    inventory_pressure = 0.0
    if below_safety:
        # How far below safety stock?
        if inp.safety_stock > 0:
            ratio = inp.usable_stock / inp.safety_stock
            inventory_pressure = max(0.0, 1.0 - ratio) * 3.0  # up to 3 points
        else:
            inventory_pressure = 2.0
    elif days_of_supply < CRITICAL_DAYS_OF_SUPPLY:
        inventory_pressure = 2.5
    elif days_of_supply < CRITICAL_DAYS_OF_SUPPLY * 2:
        inventory_pressure = 1.5

    factors["inventory_pressure"] = round(inventory_pressure, 2)
    score += inventory_pressure

    # Factor 3: Production impact
    production_pressure = 0.0
    if inp.production_deadline_days > 0:
        # Urgency: less time = higher pressure
        if inp.production_deadline_days <= 3:
            production_pressure = 3.0
        elif inp.production_deadline_days <= 7:
            production_pressure = 2.0
        elif inp.production_deadline_days <= 14:
            production_pressure = 1.0

        # Priority multiplier
        if inp.production_priority == "HIGH":
            production_pressure *= 1.5
        elif inp.production_priority == "MEDIUM":
            production_pressure *= 1.2

    factors["production_pressure"] = round(production_pressure, 2)
    score += production_pressure

    # Factor 4: Financial exposure
    financial_pressure = 0.0
    if inp.po_value_usd >= CRITICAL_VALUE_THRESHOLD:
        financial_pressure = 3.0
    elif inp.po_value_usd >= HIGH_VALUE_THRESHOLD:
        financial_pressure = 2.0
    elif inp.po_value_usd > 0:
        financial_pressure = 1.0

    factors["financial_pressure"] = round(financial_pressure, 2)
    score += financial_pressure

    # Factor 5: Supplier risk (low scores indicate unreliable supplier)
    supplier_risk = 0.0
    if inp.supplier_quality_score < 60 or inp.supplier_reliability_score < 60:
        supplier_risk = 2.0
    elif inp.supplier_quality_score < 80 or inp.supplier_reliability_score < 80:
        supplier_risk = 1.0

    factors["supplier_risk"] = round(supplier_risk, 2)
    score += supplier_risk

    factors["total_score"] = round(score, 2)

    # Map score to severity
    if score >= 15.0:
        severity = "CRITICAL"
        reason = (
            f"CRITICAL: Multiple severe factors — {inp.incident_type} with "
            f"{days_of_supply}d supply remaining, "
            f"production deadline in {inp.production_deadline_days}d, "
            f"${inp.po_value_usd:,.0f} financial exposure."
        )
    elif score >= 10.0:
        severity = "HIGH"
        reason = (
            f"HIGH: Significant impact — {inp.incident_type} with "
            f"inventory pressure and production deadline approaching."
        )
    elif score >= 5.0:
        severity = "MEDIUM"
        reason = (
            f"MEDIUM: Moderate impact — {inp.incident_type} requires attention "
            f"but no immediate critical risk."
        )
    else:
        severity = "LOW"
        reason = f"LOW: Minor incident — {inp.incident_type} with sufficient buffer."

    return TriageResult(
        severity=severity,
        classification_reason=reason,
        factors=factors,
    )


def classify_incident_type(
    incident_type: str,
    message_content: str = "",
    tracking_status: str = "",
) -> str:
    """
    Sub-classification for incident types that need more nuance.

    For SUPPLIER_LIE detection: cross-reference supplier message claims against
    actual tracking status (team doc: "message says dispatched, tracking says
    no pickup scan").
    """
    if incident_type == "SUPPLIER_LIE":
        # Check for contradiction between message and tracking
        message_lower = message_content.lower()
        tracking_lower = tracking_status.lower()

        dispatch_claimed = any(w in message_lower for w in ["dispatched", "shipped", "in transit", "sent"])
        no_pickup = any(w in tracking_lower for w in ["no pickup", "not scanned", "pending pickup", ""])

        if dispatch_claimed and no_pickup:
            return "DISPATCH_CONTRADICTION"
        return "GENERIC_LIE"

    return incident_type
