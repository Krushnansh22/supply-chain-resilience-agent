"""
app/agent/task_decomposer.py
Owner: Developer 1 (Agent)

DYNAMIC TASK DECOMPOSITION (PS Section 4.2):
Before acting, the agent breaks a disruption into sub-tasks tailored to the specific
incident type, severity, and context — replacing the rigid one-size-fits-all pipeline.

Categories align directly with SKILL.md routing discipline:
- VERIFICATION
- EXTERNAL_COMMUNICATION
- SOURCING
- PLANNING
- APPROVAL
- RECORD_UPDATE
"""

from typing import Optional
from pymongo.database import Database
from datetime import datetime, timezone


class TaskStatus:
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"
    FAILED = "FAILED"


def decompose_incident(
    incident_id: str,
    incident_type: str,
    severity: str,
    component_id: Optional[str] = None,
    po_id: Optional[str] = None,
    supplier_id: Optional[str] = None,
    context: Optional[dict] = None,
) -> list[dict]:
    """
    Produces an incident-tailored task decomposition list.
    Different incident types and severities produce different task lists.
    """
    comp = component_id or "AFFECTED_COMPONENT"
    po = po_id or "AFFECTED_PO"
    supp = supplier_id or "AFFECTED_SUPPLIER"

    tasks = []

    # 1. Base initial assessment: always verify inventory & production impact
    tasks.append({
        "task_id": "TASK-01",
        "title": "Assess Inventory Buffer & Production Impact",
        "description": f"Check usable stock, daily consumption rate, days of supply, and affected production orders for component '{comp}'.",
        "category": "VERIFICATION",
        "assigned_tool": "get_inventory",
        "status": TaskStatus.PENDING,
        "result_summary": None,
    })

    tasks.append({
        "task_id": "TASK-02",
        "title": "Evaluate Production Schedule & Deadlines",
        "description": f"Identify high-priority production orders depending on '{comp}' and check SLA deadline proximity.",
        "category": "PLANNING",
        "assigned_tool": "get_production_schedule",
        "status": TaskStatus.PENDING,
        "result_summary": None,
    })

    # 2. Type-specific investigation & communication tasks
    if incident_type == "SUPPLIER_DELAY":
        tasks.append({
            "task_id": "TASK-03",
            "title": "Investigate Delayed Supplier & Carrier Tracking",
            "description": f"Query carrier tracking status for {po} and contact supplier {supp} to determine genuine delay duration and expedite options.",
            "category": "EXTERNAL_COMMUNICATION",
            "assigned_tool": "send_supplier_message",
            "status": TaskStatus.PENDING,
            "result_summary": None,
        })
        tasks.append({
            "task_id": "TASK-04",
            "title": "Solicit Multi-Supplier Alternative RFQs",
            "description": f"Request emergency quotes from certified alternative suppliers for '{comp}' across unit price, delivery speed, and MOQ.",
            "category": "SOURCING",
            "assigned_tool": "request_rfq",
            "status": TaskStatus.PENDING,
            "result_summary": None,
        })

    elif incident_type == "SUPPLIER_LIE":
        tasks.append({
            "task_id": "TASK-03",
            "title": "Verify Carrier Tracking & Detect Dispatch Contradiction",
            "description": f"Cross-examine carrier tracking for {po} against supplier {supp}'s dispatch claim to verify actual physical movement.",
            "category": "VERIFICATION",
            "assigned_tool": "get_tracking_status",
            "status": TaskStatus.PENDING,
            "result_summary": None,
        })
        tasks.append({
            "task_id": "TASK-04",
            "title": "Challenge Supplier Contradiction & Request Clarification",
            "description": f"Issue formal challenge to {supp} regarding unverified dispatch claim; downgrade reliability and request immediate factual pickup status.",
            "category": "EXTERNAL_COMMUNICATION",
            "assigned_tool": "request_clarification",
            "status": TaskStatus.PENDING,
            "result_summary": None,
        })
        tasks.append({
            "task_id": "TASK-05",
            "title": "Solicit Replacement RFQs from Verified Suppliers",
            "description": f"Request quotes from highly reliable alternative suppliers to replace compromised shipment of '{comp}'.",
            "category": "SOURCING",
            "assigned_tool": "request_rfq",
            "status": TaskStatus.PENDING,
            "result_summary": None,
        })

    elif incident_type == "QUALITY_FAILURE":
        tasks.append({
            "task_id": "TASK-03",
            "title": "Quarantine Defective Lot & Calculate Usable Stock Shortfall",
            "description": f"Confirm quarantine of defective batch for '{comp}' and compute net shortfall against upcoming production demand.",
            "category": "RECORD_UPDATE",
            "assigned_tool": "get_inventory",
            "status": TaskStatus.PENDING,
            "result_summary": None,
        })
        tasks.append({
            "task_id": "TASK-04",
            "title": "Filter Certified Suppliers & Solicit Quality-Compliant RFQs",
            "description": f"Strictly filter suppliers with required ISO/quality certifications and request expedited replacement quotes for '{comp}'.",
            "category": "SOURCING",
            "assigned_tool": "request_rfq",
            "status": TaskStatus.PENDING,
            "result_summary": None,
        })

    elif incident_type == "STALE_INVENTORY":
        tasks.append({
            "task_id": "TASK-03",
            "title": "Reconcile Physical vs System Inventory",
            "description": f"Audit actual usable stock vs safety threshold for '{comp}' and update system-of-record.",
            "category": "VERIFICATION",
            "assigned_tool": "get_inventory",
            "status": TaskStatus.PENDING,
            "result_summary": None,
        })
        tasks.append({
            "task_id": "TASK-04",
            "title": "Replenishment RFQ Evaluation",
            "description": f"Solicit replenishment quotes to restore safety stock buffer for '{comp}'.",
            "category": "SOURCING",
            "assigned_tool": "request_rfq",
            "status": TaskStatus.PENDING,
            "result_summary": None,
        })

    else:  # Generic or BUDGET_OVERRUN or unclassified
        tasks.append({
            "task_id": "TASK-03",
            "title": "Supplier & Purchase Order Investigation",
            "description": f"Gather active purchase orders and supplier performance metrics for '{comp}'.",
            "category": "VERIFICATION",
            "assigned_tool": "get_purchase_orders",
            "status": TaskStatus.PENDING,
            "result_summary": None,
        })
        tasks.append({
            "task_id": "TASK-04",
            "title": "Solicit Alternative Sourcing Quotes",
            "description": f"Request RFQs from candidate suppliers for '{comp}'.",
            "category": "SOURCING",
            "assigned_tool": "request_rfq",
            "status": TaskStatus.PENDING,
            "result_summary": None,
        })

    # 3. Deterministic recovery planning & trade-off evaluation
    task_num = len(tasks) + 1
    tasks.append({
        "task_id": f"TASK-{task_num:02d}",
        "title": "Compute Recovery Options (Single vs Split-Order Sourcing)",
        "description": "Call deterministic decision engine to generate ranked recovery options (incl. split-order plans) against budget, SLA, and quality constraints.",
        "category": "PLANNING",
        "assigned_tool": "compute_recovery_options",
        "status": TaskStatus.PENDING,
        "result_summary": None,
    })

    # 4. Multi-criteria escalation or autonomous ERP execution
    task_num += 1
    tasks.append({
        "task_id": f"TASK-{task_num:02d}",
        "title": "Multi-Criteria Escalation Check & Decision Execution",
        "description": "Evaluate cost, SLA deadlines, quality risks, and trade-offs. If within authority, execute ERP update; if escalation required, generate Decision Brief.",
        "category": "APPROVAL",
        "assigned_tool": "check_approval_threshold",
        "status": TaskStatus.PENDING,
        "result_summary": None,
    })

    # 5. Audit trail & post-action verification
    task_num += 1
    tasks.append({
        "task_id": f"TASK-{task_num:02d}",
        "title": "Record Rich Audit Trail & Continuous Remonitoring",
        "description": "Persist explainable decision trail citing all tools, calculations, alternatives considered/rejected, and remaining risks.",
        "category": "RECORD_UPDATE",
        "assigned_tool": "record_audit",
        "status": TaskStatus.PENDING,
        "result_summary": None,
    })

    return tasks


