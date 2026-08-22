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
    Executes a tool call by name with input parameters and DB session.
    Guards against missing keys or runtime exceptions with graceful ToolResult errors.
    """
    try:
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
            return ToolResult(
                tool_name=tool_name,
                success=False,
                error="build_recovery_plan is orchestrated directly via /agent/plan or n8n workflow",
                summary="Recovery plan generation is handled via workflow orchestrator.",
            )

        if tool_name == "update_erp":
            return ToolResult(
                tool_name=tool_name,
                success=False,
                error="update_erp requires approved RecoveryPlanOption",
                summary="Direct ERP updates require an approved plan option.",
            )

        return ToolResult(
            tool_name=tool_name,
            success=False,
            error=f"Unknown tool '{tool_name}'",
            summary=f"Unknown tool requested: {tool_name}",
        )
    except KeyError as e:
        return ToolResult(
            tool_name=tool_name,
            success=False,
            error=f"Missing required parameter: {e}",
            summary=f"Tool {tool_name} failed: missing required parameter {e}.",
        )
    except Exception as e:
        return ToolResult(
            tool_name=tool_name,
            success=False,
            error=str(e),
            summary=f"Tool {tool_name} encountered an error: {e}",
        )
