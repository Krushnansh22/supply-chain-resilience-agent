"""
app/tools/rfq_tools.py
Owner: Developer 2 (Backend / Simulation), consumed by Developer 3's recovery_planner.py

RECEIVES: component_id, quantity, list of candidate supplier_ids chosen by the agent
DELIVERS: simulated RFQ responses (unit_price, delivery_days, expedite options), persisted
          to app/models/rfqs.py, and returned to the agent for "Requesting alternative
          RFQs" activity log entries.
"""

from sqlalchemy.orm import Session

from app.models.rfqs import RFQ
from app.schemas.tool_io import ToolResult
from app.simulator.supplier_simulator import simulate_rfq_response


def request_rfq(component_id: str, quantity: int, supplier_ids: list[str], db: Session) -> ToolResult:
    quotes = []
    for sid in supplier_ids:
        quote = simulate_rfq_response(sid, component_id, quantity)
        row = RFQ(
            supplier_id=sid,
            component_id=component_id,
            quantity=quantity,
            unit_price=quote["unit_price"],
            delivery_days=quote["delivery_days"],
            expedite_available=quote["expedite_available"],
            expedite_fee=quote.get("expedite_fee", 0.0),
        )
        db.add(row)
        quotes.append(quote | {"supplier_id": sid})
    db.commit()

    return ToolResult(
        tool_name="request_rfq",
        success=True,
        data=quotes,
        summary=f"Requested RFQs from {len(supplier_ids)} supplier(s) for {quantity}x {component_id}.",
    )
