"""
app/tools/purchase_tools.py
Owner: Developer 2 (Backend / Simulation)

Tools for inspecting purchase orders:
- get_purchase_orders(component_id, po_id, db) -> lists active POs and status
"""

from typing import Optional
from pymongo.database import Database
from app.schemas.tool_io import ToolResult


def get_purchase_orders(
    component_id: Optional[str] = None,
    po_id: Optional[str] = None,
    db: Database = None,
) -> ToolResult:
    query = {}
    if po_id:
        query["po_id"] = po_id
    elif component_id:
        query["component_id"] = component_id

    rows = list(db["purchase_orders"].find(query, {"_id": 0}))
    for r in rows:
        if r.get("expected_delivery") and hasattr(r["expected_delivery"], "isoformat"):
            r["expected_delivery"] = r["expected_delivery"].isoformat()

    return ToolResult(
        tool_name="get_purchase_orders",
        success=True,
        data=rows,
        summary=f"Found {len(rows)} purchase order(s) for query: {query}.",
    )
