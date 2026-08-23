"""
app/agent/queue_processor.py
Owner: Developer 1 (Agent) / Developer 2 (Backend)

GLOBAL AUTONOMOUS AGENT QUEUE PROCESSOR:
Operates as the central agent controller over the entire supply chain environment.
Picks up all unhandled or pending incidents sequentially one by one:
  1. Decomposes tasks
  2. Investigates inventory & production schedules
  3. Negotiates with suppliers / gathers RFQs
  4. Evaluates recovery options using deterministic decision engine
  5. Auto-resolves incidents within authority limit ($50k)
  6. Escalates incidents exceeding threshold or with broken data to human coordinator

Eliminates disjointed individual page triggers in favor of a unified global agent loop.
"""

from typing import Any
from datetime import datetime, timezone
from pymongo.database import Database

from app.agent.agent_loop import run_agent_cycle
from app.agent.states import AgentState
from app.audit.audit_logger import log_event


def process_all_pending_incidents(db: Database, max_incidents: int = 15) -> dict[str, Any]:
    """
    Sequentially processes all open, unresolved incidents one by one.
    """
    start_time = datetime.now(timezone.utc)

    # Find pending incidents that are not yet resolved
    query = {"status": {"$in": ["DETECTED", "INVESTIGATING", "REPLANNING"]}}
    pending_docs = list(db["incidents"].find(query).limit(max_incidents))

    processed_results: list[dict[str, Any]] = []

    for doc in pending_docs:
        inc_id = doc["incident_id"]
        # Execute genuine multi-step reasoning loop
        result = run_agent_cycle(
            incident_id=inc_id,
            db=db,
            trigger_reason="Global autonomous agent queue processing",
        )
        processed_results.append({
            "incident_id": inc_id,
            "type": doc.get("type"),
            "component_id": doc.get("affected_component"),
            "state": result.get("state"),
            "decision": result.get("decision"),
            "requires_human_approval": result.get("requires_human_approval", False),
            "steps_executed": result.get("steps_executed", 0),
        })

    total_processed = len(processed_results)
    auto_resolved = sum(1 for r in processed_results if r["state"] == AgentState.RESOLVED.value)
    escalated = sum(1 for r in processed_results if r["requires_human_approval"] or r["state"] == AgentState.WAITING_APPROVAL.value)

    log_event(
        db,
        incident_id="GLOBAL-QUEUE",
        action=f"Global agent queue processed {total_processed} incidents ({auto_resolved} resolved autonomously, {escalated} escalated to coordinator).",
        decision="QUEUE_BATCH_COMPLETED",
        reason="Autonomous operations loop execution",
        step_index=0,
    )

    return {
        "status": "success",
        "processed_count": total_processed,
        "auto_resolved_count": auto_resolved,
        "escalated_count": escalated,
        "incidents": processed_results,
        "message": f"Global Agent processed {total_processed} incidents: {auto_resolved} resolved autonomously, {escalated} elevated for coordinator approval.",
    }
