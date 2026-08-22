"""
app/tools/supplier_tools.py
Owner: Developer 2 (Backend / Simulation)

Two tools:
  - get_supplier(supplier_id)          -> supplier profile lookup
  - send_supplier_message(...)          -> simulated outbound message + simulated reply
  - get_tracking_status(po_id)          -> simulated carrier tracking (for supplier-lie detection)

RECEIVES: identifiers chosen by the agent during INVESTIGATING / SUPPLIER_CONTACT states
DELIVERS: data feeding the SUPPLIER info card and contradiction-detection logic
          (team doc Section 19B: supplier says dispatched, tracking says no pickup scan)
"""

from sqlalchemy.orm import Session
from datetime import datetime

from app.models.suppliers import Supplier
from app.models.supplier_messages import SupplierMessage
from app.schemas.tool_io import ToolResult
from app.simulator.supplier_simulator import simulate_supplier_reply, simulate_tracking_status


def get_supplier(supplier_id: str, db: Session) -> ToolResult:
    row = db.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()
    if not row:
        return ToolResult(tool_name="get_supplier", success=False,
                           error="not found", summary=f"Supplier {supplier_id} not found.")
    return ToolResult(
        tool_name="get_supplier",
        success=True,
        data={
            "supplier_id": row.supplier_id,
            "name": row.name,
            "quality_score": row.quality_score,
            "reliability_score": row.reliability_score,
            "certifications": row.certifications,
        },
        summary=f"Retrieved supplier profile for {row.name} ({row.supplier_id}).",
    )


def send_supplier_message(supplier_id: str, po_id: str, message: str, db: Session) -> ToolResult:
    """
    Sends `message` to the simulated supplier and records both the outbound message
    and the simulated inbound reply in supplier_messages.
    """
    reply_text = simulate_supplier_reply(supplier_id, po_id, message)

    outbound = SupplierMessage(supplier_id=supplier_id, po_id=po_id, message=message, timestamp=datetime.utcnow())
    inbound = SupplierMessage(supplier_id=supplier_id, po_id=po_id, message=reply_text, timestamp=datetime.utcnow())
    db.add(outbound)
    db.add(inbound)
    db.commit()

    return ToolResult(
        tool_name="send_supplier_message",
        success=True,
        data={"reply": reply_text},
        summary=f"Contacted supplier {supplier_id}. Reply: \"{reply_text}\"",
    )


def get_tracking_status(po_id: str, db: Session) -> ToolResult:
    status = simulate_tracking_status(po_id)
    return ToolResult(
        tool_name="get_tracking_status",
        success=True,
        data={"po_id": po_id, "tracking_status": status},
        summary=f"Tracking for {po_id}: {status}",
    )
