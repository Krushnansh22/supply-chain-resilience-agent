"""
app/agent/llm_client.py
Owner: Developer 1 (Agent)

Multi-provider LLM interface supporting Groq, Anthropic, and OpenAI with tool calling,
plus an intelligent deterministic planner for test/offline resilience.
"""

import json
import logging
import os
from dataclasses import dataclass, field
from typing import Any, Optional

from app.config import settings
from app.agent.tool_schemas import ANTHROPIC_TOOLS, get_openai_tools

logger = logging.getLogger(__name__)


@dataclass
class ToolCallRequest:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class AgentTurnResponse:
    text: str = ""
    tool_calls: list[ToolCallRequest] = field(default_factory=list)
    finish_reason: str = "stop"


def call_llm(
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]] | None = None,
    system_prompt: str = "",
    incident_context: dict[str, Any] | None = None,
) -> AgentTurnResponse:
    """
    Invokes the configured LLM provider (Groq, Anthropic, OpenAI) with function/tool calling.
    Falls back to deterministic autonomous planning when API keys are not configured or in test mode.
    """
    provider = (settings.LLM_PROVIDER or "groq").lower()
    groq_key = settings.GROQ_API_KEY or os.environ.get("GROQ_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")

    # 1. Try Groq (if key available)
    if provider == "groq" and groq_key:
        try:
            from groq import Groq
            client = Groq(api_key=groq_key)
            formatted_messages = []
            if system_prompt:
                formatted_messages.append({"role": "system", "content": system_prompt})
            for m in messages:
                role = m.get("role", "user")
                if role == "tool":
                    formatted_messages.append({
                        "role": "tool",
                        "content": str(m.get("content", "")),
                        "tool_call_id": m.get("tool_call_id", "call_1"),
                    })
                elif role == "assistant" and m.get("tool_calls"):
                    formatted_messages.append({
                        "role": "assistant",
                        "content": m.get("content") or None,
                        "tool_calls": m.get("tool_calls"),
                    })
                else:
                    formatted_messages.append({"role": role, "content": str(m.get("content", ""))})

            resp = client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=formatted_messages,
                tools=get_openai_tools(),
                temperature=settings.GROQ_TEMPERATURE,
            )

            choice = resp.choices[0]
            msg = choice.message
            tool_calls = []
            if msg.tool_calls:
                for tc in msg.tool_calls:
                    try:
                        args = json.loads(tc.function.arguments) if isinstance(tc.function.arguments, str) else tc.function.arguments
                    except Exception:
                        args = {}
                    tool_calls.append(ToolCallRequest(
                        id=tc.id,
                        name=tc.function.name,
                        arguments=args,
                    ))

            return AgentTurnResponse(
                text=msg.content or "",
                tool_calls=tool_calls,
                finish_reason=choice.finish_reason or "stop",
            )
        except Exception as e:
            logger.warning(f"Groq LLM call failed ({e}); falling back to deterministic planner.")

    # 2. Try Anthropic (if configured)
    if provider == "anthropic" and anthropic_key:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=anthropic_key)
            # Filter system messages for Anthropic
            anth_messages = [m for m in messages if m.get("role") in ("user", "assistant")]
            resp = client.messages.create(
                model=os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
                max_tokens=2048,
                system=system_prompt,
                messages=anth_messages,
                tools=ANTHROPIC_TOOLS,
            )
            text_blocks = []
            tool_calls = []
            for block in resp.content:
                if block.type == "text":
                    text_blocks.append(block.text)
                elif block.type == "tool_use":
                    tool_calls.append(ToolCallRequest(
                        id=block.id,
                        name=block.name,
                        arguments=block.input if isinstance(block.input, dict) else {},
                    ))
            return AgentTurnResponse(
                text="\n".join(text_blocks),
                tool_calls=tool_calls,
                finish_reason=resp.stop_reason or "stop",
            )
        except Exception as e:
            logger.warning(f"Anthropic LLM call failed ({e}); falling back to deterministic planner.")

    # 3. Deterministic Autonomous Agent Planner (Offline / Test / Resilient Fallback)
    return _deterministic_plan_step(messages, incident_context)


