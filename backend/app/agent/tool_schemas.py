"""
app/agent/tool_schemas.py
Owner: Developer 1 (Agent)

Canonical tool schema definitions for LLM tool calling / function calling.
Provides formats for Anthropic, Groq, and OpenAI APIs.
"""

# Anthropic format tool definitions
ANTHROPIC_TOOLS = [
    {
        "name": "get_inventory",
        "description": "Look up current usable stock, daily consumption rate, safety stock, and days of supply for a component.",
        "input_schema": {
            "type": "object",
            "properties": {"component_id": {"type": "string", "description": "The component identifier (e.g. COMP-104)"}},
            "required": ["component_id"],
        },
    },
    {
        "name": "get_purchase_orders",
        "description": "List active purchase orders for a component or inspect a specific PO status and expected delivery.",
        "input_schema": {
            "type": "object",
            "properties": {
                "component_id": {"type": "string", "description": "Filter POs by component ID"},
                "po_id": {"type": "string", "description": "Specific PO identifier"},
            },
        },
    },
    {
        "name": "get_production_schedule",
        "description": "List all production orders that depend on a component, with priority, deadline, and risk level.",
        "input_schema": {
            "type": "object",
            "properties": {"component_id": {"type": "string", "description": "Component identifier"}},
            "required": ["component_id"],
        },
    },
    {
        "name": "get_supplier",
        "description": "Retrieve a supplier profile including quality score, reliability score, and ISO/quality certifications.",
        "input_schema": {
            "type": "object",
            "properties": {"supplier_id": {"type": "string", "description": "Supplier identifier (e.g. SUP-001)"}},
            "required": ["supplier_id"],
        },
    },
    {
        "name": "get_suppliers",
        "description": "Find candidate suppliers that can supply a given component.",
        "input_schema": {
            "type": "object",
            "properties": {"component_id": {"type": "string", "description": "Component identifier"}},
        },
    },
    {
        "name": "request_rfq",
        "description": "Request formal quotes (unit price, delivery time, MOQ, expedite fee) from candidate suppliers.",
        "input_schema": {
            "type": "object",
            "properties": {
                "component_id": {"type": "string", "description": "Component identifier"},
                "quantity": {"type": "integer", "description": "Quantity required"},
                "supplier_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of candidate supplier IDs to solicit",
                },
            },
            "required": ["component_id", "quantity", "supplier_ids"],
        },
    },
    {
        "name": "send_supplier_message",
        "description": "Send an operational inquiry message to a supplier about a PO and receive their simulated response.",
        "input_schema": {
            "type": "object",
            "properties": {
                "supplier_id": {"type": "string", "description": "Supplier identifier"},
                "po_id": {"type": "string", "description": "Purchase order identifier"},
                "message": {"type": "string", "description": "Inquiry text to send"},
            },
            "required": ["supplier_id", "po_id", "message"],
        },
    },
    {
        "name": "request_clarification",
        "description": "Challenge a vague, unverified, or contradictory supplier claim with a specific, falsifiable question.",
        "input_schema": {
            "type": "object",
            "properties": {
                "supplier_id": {"type": "string", "description": "Supplier identifier"},
                "po_id": {"type": "string", "description": "Purchase order identifier"},
                "question": {"type": "string", "description": "Specific question or challenge"},
                "previous_claim": {"type": "string", "description": "The prior claim being challenged"},
            },
            "required": ["supplier_id", "po_id", "question"],
        },
    },
    {
        "name": "get_tracking_status",
        "description": "Check simulated carrier tracking status for a PO to independently verify dispatch/transit claims.",
        "input_schema": {
            "type": "object",
            "properties": {"po_id": {"type": "string", "description": "Purchase order identifier"}},
            "required": ["po_id"],
        },
    },
    {
        "name": "compute_recovery_options",
        "description": "Execute deterministic decision engine math to compute ranked single and split-order recovery plans against constraints.",
        "input_schema": {
            "type": "object",
            "properties": {
                "component_id": {"type": "string", "description": "Component identifier"},
                "required_quantity": {"type": "integer", "description": "Units required"},
                "required_by_days": {"type": "integer", "description": "SLA deadline in days"},
                "required_cert": {"type": "string", "description": "Optional required quality cert (e.g. ISO9001)"},
                "max_budget": {"type": "number", "description": "Maximum budget ceiling in USD"},
            },
            "required": ["component_id", "required_quantity", "required_by_days"],
        },
    },
    {
        "name": "propose_plan",
        "description": "Select a recovery plan option (single or split sourcing) and provide explicit trade-off rationale.",
        "input_schema": {
            "type": "object",
            "properties": {
                "incident_id": {"type": "string", "description": "Incident identifier"},
                "option_id": {"type": "string", "description": "Chosen option ID (e.g. A, B, C)"},
                "justification": {"type": "string", "description": "Detailed reasoning comparing cost, SLA, quality, and risk"},
            },
            "required": ["incident_id", "option_id", "justification"],
        },
    },
    {
        "name": "check_approval_threshold",
        "description": "Deterministically check if a plan cost or situation requires human coordinator approval.",
        "input_schema": {
            "type": "object",
            "properties": {
                "cost": {"type": "number", "description": "Total recovery plan cost in USD"},
                "incident_id": {"type": "string", "description": "Incident identifier"},
            },
            "required": ["cost"],
        },
    },
    {
        "name": "update_erp",
        "description": "Execute an authorized recovery plan: create purchase orders in ERP, adjust inventory commitments, mark incident RESOLVED.",
        "input_schema": {
            "type": "object",
            "properties": {
                "incident_id": {"type": "string", "description": "Incident identifier"},
                "option_id": {"type": "string", "description": "Option ID to execute"},
            },
            "required": ["incident_id", "option_id"],
        },
    },
    {
        "name": "escalate_to_human",
        "description": "Escalate the incident to a human operations coordinator with a structured Decision Brief.",
        "input_schema": {
            "type": "object",
            "properties": {
                "incident_id": {"type": "string", "description": "Incident identifier"},
                "reason": {"type": "string", "description": "Reason for escalation"},
                "trigger_criterion": {
                    "type": "string",
                    "enum": [
                        "COST_EXCEEDS_THRESHOLD",
                        "NO_SUPPLIER_MEETS_DEADLINE",
                        "HIGH_QUALITY_RISK",
                        "SERIOUS_MULTI_OBJECTIVE_TRADEOFFS",
                        "UNAVOIDABLE_PRODUCTION_SHUTDOWN",
                        "BUDGET_EXHAUSTED",
                    ],
                    "description": "Which specific criterion triggered escalation",
                },
                "decision_brief": {"type": "string", "description": "Structured Decision Brief"},
            },
            "required": ["incident_id", "reason", "trigger_criterion"],
        },
    },
    {
        "name": "replan_incident",
        "description": "Trigger mid-flight replanning when new disruption facts invalidate an active plan.",
        "input_schema": {
            "type": "object",
            "properties": {
                "incident_id": {"type": "string", "description": "Incident identifier"},
                "invalidation_reason": {"type": "string", "description": "Why the prior plan was invalidated"},
                "affected_supplier": {"type": "string", "description": "Supplier to exclude or avoid"},
            },
            "required": ["incident_id", "invalidation_reason"],
        },
    },
]

# Alias for backwards compatibility
TOOLS = ANTHROPIC_TOOLS


def get_openai_tools() -> list[dict]:
    """Converts tools into OpenAI / Groq tool-calling format."""
    openai_tools = []
    for tool in ANTHROPIC_TOOLS:
        openai_tools.append({
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["input_schema"],
            },
        })
    return openai_tools
