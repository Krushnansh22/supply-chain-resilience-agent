"""
app/decision_engine/inventory_calc.py
Owner: Developer 3 (Decision Engine)

REQUIRED business rule (team doc Section 8):
    days_of_supply = usable_stock / daily_usage
    if days_of_supply < required_lead_time: production_risk = HIGH

RECEIVES: raw values from app/models/inventory.py rows (via API routes or tools)
DELIVERS: `days_of_supply` used by:
  - api/routes_inventory.py (shown in Inventory page)
  - decision_engine/production_risk.py (risk calculation)
  - tools/inventory_tools.get_inventory() (what the agent sees when it calls the tool)
"""


def compute_days_of_supply(usable_stock: int, daily_usage: float) -> float:
    """
    Returns remaining days of coverage. Guards against division by zero
    (e.g. a component that isn't currently consumed).
    """
    if daily_usage <= 0:
        return float("inf")
    return round(usable_stock / daily_usage, 2)


def is_below_safety_stock(usable_stock: int, safety_stock: int) -> bool:
    return usable_stock < safety_stock


# TODO (Dev3): add compute_shortfall(required_qty, usable_stock) -> int
# used by recovery_planner.py to know how many units must be sourced externally.
