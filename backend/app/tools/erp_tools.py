"""
app/tools/erp_tools.py
Owner: Developer 2 (Backend / Simulation)

The ONLY tool that mutates state in the simulated ERP once a plan is authorized
(either auto-approved under threshold, or human-approved).

RECEIVES: an approved RecoveryPlanOption (schemas/recovery_plan.py) + incident_id
DELIVERS:
  - new PurchaseOrder rows (one per allocation)
  - updated Inventory.usable_stock (marked as incoming stock)
  - Incident.status set to RESOLVED
  - an audit log entry via app/audit/audit_logger.py
  - is the last step before the agent transitions to RESOLVED
"""

import uuid
from datetime import datetime, timedelta, timezone
from pymongo.database import Database

from app.schemas.tool_io import ToolResult
from app.schemas.recovery_plan import RecoveryPlanOption


def update_erp(incident_id: str, option: RecoveryPlanOption, db: Database) -> ToolResult:
    """
    Executes an approved recovery plan option:
    1. Validates the incident exists.
    2. Creates a new PurchaseOrder row for each allocation.
    3. Updates Inventory.usable_stock to reflect incoming stock commitment.
    4. Marks the source incident as RESOLVED.
    """
    incident = db["incidents"].find_one({"incident_id": incident_id})
    if not incident:
        return ToolResult(
            tool_name="update_erp",
            success=False,
            error=f"Incident '{incident_id}' not found.",
            summary=f"ERP update aborted: incident '{incident_id}' does not exist.",
        )

    component_id = incident.get("affected_component") or "UNKNOWN"
    created_pos = []

    for allocation in option.allocations:
        po_id = f"PO-{uuid.uuid4().hex[:6].upper()}"
        expected_delivery = datetime.now(timezone.utc) + timedelta(days=allocation.delivery_days)

        db["purchase_orders"].insert_one({
            "po_id": po_id,
            "component_id": component_id,
            "supplier_id": allocation.supplier_id,
            "quantity": allocation.quantity,
            "unit_price": allocation.unit_price,
            "expected_delivery": expected_delivery,
            "status": "OPEN",
        })
        created_pos.append(po_id)

        # Reflect incoming stock commitment in usable_stock
        if component_id != "UNKNOWN":
            inv = db["inventory"].find_one({"component_id": component_id})
            if inv:
                db["inventory"].update_one(
                    {"component_id": component_id},
                    {"$inc": {"usable_stock": allocation.quantity}},
                )

    # Mark incident as RESOLVED
    db["incidents"].update_one({"incident_id": incident_id}, {"$set": {"status": "RESOLVED"}})

    total_cost = option.total_cost
    return ToolResult(
        tool_name="update_erp",
        success=True,
        data={
            "incident_id": incident_id,
            "option_id": option.option_id,
            "total_cost": total_cost,
            "purchase_orders_created": created_pos,
        },
        summary=(
            f"ERP updated: executed recovery option {option.option_id} for incident "
            f"{incident_id}. Created POs: {', '.join(created_pos)}. "
            f"Total cost: ${total_cost:,.2f}. Incident marked RESOLVED."
        ),
    )


def _get_component_for_incident(incident_id: str, db: Database) -> str:
    """Helper: get the affected component from the incident row."""
    incident = db["incidents"].find_one({"incident_id": incident_id}, {"_id": 0})
    if incident and incident.get("affected_component"):
        return incident["affected_component"]
    return "UNKNOWN"
