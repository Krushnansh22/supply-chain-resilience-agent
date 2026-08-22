"""
app/tools/inventory_tools.py
Owner: Developer 2 (Backend I/O) implements DB access; Developer 3 supplies the math
       (decision_engine/inventory_calc.py) this tool wraps.

This is a TOOL the LLM agent (Dev1) can call by name. Its schema (name, description,
parameters) MUST match the entry in app/agent/tool_schemas.py and docs/TOOL_SCHEMAS.md.

RECEIVES: component_id (str) chosen by the LLM based on the incident it's investigating
DELIVERS: ToolResult with usable_stock, days_of_supply etc. — this becomes the
          "Checked inventory — 390 usable units remain." audit log line (docs Section 14)
"""

from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.decision_engine.inventory_calc import compute_days_of_supply
from app.schemas.tool_io import ToolResult


def get_inventory(component_id: str, db: Session) -> ToolResult:
    row = db.query(Inventory).filter(Inventory.component_id == component_id).first()
    if not row:
        return ToolResult(
            tool_name="get_inventory",
            success=False,
            error=f"component {component_id} not found",
            summary=f"Could not find inventory for {component_id}.",
        )

    days = compute_days_of_supply(row.usable_stock, row.daily_usage)
    return ToolResult(
        tool_name="get_inventory",
        success=True,
        data={
            "component_id": row.component_id,
            "usable_stock": row.usable_stock,
            "daily_usage": row.daily_usage,
            "safety_stock": row.safety_stock,
            "days_of_supply": days,
        },
        summary=f"Checked inventory — {row.usable_stock} usable units remain ({days} days of supply).",
    )

# TODO (Dev2/Dev3): add adjust_inventory(component_id, delta, db) used internally by erp_tools.update_erp
