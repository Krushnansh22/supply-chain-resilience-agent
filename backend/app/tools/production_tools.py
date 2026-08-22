"""
app/tools/production_tools.py
Owner: Developer 2 (DB I/O) + Developer 3 (risk logic in decision_engine/production_risk.py)

RECEIVES: component_id or production_id chosen by the agent
DELIVERS: ToolResult feeding the PRODUCTION info card + "Production coverage is X days" log line
"""

from sqlalchemy.orm import Session

from app.models.production_orders import ProductionOrder
from app.decision_engine.production_risk import assess_production_risk
from app.schemas.tool_io import ToolResult


def get_production_orders(component_id: str, db: Session, days_of_supply: float | None = None) -> ToolResult:
    rows = db.query(ProductionOrder).filter(ProductionOrder.component_id == component_id).all()
    if not rows:
        return ToolResult(
            tool_name="get_production_orders",
            success=True,
            data=[],
            summary=f"No production orders depend on {component_id}.",
        )

    results = []
    for r in rows:
        risk = assess_production_risk(
            production_id=r.production_id,
            days_of_supply=days_of_supply if days_of_supply is not None else 9999,
            deadline=r.deadline,
            priority=r.priority,
        )
        results.append({
            "production_id": r.production_id,
            "product": r.product,
            "priority": r.priority,
            "deadline": r.deadline.isoformat() if r.deadline else None,
            "risk_level": risk.risk_level,
            "reason": risk.reason,
        })

    return ToolResult(
        tool_name="get_production_orders",
        success=True,
        data=results,
        summary=f"Checked {len(results)} production order(s) depending on {component_id}.",
    )
