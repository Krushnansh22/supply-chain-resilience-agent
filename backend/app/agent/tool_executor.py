"""
app/agent/tool_executor.py
Owner: Developer 1 (Agent) owns the dispatch table; the underlying functions are
       owned by Developer 2 (I/O) and Developer 3 (business logic) in app/tools/*.

Maps a tool name (string, as chosen by the LLM) to the actual Python function call,
injecting the DB session. This is the ONLY place that should need updating when a
new tool is added — plus tool_schemas.py and docs/TOOL_SCHEMAS.md.

RECEIVES: tool_name (str) + input dict (from the LLM's tool_use block) + DB session
DELIVERS: schemas/tool_io.ToolResult, returned to agent_loop.py to feed back into the
          LLM conversation and into audit logging.
"""

from pymongo.database import Database

from app.tools import inventory_tools, production_tools, supplier_tools, rfq_tools, approval_tools, erp_tools
from app.schemas.tool_io import ToolResult


def execute_tool(tool_name: str, tool_input: dict, db: Database) -> ToolResult:
    """
    TODO (Dev1): expand this dispatch table as tools are finalized. `build_recovery_plan`
    is intentionally more involved since it needs RFQ rows already persisted by a prior
    request_rfq call — coordinate the exact flow with Dev3.
    """
    if tool_name == "get_inventory":
        return inventory_tools.get_inventory(tool_input["component_id"], db)

    if tool_name == "get_production_orders":
        return production_tools.get_production_orders(tool_input["component_id"], db)

    if tool_name == "get_supplier":
        return supplier_tools.get_supplier(tool_input["supplier_id"], db)

    if tool_name == "send_supplier_message":
        return supplier_tools.send_supplier_message(
            tool_input["supplier_id"], tool_input["po_id"], tool_input["message"], db
        )

    if tool_name == "get_tracking_status":
        return supplier_tools.get_tracking_status(tool_input["po_id"], db)

    if tool_name == "request_rfq":
        return rfq_tools.request_rfq(
            tool_input["component_id"], tool_input["quantity"], tool_input["supplier_ids"], db
        )

    if tool_name == "check_approval":
        return approval_tools.check_approval(tool_input["cost"])

    if tool_name == "build_recovery_plan":
        # TODO (Dev1 + Dev3): fetch relevant RFQ rows for this incident's component,
        # call decision_engine.recovery_planner.build_recovery_plan(), wrap result in ToolResult.
        raise NotImplementedError("TODO: wire build_recovery_plan tool to recovery_planner.py")

    if tool_name == "update_erp":
        # TODO (Dev1 + Dev2): look up the RecoveryPlanOption by option_id (needs to be
        # cached/stored somewhere after build_recovery_plan — e.g. in-memory dict keyed
        # by incident_id, or a new DB table; decide with Dev2/Dev3) then call erp_tools.update_erp.
        raise NotImplementedError("TODO: wire update_erp tool")

    return ToolResult(tool_name=tool_name, success=False, error="unknown tool",
                       summary=f"Unknown tool requested: {tool_name}")
