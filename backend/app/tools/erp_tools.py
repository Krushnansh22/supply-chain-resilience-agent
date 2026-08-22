"""
app/tools/erp_tools.py
Owner: Developer 2 (Backend / Simulation)

The ONLY tool that mutates state in the simulated ERP once a plan is authorized
(either auto-approved under threshold, or human-approved).

RECEIVES: an approved RecoveryPlanOption (schemas/recovery_plan.py) + incident_id
DELIVERS:
  - updated `inventory` / `purchase_orders` rows
  - an audit log entry via app/audit/audit_logger.py
  - is the last step before the agent transitions to RESOLVED
"""

from sqlalchemy.orm import Session

from app.schemas.tool_io import ToolResult
from app.schemas.recovery_plan import RecoveryPlanOption


def update_erp(incident_id: str, option: RecoveryPlanOption, db: Session) -> ToolResult:
    """
    TODO (Dev2): implement actual DB writes:
      1. For each allocation in option.allocations, create/update a PurchaseOrder row.
      2. Optionally adjust Inventory.usable_stock if this is treated as an immediate
         stock correction rather than an incoming PO (confirm with Dev3).
      3. Mark the source incident's status as RESOLVED (or however agent_loop signals it).
    """
    # Placeholder no-op so the rest of the pipeline can be wired/tested end-to-end
    # before this is implemented for real.
    total_cost = option.total_cost
    return ToolResult(
        tool_name="update_erp",
        success=True,
        data={"incident_id": incident_id, "option_id": option.option_id, "total_cost": total_cost},
        summary=f"ERP updated: executed recovery option {option.option_id} for incident {incident_id}.",
    )
