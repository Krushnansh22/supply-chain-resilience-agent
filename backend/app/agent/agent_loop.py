"""
app/agent/agent_loop.py
Owner: Developer 1 (Agent)

The core orchestration loop: given an incident, drives the agent through the state
machine in states.py, calling tools dynamically (NOT a hardcoded sequence — team doc
Section 2 stresses genuine tool-based agentic behavior) until it reaches PLAN_READY,
then either EXECUTING or WAITING_APPROVAL, and finally RESOLVED. Also handles
REPLANNING when decision_engine/replanning.py detects an active plan is invalidated.

RECEIVES:
  - incident_id (str) from api/routes_agent.py (POST /agent/trigger)
  - DB session
DELIVERS:
  - updates Incident.status to mirror AgentState at every transition
  - writes to audit_logs via audit/audit_logger.log_event() on every tool call/decision
  - returns a summary dict to the API layer -> shown in frontend Agent Activity feed
"""

from pymongo.database import Database
from app.agent.states import AgentState
from app.agent.prompts import build_system_prompt
from app.agent.tool_schemas import TOOLS
from app.agent.llm_client import call_llm
from app.audit.audit_logger import log_event

# Tool name -> implementation, dispatched by tool_executor.py
from app.agent.tool_executor import execute_tool


def get_agent_state(incident_id: str, db: Database) -> str:
  incident = db["incidents"].find_one({"incident_id": incident_id}, {"status": 1})
  return incident.get("status", "UNKNOWN") if incident else "UNKNOWN"


def _set_state(incident: dict, state: AgentState, db: Database):
  db["incidents"].update_one({"incident_id": incident["incident_id"]}, {"$set": {"status": state.value}})


def run_agent_for_incident(incident_id: str, db: Database) -> dict:
    """
    TODO (Dev1): implement the real agentic tool-calling loop. Skeleton below shows
    the intended shape:

        1. Load incident, build system prompt with incident context.
        2. _set_state(DETECTED -> INVESTIGATING); log_event(...)
        3. Loop: call_llm(messages, TOOLS, system_prompt)
             - if response has tool_use blocks: execute_tool(name, input, db),
               log_event() with the tool's `summary`, append tool_result to messages,
               continue loop.
             - if response has only text: treat as the agent's narration/decision,
               log_event() with the decision.
           Track loop-driven state transitions (SUPPLIER_CONTACT once
           send_supplier_message is called, EVALUATING once request_rfq / build_recovery_plan
           is called, PLAN_READY once build_recovery_plan returns, etc.)
        4. Once a RecoveryPlan exists, call check_approval tool via execute_tool.
             - requires_approval True  -> _set_state(WAITING_APPROVAL); STOP loop, return.
             - requires_approval False -> _set_state(EXECUTING); call update_erp tool;
               _set_state(RESOLVED).
        5. Before finalizing, consult decision_engine/replanning.is_plan_invalidated()
           against any other open incidents affecting the same component/supplier;
           if invalidated, _set_state(REPLANNING) and go back to step 3 with a note
           in the prompt about why the previous plan failed.

    Returns a small summary dict — full detail lives in the audit log / DB, not in
    this return value (frontend should poll GET /audit and GET /incidents instead of
    relying on this response being complete).
    """
    incident = db["incidents"].find_one({"incident_id": incident_id}, {"_id": 0})
    if not incident:
        return {"error": "incident not found"}

    _set_state(incident, AgentState.INVESTIGATING, db)
    log_event(db, incident_id, action="Agent started investigating incident.",
              decision=None, reason=None)

    _set_state(incident, AgentState.WAITING_APPROVAL, db)
    log_event(db, incident_id, action="Recovery plan requires coordinator approval.", decision="WAITING_APPROVAL", reason="Demo agent workflow")
    return {"incident_id": incident_id, "state": AgentState.WAITING_APPROVAL.value, "message": "Agent paused for approval."}
