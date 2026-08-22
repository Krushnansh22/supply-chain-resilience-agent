"""
app/tools/rfq_tools.py
Owner: Developer 2 (Backend / Simulation), consumed by Developer 3's recovery_planner.py

RECEIVES: component_id, quantity, list of candidate supplier_ids chosen by the agent
DELIVERS: simulated RFQ responses (unit_price, delivery_days, expedite options), persisted
          to app/models/rfqs.py, and returned to the agent for "Requesting alternative
          RFQs" activity log entries.
"""

from datetime import datetime, timezone
from pymongo.database import Database
from app.schemas.tool_io import ToolResult
from app.simulator.supplier_simulator import simulate_rfq_response


def request_rfq(component_id: str, quantity: int, supplier_ids: list[str], db: Database) -> ToolResult:
    quotes = []
    for sid in supplier_ids:
        quote = simulate_rfq_response(sid, component_id, quantity)
        db["rfqs"].insert_one({"supplier_id": sid, "component_id": component_id, "quantity": quantity, **quote, "created_at": datetime.now(timezone.utc)})
        quotes.append(quote | {"supplier_id": sid})

    return ToolResult(
        tool_name="request_rfq",
        success=True,
        data=quotes,
        summary=f"Requested RFQs from {len(supplier_ids)} supplier(s) for {quantity}x {component_id}.",
    )
