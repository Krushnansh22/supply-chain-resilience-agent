"""
app/agent/agent_loop.py
Owner: Developer 1 (Agent)

GENUINE MULTI-STEP AGENTIC CONTROLLER (PS Section 4):
Owns the full multi-step reasoning loop inside FastAPI:
  Observe incident -> Decompose tasks -> Decide next tool -> Execute tool ->
  Observe result -> Reason -> ... -> Resolve / Escalate / Replan.

Replaces the single-classification n8n workflow with a true autonomous operations controller.
"""

from typing import Any, Optional
from datetime import datetime, timezone
from pymongo.database import Database

from app.agent.states import AgentState
from app.agent.task_decomposer import (
    decompose_incident,
    persist_tasks,
    update_task_status,
    get_tasks_for_incident,
    TaskStatus,
)
from app.agent.prompts import build_system_prompt, build_incident_user_prompt
from app.agent.llm_client import call_llm
from app.agent.tool_executor import execute_tool
from app.agent.escalation_engine import evaluate_escalation, EscalationCriterion
from app.audit.audit_logger import log_event, get_incident_audit_trail


def get_agent_state(incident_id: str, db: Database) -> str:
    """Retrieves current incident status string."""
    incident = db["incidents"].find_one({"incident_id": incident_id}, {"status": 1})
    return incident.get("status", "UNKNOWN") if incident else "UNKNOWN"


def _set_state(incident_id: str, state: AgentState, db: Database) -> None:
    db["incidents"].update_one(
        {"incident_id": incident_id},
        {"$set": {"status": state.value, "updated_at": datetime.now(timezone.utc)}},
    )
    db["agent_sessions"].update_one(
        {"incident_id": incident_id},
        {
            "$set": {
                "incident_id": incident_id,
                "state": state.value,
                "updated_at": datetime.now(timezone.utc),
            },
            "$inc": {"revision": 1},
        },
        upsert=True,
    )


