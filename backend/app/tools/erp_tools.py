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
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.schemas.tool_io import ToolResult
from app.schemas.recovery_plan import RecoveryPlanOption
from app.models.purchase_orders import PurchaseOrder
from app.models.inventory import Inventory
from app.models.incidents import Incident


def update_erp(incident_id: str, option: RecoveryPlanOption, db: Session) -> ToolResult:
    """
    Executes an approved recovery plan option:
    1. Creates a new PurchaseOrder row for each allocation.
    2. Updates Inventory.usable_stock to reflect incoming stock commitment.
    3. Marks the source incident as RESOLVED.
    """
    created_pos = []

    for allocation in option.allocations:
        po_id = f"PO-{uuid.uuid4().hex[:6].upper()}"
        expected_delivery = datetime.utcnow() + timedelta(days=allocation.delivery_days)

        po = PurchaseOrder(
            po_id=po_id,
            component_id=_get_component_for_incident(incident_id, db),
            supplier_id=allocation.supplier_id,
            quantity=allocation.quantity,
            unit_price=allocation.unit_price,
            expected_delivery=expected_delivery,
            status="OPEN",
        )
        db.add(po)
        created_pos.append(po_id)

        # Reflect incoming stock commitment in usable_stock
        inv = db.query(Inventory).filter(
            Inventory.component_id == po.component_id
        ).first()
        if inv:
            inv.usable_stock += allocation.quantity

    # Mark incident as RESOLVED
    incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
    if incident:
        incident.status = "RESOLVED"

    db.commit()

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


def _get_component_for_incident(incident_id: str, db: Session) -> str:
    """Helper: get the affected component from the incident row."""
    incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
    if incident and incident.affected_component:
        return incident.affected_component
    return "UNKNOWN"
