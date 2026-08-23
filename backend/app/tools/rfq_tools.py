"""
app/tools/rfq_tools.py
Owner: Developer 2 (Backend / Simulation)

Tools for soliciting and managing RFQs (Requests for Quote):
- request_rfq(component_id, quantity, supplier_ids, db) -> gathers quotes and supplier profiles
"""

from datetime import datetime, timezone
from pymongo.database import Database
from app.schemas.tool_io import ToolResult
from app.simulator.supplier_simulator import simulate_rfq_response


def request_rfq(
    component_id: str,
    quantity: int,
    supplier_ids: list[str],
    db: Database,
) -> ToolResult:
    """
    Requests synthetic RFQs from candidate suppliers and merges their supplier profile data.
    """
    quotes = []
    now = datetime.now(timezone.utc)

    for sid in supplier_ids:
        raw_quote = simulate_rfq_response(sid, component_id, quantity)
        # Fetch supplier profile details for comprehensive evaluation
        supp_row = db["suppliers"].find_one({"supplier_id": sid}, {"_id": 0}) or {}

        quote_data = {
            "supplier_id": sid,
            "component_id": component_id,
            "quantity": quantity,
            "unit_price": raw_quote["unit_price"],
            "delivery_days": raw_quote["delivery_days"],
            "expedite_available": raw_quote.get("expedite_available", False),
            "expedite_fee": raw_quote.get("expedite_fee", 0.0),
            "moq": supp_row.get("min_order_qty", raw_quote.get("moq", 0)),
            "quality_score": supp_row.get("quality_score", 75.0),
            "reliability_score": supp_row.get("reliability_score", 75.0),
            "certifications": supp_row.get("certifications", ""),
            "created_at": now,
        }

        db["rfqs"].insert_one({**quote_data})
        # Remove Mongo ObjectId reference for JSON serialization
        quote_data.pop("_id", None)
        quotes.append(quote_data)

    return ToolResult(
        tool_name="request_rfq",
        success=True,
        data=quotes,
        summary=f"Obtained quotes from {len(supplier_ids)} supplier(s) for {quantity}x {component_id}.",
    )
