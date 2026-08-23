"""
app/audit/audit_logger.py
Owner: Developer 2 (Backend / Simulation) / Developer 1 (Agent)

REQUIRED by PS Core Capability #4: "Output human-readable reasoning logs" +
"Comprehensive Audit Trail & Explainability Output".

Maintains a rich, verifiable, explainable audit trail for every incident step.
"""

from datetime import datetime, timezone
from typing import Optional, Any
from pymongo.database import Database


def log_event(
    db: Database,
    incident_id: Optional[str],
    action: str,
    tool: Optional[str] = None,
    result: Optional[str] = None,
    decision: Optional[str] = None,
    reason: Optional[str] = None,
    thought: Optional[str] = None,
    tool_args: Optional[dict] = None,
    step_index: Optional[int] = None,
    data_sources_checked: Optional[list[str]] = None,
    supplier_communications: Optional[list[dict]] = None,
    alternatives_considered: Optional[list[dict]] = None,
    alternatives_rejected: Optional[list[dict]] = None,
    calculations_performed: Optional[list[dict]] = None,
    erp_updates_made: Optional[list[str]] = None,
    escalation_details: Optional[dict] = None,
    remaining_risk: Optional[str] = None,
) -> dict:
    """
    Persists an audit log entry to MongoDB 'audit_logs' collection.
    Supports both basic event logging and rich, deep agent step logging.
    """
    now = datetime.now(timezone.utc)
    entry: dict[str, Any] = {
        "timestamp": now,
        "incident_id": incident_id,
        "action": action,
        "tool": tool,
        "result": result,
        "decision": decision,
        "reason": reason,
    }
    if thought:
        entry["thought"] = thought
    if tool_args:
        entry["tool_args"] = tool_args

    if step_index is not None:
        entry["step_index"] = step_index
    if data_sources_checked:
        entry["data_sources_checked"] = data_sources_checked
    if supplier_communications:
        entry["supplier_communications"] = supplier_communications
    if alternatives_considered:
        entry["alternatives_considered"] = alternatives_considered
    if alternatives_rejected:
        entry["alternatives_rejected"] = alternatives_rejected
    if calculations_performed:
        entry["calculations_performed"] = calculations_performed
    if erp_updates_made:
        entry["erp_updates_made"] = erp_updates_made
    if escalation_details:
        entry["escalation_details"] = escalation_details
    if remaining_risk:
        entry["remaining_risk"] = remaining_risk

    db["audit_logs"].insert_one(entry)
    # Remove Mongo internal ObjectId for returned dict
    entry.pop("_id", None)
    return entry


def get_incident_audit_trail(incident_id: str, db: Database) -> list[dict]:
    """Retrieves full chronological audit trail for an incident."""
    logs = list(db["audit_logs"].find({"incident_id": incident_id}, {"_id": 0}).sort("timestamp", 1))
    return logs