def run_agent_cycle(
    incident_id: str,
    db: Database,
    max_steps: int = 15,
    trigger_reason: str = "Disruption detected",
    replan_context: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """
    Executes the autonomous multi-step reasoning loop for an incident.

    1. Loads incident and transitions state to INVESTIGATING (or REPLANNING).
    2. Emits dynamic task decomposition tailored to incident type and severity.
    3. Iteratively calls the LLM with tool schemas, executes returned tools, and updates state.
    4. Evaluates multi-criteria escalation or autonomous ERP resolution.
    5. Produces a verifiable, rich audit trail and returns final resolution summary.
    """
    incident = db["incidents"].find_one({"incident_id": incident_id}, {"_id": 0})
    if not incident:
        return {"error": "incident not found", "incident_id": incident_id}

    # Step 1: Initialize lifecycle state
    initial_state = AgentState.REPLANNING if replan_context else AgentState.INVESTIGATING
    _set_state(incident_id, initial_state, db)

    # Step 2: Dynamic Task Decomposition
    tasks = decompose_incident(
        incident_id=incident_id,
        incident_type=incident.get("type", "SUPPLIER_DELAY"),
        severity=incident.get("severity", "HIGH"),
        component_id=incident.get("affected_component"),
        po_id=incident.get("affected_po"),
        supplier_id=incident.get("affected_supplier"),
        context=replan_context,
    )
    persist_tasks(incident_id, tasks, db)

    action_msg = (
        f"Replanning cycle initiated: {trigger_reason}. Dynamic task decomposition refreshed."
        if replan_context else
        f"Agent loop initiated ({trigger_reason}). Dynamic task decomposition generated with {len(tasks)} subtasks."
    )
    log_event(
        db,
        incident_id=incident_id,
        action=action_msg,
        decision=initial_state.value,
        reason=trigger_reason,
        step_index=0,
    )

    # Step 3: Build conversation context
    system_prompt = build_system_prompt()
    user_prompt = build_incident_user_prompt(incident, tasks, replan_context)
    messages: list[dict[str, Any]] = [{"role": "user", "content": user_prompt}]

    step_count = 0
    terminal_reached = False
    final_decision = initial_state.value
    decision_brief = None

    # Step 4: Multi-Step Reason & Act Loop
    while step_count < max_steps and not terminal_reached:
        step_count += 1

        turn = call_llm(
            messages=messages,
            system_prompt=system_prompt,
            incident_context=incident,
        )

        if not turn.tool_calls:
            if turn.text:
                messages.append({"role": "assistant", "content": turn.text})
            break

        # Process tool calls
        assistant_msg: dict[str, Any] = {
            "role": "assistant",
            "content": turn.text or None,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.name, "arguments": tc.arguments},
                }
                for tc in turn.tool_calls
            ],
        }
        messages.append(assistant_msg)

        for tc in turn.tool_calls:
            # Execute tool
            tool_res = execute_tool(tc.name, tc.arguments, db)

            # Match and update task decomposition status
            matched = False
            for t in tasks:
                if t.get("assigned_tool") == tc.name and t["status"] == TaskStatus.PENDING:
                    update_task_status(
                        incident_id=incident_id,
                        task_id=t["task_id"],
                        status=TaskStatus.COMPLETED if tool_res.success else TaskStatus.FAILED,
                        result_summary=tool_res.summary,
                        db=db,
                    )
                    t["status"] = TaskStatus.COMPLETED if tool_res.success else TaskStatus.FAILED
                    t["result_summary"] = tool_res.summary
                    matched = True
                    break
            if not matched:
                for t in tasks:
                    if t["status"] == TaskStatus.PENDING:
                        update_task_status(
                            incident_id=incident_id,
                            task_id=t["task_id"],
                            status=TaskStatus.COMPLETED if tool_res.success else TaskStatus.FAILED,
                            result_summary=tool_res.summary,
                            db=db,
                        )
                        t["status"] = TaskStatus.COMPLETED if tool_res.success else TaskStatus.FAILED
                        t["result_summary"] = tool_res.summary
                        break

            # Rich Audit Logging
            data_sources = []
            if "component_id" in tc.arguments:
                data_sources.append(f"component:{tc.arguments['component_id']}")
            if "po_id" in tc.arguments:
                data_sources.append(f"po:{tc.arguments['po_id']}")
            if "supplier_id" in tc.arguments:
                data_sources.append(f"supplier:{tc.arguments['supplier_id']}")

            calculations = []
            if tc.name in ("compute_recovery_options", "build_recovery_plan"):
                calculations.append({
                    "tool": "recovery_planner.build_recovery_plan",
                    "inputs": tc.arguments,
                    "recommended_option": tool_res.data.get("recommended_option_id") if isinstance(tool_res.data, dict) else None,
                })

            log_event(
                db,
                incident_id=incident_id,
                action=f"Step {step_count}: Executed {tc.name}",
                tool=tc.name,
                result=tool_res.summary,
                decision=None,
                reason=turn.text,
                thought=turn.text,
                tool_args=tc.arguments,
                step_index=step_count,
                data_sources_checked=data_sources,
                calculations_performed=calculations if calculations else None,
            )

            # Append tool result to conversation history
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "tool_name": tc.name,
                "tool_result": tool_res.data if tool_res.success else {"error": tool_res.error},
                "content": tool_res.summary,
            })

            # Check if terminal tool was executed
            if tc.name == "update_erp" and tool_res.success:
                _set_state(incident_id, AgentState.RESOLVED, db)
                terminal_reached = True
                final_decision = AgentState.RESOLVED.value
            elif tc.name == "escalate_to_human":
                _set_state(incident_id, AgentState.WAITING_APPROVAL, db)
                terminal_reached = True
                final_decision = AgentState.WAITING_APPROVAL.value
                decision_brief = tc.arguments.get("decision_brief")

    # Step 5: Handle step budget exhaustion
    if not terminal_reached and step_count >= max_steps:
        esc_eval = evaluate_escalation(
            incident_id=incident_id,
            incident_type=incident.get("type", "SUPPLIER_DELAY"),
            severity=incident.get("severity", "HIGH"),
            component_id=incident.get("affected_component"),
            budget_exhausted=True,
        )
        _set_state(incident_id, AgentState.WAITING_APPROVAL, db)
        db["incidents"].update_one(
            {"incident_id": incident_id},
            {"$set": {
                "escalation_reason": esc_eval.trigger_reason,
                "escalation_criterion": EscalationCriterion.BUDGET_EXHAUSTED,
                "decision_brief": esc_eval.decision_brief,
            }},
        )
        log_event(
            db,
            incident_id=incident_id,
            action="Step limit budget exhausted. Escalated to human coordinator.",
            tool="agent_loop",
            decision="WAITING_APPROVAL",
            reason=esc_eval.trigger_reason,
            step_index=step_count + 1,
            escalation_details={"criterion": EscalationCriterion.BUDGET_EXHAUSTED, "decision_brief": esc_eval.decision_brief},
        )
        final_decision = AgentState.WAITING_APPROVAL.value
        decision_brief = esc_eval.decision_brief

    # Step 6: Assemble final rich response
    latest_incident = db["incidents"].find_one({"incident_id": incident_id}, {"_id": 0})
    latest_tasks = get_tasks_for_incident(incident_id, db)
    audit_trail = get_incident_audit_trail(incident_id, db)
    plan = db["recovery_plans"].find_one({"incident_id": incident_id}, {"_id": 0})

    component_id = incident.get("affected_component")
    inventory = db["inventory"].find_one({"component_id": component_id}, {"_id": 0}) if component_id else None
    production_orders = list(db["production_orders"].find({"component_id": component_id}, {"_id": 0}).limit(5)) if component_id else []

    requires_approval = (final_decision == AgentState.WAITING_APPROVAL.value)

    return {
        "incident_id": incident_id,
        "state": latest_incident.get("status", final_decision) if latest_incident else final_decision,
        "decision": final_decision,
        "steps_executed": step_count,
        "tasks": latest_tasks,
        "requires_human_approval": requires_approval,
        "decision_brief": decision_brief or (latest_incident.get("decision_brief") if latest_incident else None),
        "recovery_plan": plan,
        "audit_trail_count": len(audit_trail),
        "incident": latest_incident,
        "context": {
            "component_id": component_id,
            "inventory": inventory,
            "production_orders": production_orders,
        },
        "message": f"Agent loop completed with state: {final_decision}.",
    }


def run_agent_for_incident(incident_id: str, db: Database) -> dict[str, Any]:
    """
    Main entry point for agent execution.
    Maintains full backwards compatibility while running the true multi-step agent loop.
    """
    return run_agent_cycle(incident_id, db)
