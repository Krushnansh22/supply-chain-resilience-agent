"""
app/tools/production_tools.py
Owner: Developer 2 (DB I/O) + Developer 3 (risk logic in decision_engine/production_risk.py)

RECEIVES: component_id or production_id chosen by the agent
DELIVERS: ToolResult feeding the PRODUCTION info card + "Production coverage is X days" log line
"""

from pymongo.database import Database
from app.decision_engine.inventory_calc import compute_days_of_supply
from app.decision_engine.production_risk import assess_production_risk
from app.schemas.tool_io import ToolResult


def get_production_orders(component_id: str, db: Database, days_of_supply: float | None = None) -> ToolResult:
    rows = list(db["production_orders"].find({"component_id": component_id}, {"_id": 0}))
    if not rows:
        return ToolResult(
            tool_name="get_production_orders",
            success=True,
            data=[],
            summary=f"No production orders depend on {component_id}.",
        )

    # BUG FIX: look up actual days_of_supply from DB if not provided by caller,
    # instead of defaulting to 9999 which always shows risk as LOW.
    if days_of_supply is None:
        inv = db["inventory"].find_one({"component_id": component_id}, {"_id": 0})
        if inv:
            days_of_supply = compute_days_of_supply(inv["usable_stock"], inv["daily_usage"])
        else:
            days_of_supply = 0.0  # no inventory record → treat as zero supply

    results = []
    for r in rows:
        risk = assess_production_risk(
            production_id=r["production_id"],
            days_of_supply=days_of_supply,
            deadline=r.get("deadline"),
            priority=r["priority"],
        )
        results.append({
            "production_id": r["production_id"],
            "product": r["product"],
            "priority": r["priority"],
            "deadline": r["deadline"].isoformat() if r.get("deadline") else None,
            "risk_level": risk.risk_level,
            "reason": risk.reason,
        })

    return ToolResult(
        tool_name="get_production_orders",
        success=True,
        data=results,
        summary=f"Checked {len(results)} production order(s) depending on {component_id}. Days of supply: {days_of_supply}.",
    )
