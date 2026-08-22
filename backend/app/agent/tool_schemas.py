"""
app/agent/tool_schemas.py
Owner: Developer 1 (Agent) owns the file, but MUST stay in sync with the actual
       function signatures in app/tools/*.py (Developer 2 & 3). If you change a tool's
       parameters, update BOTH the Python function and this schema, plus
       docs/TOOL_SCHEMAS.md.

This is the JSON-schema tool definition list passed to the LLM API's tool-use /
function-calling parameter (Anthropic `tools=[...]` format shown here; adapt shape
if LLM_PROVIDER is switched to OpenAI/Gemini in llm_client.py).

RECEIVES: nothing (static definitions)
DELIVERS: TOOLS list consumed by llm_client.py on every agent turn
"""

TOOLS = [
    {
        "name": "get_inventory",
        "description": "Look up current usable stock and days of supply for a component.",
        "input_schema": {
            "type": "object",
            "properties": {"component_id": {"type": "string"}},
            "required": ["component_id"],
        },
    },
    {
        "name": "get_production_orders",
        "description": "List production orders that depend on a given component, with risk level.",
        "input_schema": {
            "type": "object",
            "properties": {"component_id": {"type": "string"}},
            "required": ["component_id"],
        },
    },
    {
        "name": "get_supplier",
        "description": "Retrieve a supplier's profile: quality score, reliability score, certifications.",
        "input_schema": {
            "type": "object",
            "properties": {"supplier_id": {"type": "string"}},
            "required": ["supplier_id"],
        },
    },
    {
        "name": "send_supplier_message",
        "description": "Send a message to a supplier about a PO and receive their (simulated) reply.",
        "input_schema": {
            "type": "object",
            "properties": {
                "supplier_id": {"type": "string"},
                "po_id": {"type": "string"},
                "message": {"type": "string"},
            },
            "required": ["supplier_id", "po_id", "message"],
        },
    },
    {
        "name": "get_tracking_status",
        "description": "Check simulated carrier tracking status for a purchase order.",
        "input_schema": {
            "type": "object",
            "properties": {"po_id": {"type": "string"}},
            "required": ["po_id"],
        },
    },
    {
        "name": "request_rfq",
        "description": "Request quotes (price, delivery time) from candidate suppliers for a component/quantity.",
        "input_schema": {
            "type": "object",
            "properties": {
                "component_id": {"type": "string"},
                "quantity": {"type": "integer"},
                "supplier_ids": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["component_id", "quantity", "supplier_ids"],
        },
    },
    {
        "name": "build_recovery_plan",
        "description": "Build ranked recovery plan options (incl. split sourcing) from RFQ results, "
                        "validated against budget/quality/delivery/MOQ constraints.",
        "input_schema": {
            "type": "object",
            "properties": {
                "required_quantity": {"type": "integer"},
                "required_cert": {"type": "string"},
                "required_by_days": {"type": "integer"},
            },
            "required": ["required_quantity", "required_by_days"],
        },
    },
    {
        "name": "check_approval",
        "description": "Deterministically check whether a recovery plan's cost requires human approval "
                        "(>$50,000 impact per official rules). NEVER decide this yourself.",
        "input_schema": {
            "type": "object",
            "properties": {"cost": {"type": "number"}},
            "required": ["cost"],
        },
    },
    {
        "name": "update_erp",
        "description": "Execute an approved recovery plan option: writes purchase orders / inventory updates.",
        "input_schema": {
            "type": "object",
            "properties": {
                "incident_id": {"type": "string"},
                "option_id": {"type": "string"},
            },
            "required": ["incident_id", "option_id"],
        },
    },
]

# TODO (Dev1): add check_constraints as a standalone tool if the team decides the agent
# should be able to probe individual constraints separately from full plan-building.
