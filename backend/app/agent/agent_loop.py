"""
app/agent/agent_loop.py
Owner: Developer 1 (Agent)

IMPORTANT: LLM reasoning has moved entirely to the n8n workflow (Groq AI Agent node).
The backend agent endpoints are now lightweight state-machine controllers:
  - /agent/trigger   -> set state INVESTIGATING, log, return incident context for n8n
  - /agent/approve   -> set state EXECUTING, log
  - /agent/reject    -> set state REPLANNING, log

n8n calls these endpoints and orchestrates the full reasoning loop via the
Groq AI Agent node. The backend stores state in MongoDB and serves data to n8n
through the /integrations/* routes.

RECEIVES:
  - incident_id (str) from api/routes_agent.py (POST /agent/trigger)
  - DB session
DELIVERS:
  - updates Incident.status to mirror AgentState at every transition
  - writes to audit_logs via audit/audit_logger.log_event() on every state change
  - returns a summary dict + incident context to the API layer (n8n consumes this)
"""

from pymongo.database import Database
from app.agent.states import AgentState
from app.audit.audit_logger import log_event
from datetime import datetime


def get_agent_state(incident_id: str, db: Database) -> str:
    incident = db["incidents"].find_one({"incident_id": incident_id}, {"status": 1})
    return incident.get("status", "UNKNOWN") if incident else "UNKNOWN"


def _set_state(incident_id: str, state: AgentState, db: Database):
    db["incidents"].update_one(
        {"incident_id": incident_id},
        {"$set": {"status": state.value}}
    )


def run_agent_for_incident(incident_id: str, db: Database) -> dict:
    """
    Triggered by POST /agent/trigger (called by n8n after detecting an incident).

    1. Load the incident from MongoDB.
    2. Transition to INVESTIGATING state.
    3. Fetch context (inventory, production orders, suppliers) for n8n to pass to Groq.
    4. Return incident context — n8n's Groq AI Agent node uses this to reason.

    The full reasoning loop is in n8n. Once n8n's agent decides on a recovery plan,
    it calls /agent/approve or /agent/reject accordingly.
    """
    incident = db["incidents"].find_one({"incident_id": incident_id}, {"_id": 0})
    if not incident:
        return {"error": "incident not found", "incident_id": incident_id}

    # Transition: DETECTED -> INVESTIGATING
    _set_state(incident_id, AgentState.INVESTIGATING, db)
    db["agent_sessions"].update_one(
        {"incident_id": incident_id},
        {"$set": {
            "incident_id": incident_id,
            "state": AgentState.INVESTIGATING.value,
            "updated_at": datetime.utcnow(),
            "last_context": {"affected_component": incident.get("affected_component")},
        }, "$inc": {"revision": 1}},
        upsert=True,
    )
    log_event(
        db, incident_id,
        action="Agent triggered by n8n workflow. Transitioning to INVESTIGATING.",
        decision="INVESTIGATING",
        reason="n8n event detected supply chain disruption"
    )

    # Gather context for n8n's Groq AI Agent
    component_id = incident.get("affected_component")
    inventory = None
    production_orders = []
    suppliers = []

    if component_id:
        inventory = db["inventory"].find_one({"component_id": component_id}, {"_id": 0})
        production_orders = list(
            db["production_orders"].find({"component_id": component_id}, {"_id": 0}).limit(5)
        )
        # Get suppliers that handle this component via purchase orders
        po_docs = list(db["purchase_orders"].find({"component_id": component_id}, {"_id": 0}).limit(5))
        supplier_ids = list({po["supplier_id"] for po in po_docs if po.get("supplier_id")})
        suppliers = list(db["suppliers"].find({"supplier_id": {"$in": supplier_ids}}, {"_id": 0}))

    return {
        "incident_id": incident_id,
        "state": AgentState.INVESTIGATING.value,
        "incident": incident,
        "context": {
            "component_id": component_id,
            "inventory": inventory,
            "production_orders": production_orders,
            "suppliers": suppliers,
        },
        "message": "Agent is INVESTIGATING. n8n Groq AI Agent will now reason on this context."
    }
