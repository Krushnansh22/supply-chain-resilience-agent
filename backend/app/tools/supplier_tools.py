"""
app/tools/supplier_tools.py
Owner: Developer 2 (Backend / Simulation)

Tools for supplier interactions:
- get_supplier(supplier_id)             -> supplier profile lookup (quality, reliability, certs)
- get_suppliers(component_id)           -> lookup all candidate suppliers for a component
- send_supplier_message(...)            -> simulated outbound message + dynamic reply
- request_clarification(...)            -> challenge vague/contradictory claims with falsifiable questions
- get_tracking_status(po_id)            -> carrier tracking status for contradiction detection
"""

from datetime import datetime, timezone
from typing import Optional
from pymongo.database import Database
from app.schemas.tool_io import ToolResult
from app.simulator.supplier_simulator import (
    simulate_supplier_reply,
    simulate_tracking_status,
)


def get_supplier(supplier_id: str, db: Database) -> ToolResult:
    row = db["suppliers"].find_one({"supplier_id": supplier_id}, {"_id": 0})
    if not row:
        return ToolResult(
            tool_name="get_supplier",
            success=False,
            error=f"Supplier '{supplier_id}' not found",
            summary=f"Supplier {supplier_id} not found.",
        )
    return ToolResult(
        tool_name="get_supplier",
        success=True,
        data={
            "supplier_id": row["supplier_id"],
            "name": row.get("name", supplier_id),
            "quality_score": row.get("quality_score", 70.0),
            "reliability_score": row.get("reliability_score", 70.0),
            "certifications": row.get("certifications", ""),
            "min_order_qty": row.get("min_order_qty", 0),
        },
        summary=f"Retrieved profile for {row.get('name', supplier_id)} (Quality: {row.get('quality_score')}%, Reliability: {row.get('reliability_score')}%).",
    )


def get_suppliers(component_id: Optional[str], db: Database) -> ToolResult:
    """Finds all candidate suppliers (optionally filtered by component history or all known suppliers)."""
    if component_id:
        # Find suppliers associated with POs or RFQs for this component
        po_suppliers = db["purchase_orders"].distinct("supplier_id", {"component_id": component_id})
        rfq_suppliers = db["rfqs"].distinct("supplier_id", {"component_id": component_id})
        supplier_ids = list(set(po_suppliers + rfq_suppliers))
        if supplier_ids:
            suppliers = list(db["suppliers"].find({"supplier_id": {"$in": supplier_ids}}, {"_id": 0}))
        else:
            suppliers = list(db["suppliers"].find({}, {"_id": 0}).limit(6))
    else:
        suppliers = list(db["suppliers"].find({}, {"_id": 0}))

    return ToolResult(
        tool_name="get_suppliers",
        success=True,
        data=suppliers,
        summary=f"Found {len(suppliers)} candidate supplier(s).",
    )


def send_supplier_message(supplier_id: str, po_id: str, message: str, db: Database) -> ToolResult:
    """
    Sends a message to the simulated supplier and records the conversation turn.
    """
    reply_text = simulate_supplier_reply(supplier_id, po_id, message)

    now = datetime.now(timezone.utc)
    db["supplier_messages"].insert_many([
        {
            "message_id": f"MSG-{now.timestamp():.3f}-OUT",
            "supplier_id": supplier_id,
            "po_id": po_id,
            "message": message,
            "direction": "OUTBOUND",
            "timestamp": now,
        },
        {
            "message_id": f"MSG-{now.timestamp():.3f}-IN",
            "supplier_id": supplier_id,
            "po_id": po_id,
            "message": reply_text,
            "direction": "INBOUND",
            "timestamp": datetime.now(timezone.utc),
        },
    ])

    return ToolResult(
        tool_name="send_supplier_message",
        success=True,
        data={"supplier_id": supplier_id, "po_id": po_id, "reply": reply_text},
        summary=f"Contacted supplier {supplier_id}. Reply: \"{reply_text}\"",
    )


def request_clarification(
    supplier_id: str,
    po_id: str,
    question: str,
    previous_claim: Optional[str],
    db: Database,
) -> ToolResult:
    """
    Challenges a vague or contradictory supplier statement with a falsifiable question.
    """
    challenge_prompt = f"CHALLENGE / CLARIFICATION: {question}"
    if previous_claim:
        challenge_prompt += f" (Addressing previous claim: '{previous_claim}')"

    reply_text = simulate_supplier_reply(supplier_id, po_id, challenge_prompt)

    now = datetime.now(timezone.utc)
    db["supplier_messages"].insert_many([
        {
            "message_id": f"MSG-{now.timestamp():.3f}-CHALLENGE",
            "supplier_id": supplier_id,
            "po_id": po_id,
            "message": challenge_prompt,
            "direction": "OUTBOUND_CHALLENGE",
            "timestamp": now,
        },
        {
            "message_id": f"MSG-{now.timestamp():.3f}-CONCESSION",
            "supplier_id": supplier_id,
            "po_id": po_id,
            "message": reply_text,
            "direction": "INBOUND_REVISED",
            "timestamp": datetime.now(timezone.utc),
        },
    ])

    return ToolResult(
        tool_name="request_clarification",
        success=True,
        data={
            "supplier_id": supplier_id,
            "po_id": po_id,
            "question": question,
            "reply": reply_text,
            "challenged_claim": previous_claim,
        },
        summary=f"Challenged supplier {supplier_id} with clarification request. Revised response: \"{reply_text}\"",
    )


def get_tracking_status(po_id: str, db: Database) -> ToolResult:
    """
    Checks simulated carrier tracking status for a purchase order.
    """
    status = simulate_tracking_status(po_id)
    return ToolResult(
        tool_name="get_tracking_status",
        success=True,
        data={"po_id": po_id, "tracking_status": status},
        summary=f"Carrier tracking for {po_id}: {status}.",
    )