def persist_tasks(incident_id: str, tasks: list[dict], db: Database) -> None:
    """Saves or updates the dynamic task list in MongoDB."""
    now = datetime.now(timezone.utc)
    db["agent_tasks"].update_one(
        {"incident_id": incident_id},
        {"$set": {"incident_id": incident_id, "tasks": tasks, "updated_at": now}},
        upsert=True,
    )
    # Also update incident document for convenience
    db["incidents"].update_one(
        {"incident_id": incident_id},
        {"$set": {"task_decomposition": tasks, "tasks_count": len(tasks)}},
    )


def update_task_status(
    incident_id: str,
    task_id: str,
    status: str,
    result_summary: Optional[str],
    db: Database,
) -> None:
    """Updates a single task's status and result summary in MongoDB."""
    doc = db["agent_tasks"].find_one({"incident_id": incident_id})
    if not doc or "tasks" not in doc:
        return

    tasks = doc["tasks"]
    for t in tasks:
        if t["task_id"] == task_id:
            t["status"] = status
            if result_summary:
                t["result_summary"] = result_summary
            break

    persist_tasks(incident_id, tasks, db)


def get_tasks_for_incident(incident_id: str, db: Database) -> list[dict]:
    """Retrieves current tasks for an incident."""
    doc = db["agent_tasks"].find_one({"incident_id": incident_id}, {"_id": 0})
    if doc and "tasks" in doc:
        return doc["tasks"]
    inc = db["incidents"].find_one({"incident_id": incident_id}, {"_id": 0})
    if inc and "task_decomposition" in inc:
        return inc["task_decomposition"]
    return []