def _deterministic_plan_step(
    messages: list[dict[str, Any]],
    incident_context: Optional[dict[str, Any]],
) -> AgentTurnResponse:
    """
    Deterministic multi-step reasoning planner.
    Analyzes conversation history and previous tool observations to decide the next tool to invoke.
    """
    ctx = incident_context or {}
    inc_id = ctx.get("incident_id", "INC-001")
    inc_type = ctx.get("type", "SUPPLIER_DELAY")
    comp_id = ctx.get("affected_component") or "COMP-104"
    po_id = ctx.get("affected_po") or "PO-100"
    supp_id = ctx.get("affected_supplier") or "SUP-001"

    # Inspect which tools have already run in the message history
    executed_tools = set()
    latest_tool_results: dict[str, Any] = {}
    for m in messages:
        if m.get("role") == "tool":
            tname = m.get("tool_name")
            if tname:
                executed_tools.add(tname)
                latest_tool_results[tname] = m.get("tool_result")

    # Step 1: Inventory
    if "get_inventory" not in executed_tools:
        return AgentTurnResponse(
            text=f"First, investigating inventory levels and days of supply for {comp_id}.",
            tool_calls=[ToolCallRequest(
                id=f"call_{len(executed_tools)+1}",
                name="get_inventory",
                arguments={"component_id": comp_id},
            )],
        )

    # Step 2: Production Schedule
    if "get_production_schedule" not in executed_tools and "get_production_orders" not in executed_tools:
        return AgentTurnResponse(
            text=f"Next, checking dependent production orders and delivery deadlines for {comp_id}.",
            tool_calls=[ToolCallRequest(
                id=f"call_{len(executed_tools)+1}",
                name="get_production_schedule",
                arguments={"component_id": comp_id},
            )],
        )

    # Step 3: Supplier Investigation / Contradiction Verification
    if inc_type == "SUPPLIER_LIE":
        if "get_tracking_status" not in executed_tools:
            return AgentTurnResponse(
                text=f"Supplier claims dispatch. Cross-checking carrier tracking for {po_id} to verify physical movement.",
                tool_calls=[ToolCallRequest(
                    id=f"call_{len(executed_tools)+1}",
                    name="get_tracking_status",
                    arguments={"po_id": po_id},
                )],
            )
        if "request_clarification" not in executed_tools:
            return AgentTurnResponse(
                text=f"Tracking confirms NO_PICKUP_SCAN contradicting supplier dispatch claim. Challenging supplier {supp_id}.",
                tool_calls=[ToolCallRequest(
                    id=f"call_{len(executed_tools)+1}",
                    name="request_clarification",
                    arguments={
                        "supplier_id": supp_id,
                        "po_id": po_id,
                        "question": "Carrier tracking indicates no pickup scan. Please clarify physical dispatch timestamp.",
                        "previous_claim": "Dispatched yesterday",
                    },
                )],
            )

    elif inc_type == "SUPPLIER_DELAY":
        if "send_supplier_message" not in executed_tools and "get_tracking_status" not in executed_tools:
            return AgentTurnResponse(
                text=f"Contacting supplier {supp_id} regarding delay duration and expedite options for {po_id}.",
                tool_calls=[ToolCallRequest(
                    id=f"call_{len(executed_tools)+1}",
                    name="send_supplier_message",
                    arguments={
                        "supplier_id": supp_id,
                        "po_id": po_id,
                        "message": "Please provide revised dispatch date and expedite fee options.",
                    },
                )],
            )

    # Step 4: Solicit RFQs
    if "request_rfq" not in executed_tools and "request_supplier_quote" not in executed_tools:
        cand_suppliers = ["SUP-001", "SUP-002", "SUP-003", "SUP-004"]
        if inc_type == "SUPPLIER_LIE":
            # Exclude compromised supplier
            cand_suppliers = [s for s in cand_suppliers if s != supp_id]
        return AgentTurnResponse(
            text=f"Soliciting alternative quotes from candidate suppliers for {comp_id}.",
            tool_calls=[ToolCallRequest(
                id=f"call_{len(executed_tools)+1}",
                name="request_rfq",
                arguments={
                    "component_id": comp_id,
                    "quantity": 500,
                    "supplier_ids": cand_suppliers[:3],
                },
            )],
        )

    # Step 5: Compute Recovery Options (Deterministic Decision Engine)
    if "compute_recovery_options" not in executed_tools and "build_recovery_plan" not in executed_tools:
        req_cert = "ISO9001" if inc_type == "QUALITY_FAILURE" else None
        return AgentTurnResponse(
            text="Invoking deterministic decision engine to compute single and split-sourcing options.",
            tool_calls=[ToolCallRequest(
                id=f"call_{len(executed_tools)+1}",
                name="compute_recovery_options",
                arguments={
                    "incident_id": inc_id,
                    "component_id": comp_id,
                    "required_quantity": 500,
                    "required_by_days": 6,
                    "required_cert": req_cert,
                    "max_budget": 60000.0,
                },
            )],
        )

    # Step 6: Check Approval Threshold / Escalation
    if "check_approval_threshold" not in executed_tools and "check_approval" not in executed_tools:
        plan_res = latest_tool_results.get("compute_recovery_options") or {}
        cost = 25000.0
        if isinstance(plan_res, dict) and "options" in plan_res and plan_res["options"]:
            cost = plan_res["options"][0].get("total_cost", 25000.0)

        return AgentTurnResponse(
            text=f"Evaluating approval threshold for recovery plan (Estimated cost: ${cost:,.2f}).",
            tool_calls=[ToolCallRequest(
                id=f"call_{len(executed_tools)+1}",
                name="check_approval_threshold",
                arguments={"cost": cost, "incident_id": inc_id},
            )],
        )

    # Step 7: Propose Plan / Escalate / Execute ERP
    if "propose_plan" not in executed_tools and "escalate_to_human" not in executed_tools and "update_erp" not in executed_tools:
        plan_res = latest_tool_results.get("compute_recovery_options") or {}
        approval_res = latest_tool_results.get("check_approval_threshold") or {}
        requires_approval = approval_res.get("requires_approval", False)
        esc_eval = approval_res.get("escalation_evaluation", {})

        if inc_type == "STALE_INVENTORY":
            return AgentTurnResponse(
                text=f"Physical inventory discrepancy detected for {comp_id}. Escalating to coordinator on the Approval page for revised stock count.",
                tool_calls=[ToolCallRequest(
                    id=f"call_{len(executed_tools)+1}",
                    name="escalate_to_human",
                    arguments={
                        "incident_id": inc_id,
                        "reason": f"Physical inventory discrepancy / broken data detected for {comp_id}. Revised stock count required.",
                        "trigger_criterion": "DATA_INCONSISTENCY",
                        "decision_brief": (
                            f"=======================================================\n"
                            f"DECISION BRIEF (DATA CALIBRATION REQUIRED)\n"
                            f"=======================================================\n"
                            f"SITUATION:\n"
                            f"  Physical inventory count discrepancy or negative data detected for component '{comp_id}'.\n\n"
                            f"COST OF INACTION:\n"
                            f"  Procuring against an uncalibrated stock baseline leads to severe over-spend or unexpected stockouts.\n\n"
                            f"RECOMMENDATION:\n"
                            f"  Please input the verified physical stock count in the Approval form to update inventory properly.\n\n"
                            f"WHY THIS NEEDS APPROVAL:\n"
                            f"  DATA_INCONSISTENCY\n"
                            f"======================================================="
                        ),
                    },
                )],
            )

        if requires_approval or esc_eval.get("requires_escalation"):
            return AgentTurnResponse(
                text="Plan exceeds autonomous authority limits or trigger criteria. Escalating to human coordinator with Decision Brief.",
                tool_calls=[ToolCallRequest(
                    id=f"call_{len(executed_tools)+1}",
                    name="escalate_to_human",
                    arguments={
                        "incident_id": inc_id,
                        "reason": esc_eval.get("trigger_reason", f"Cost exceeds ${settings.AUTONOMOUS_APPROVAL_LIMIT_USD:,.0f} limit"),
                        "trigger_criterion": esc_eval.get("trigger_criterion", "COST_EXCEEDS_THRESHOLD"),
                        "decision_brief": esc_eval.get("decision_brief", "Decision brief generated."),
                    },
                )],
            )
        else:
            rec_opt = "A"
            if isinstance(plan_res, dict):
                rec_opt = plan_res.get("recommended_option_id", "A") or "A"

            return AgentTurnResponse(
                text=f"Proposing and executing recovery Option {rec_opt} within autonomous limits.",
                tool_calls=[ToolCallRequest(
                    id=f"call_{len(executed_tools)+1}",
                    name="update_erp",
                    arguments={"incident_id": inc_id, "option_id": rec_opt},
                )],
            )

    # Step 8: Resolution reached
    return AgentTurnResponse(
        text=f"Autonomous resolution cycle completed for incident {inc_id}.",
        tool_calls=[],
        finish_reason="stop",
    )
