"""
app/api/routes_agent.py
Owner: Developer 1 (Agent) / Developer 2 (Backend)

Bridge between the frontend / n8n orchestrator and the autonomous agent runtime.

ENDPOINTS:
  - POST /agent/run-incident       -> runs full multi-step agent reasoning loop
  - POST /agent/trigger            -> triggers agent execution for an incident
  - GET  /agent/tasks/{id}         -> dynamic task decomposition list
  - GET  /agent/audit/{id}         -> rich explainable audit trail
  - POST /agent/replan/{id}        -> triggers mid-flight replan
  - GET  /agent/state/{id}         -> current agent lifecycle state
  - GET  /agent/plan/{id}          -> current recovery plan
  - POST /agent/approve            -> human coordinator approves recovery plan (transitions to EXECUTING)
  - POST /agent/reject             -> human coordinator rejects recovery plan (transitions to REPLANNING)
"""

from fastapi import APIRouter, Depends, Path, Request
from pydantic import BaseModel, ConfigDict, field_validator, Field
from datetime import datetime, timezone
from typing import Optional, Any, Dict, List
from pymongo.database import Database

from app.mongo_database import get_mongo_db
from app.agent.agent_loop import run_agent_cycle, run_agent_for_incident, get_agent_state
from app.agent.task_decomposer import get_tasks_for_incident
from app.agent.states import AgentState
from app.agent.tool_executor import execute_tool
from app.audit.audit_logger import get_incident_audit_trail, log_event
from app.middleware.security import require_api_key
from app.middleware.rate_limiter import check_rate_limit

from app.agent.environment_scanner import scan_operational_environment
from app.agent.queue_processor import process_all_pending_incidents
from app.decision_engine.recovery_planner import build_recovery_plan

router = APIRouter()

_ID_PATTERN = r"^[A-Za-z0-9_-]+$"


class TriggerRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    incident_id: str = Field(..., min_length=1, max_length=32, pattern=_ID_PATTERN)

    @field_validator("incident_id")
    @classmethod
    def sanitize_id(cls, v: str) -> str:
        return v.strip().replace("\x00", "")


class ReplanRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    incident_id: str = Field(..., min_length=1, max_length=32, pattern=_ID_PATTERN)
    invalidation_reason: str = Field(..., min_length=1, max_length=500)
    affected_supplier: Optional[str] = Field(None, max_length=64)


class ApprovalDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")
    incident_id: str = Field(..., min_length=1, max_length=32, pattern=_ID_PATTERN)
    approver: str = Field(default="human-coordinator", min_length=1, max_length=64)
    revised_value: Optional[float] = Field(default=None, description="Revised physical stock count or quantity to fix broken/negative data")
    revision_reason: Optional[str] = Field(default=None, max_length=256, description="Reason for the data correction")

    @field_validator("incident_id", "approver")
    @classmethod
    def sanitize_fields(cls, v: str) -> str:
        return v.strip().replace("\x00", "")


@router.post("/scan-and-triage")
def scan_environment_endpoint(
    request: Request,
    db: Database = Depends(get_mongo_db),
    _auth: None = Depends(require_api_key),
):
    """
    POST /agent/scan-and-triage
    Scans the entire operational database environment (inventory, POs, suppliers),
    discovers anomalies/broken data, and autonomously triggers the multi-step agent reasoning loop.
    """
    check_rate_limit(request, bucket="agent_scan", max_calls=15, window_seconds=60)
    result = scan_operational_environment(db)
    return result


@router.post("/process-backlog")
def process_backlog_endpoint(
    request: Request,
    db: Database = Depends(get_mongo_db),
    _auth: None = Depends(require_api_key),
):
    """
    POST /agent/process-backlog
    Global Autonomous Agent Controller:
    Takes all active/pending incidents one by one, reasons over each, resolves autonomous ones,
    and escalates high-risk/high-cost ones to coordinators.
    """
    check_rate_limit(request, bucket="agent_backlog", max_calls=20, window_seconds=60)
    result = process_all_pending_incidents(db)
    return result


@router.get("/system-status")
def get_system_status(db: Database = Depends(get_mongo_db)):
    """
    GET /agent/system-status
    Returns current agent operational status and aggregate environment metrics.
    """
    total_incidents = db["incidents"].count_documents({})
    waiting_approval = db["incidents"].count_documents({"status": "WAITING_APPROVAL"})
    investigating = db["incidents"].count_documents({"status": {"$in": ["INVESTIGATING", "EXECUTING", "REPLANNING"]}})
    resolved = db["incidents"].count_documents({"status": "RESOLVED"})
    data_inconsistencies = db["incidents"].count_documents({"data_inconsistency_detected": True, "status": {"$ne": "RESOLVED"}})

    inventory_count = db["inventory"].count_documents({})
    po_count = db["purchase_orders"].count_documents({})
    supplier_count = db["suppliers"].count_documents({})

    return {
        "agent_status": "ACTIVE" if investigating > 0 else "IDLE",
        "metrics": {
            "total_incidents": total_incidents,
            "waiting_approval": waiting_approval,
            "investigating": investigating,
            "resolved": resolved,
            "data_inconsistencies": data_inconsistencies,
            "inventory_monitored": inventory_count,
            "purchase_orders_monitored": po_count,
            "suppliers_connected": supplier_count,
        },
    }


@router.post("/run-incident")
def run_incident_endpoint(
    req: TriggerRequest,
    request: Request,
    db: Database = Depends(get_mongo_db),
    _auth: None = Depends(require_api_key),
):
    """
    POST /agent/run-incident
    Executes the full multi-step agentic controller loop.
    Returns the complete resolution, task decomposition, audit trail, and decision brief.
    """
    check_rate_limit(request, bucket="agent_run", max_calls=20, window_seconds=60)
    result = run_agent_cycle(req.incident_id, db)
    return result


@router.post("/trigger")
def trigger_agent(
    req: TriggerRequest,
    request: Request,
    db: Database = Depends(get_mongo_db),
    _auth: None = Depends(require_api_key),
):
    """
    POST /agent/trigger
    Kicks off or resumes the agent loop for an incident.
    """
    check_rate_limit(request, bucket="agent_trigger", max_calls=20, window_seconds=60)
    result = run_agent_for_incident(req.incident_id, db)
    return result


@router.get("/tasks/{incident_id}")
def get_incident_tasks(
    incident_id: str = Path(..., pattern=_ID_PATTERN, min_length=1, max_length=32),
    db: Database = Depends(get_mongo_db),
):
    """
    GET /agent/tasks/{incident_id}
    Retrieves the dynamic task decomposition list for an incident.
    """
    tasks = get_tasks_for_incident(incident_id, db)
    return {"incident_id": incident_id, "tasks": tasks, "count": len(tasks)}


@router.get("/audit/{incident_id}")
def get_incident_audit(
    incident_id: str = Path(..., pattern=_ID_PATTERN, min_length=1, max_length=32),
    db: Database = Depends(get_mongo_db),
):
    """
    GET /agent/audit/{incident_id}
    Returns the chronological, rich audit trail with explainable decision steps.
    """
    audit_trail = get_incident_audit_trail(incident_id, db)
    return {"incident_id": incident_id, "audit_trail": audit_trail, "count": len(audit_trail)}


@router.post("/replan/{incident_id}")
def replan_incident_endpoint(
    req: ReplanRequest,
    request: Request,
    incident_id: str = Path(..., pattern=_ID_PATTERN, min_length=1, max_length=32),
    db: Database = Depends(get_mongo_db),
    _auth: None = Depends(require_api_key),
):
    """
    POST /agent/replan/{incident_id}
    Triggers mid-flight replanning when new facts/disruptions invalidate an active plan.
    """
    check_rate_limit(request, bucket="agent_replan", max_calls=10, window_seconds=60)
    replan_context = {
        "reason": req.invalidation_reason,
        "suppliers_to_avoid": [req.affected_supplier] if req.affected_supplier else [],
    }
    result = run_agent_cycle(
        incident_id=req.incident_id,
        db=db,
        trigger_reason=f"Replanning triggered: {req.invalidation_reason}",
        replan_context=replan_context,
    )
    return result


@router.get("/state/{incident_id}")
def agent_state(
    incident_id: str = Path(..., pattern=_ID_PATTERN, min_length=1, max_length=32),
    db: Database = Depends(get_mongo_db),
):
    """
    GET /agent/state/{incident_id}
    Returns the current state machine position of an incident.
    """
    return {"incident_id": incident_id, "state": get_agent_state(incident_id, db)}


@router.get("/plan/{incident_id}")
def agent_plan(
    incident_id: str = Path(..., pattern=_ID_PATTERN, min_length=1, max_length=32),
    db: Database = Depends(get_mongo_db),
):
    """
    GET /agent/plan/{incident_id}
    Returns the current recovery plan and options.
    If no plan document exists yet but incident exists, builds candidate recovery options dynamically.
    """
    plan = db["recovery_plans"].find_one({"incident_id": incident_id}, {"_id": 0})
    if not plan:
        incident = db["incidents"].find_one({"incident_id": incident_id}, {"_id": 0})
        comp_id = incident.get("affected_component") if incident else None

        if comp_id:
            try:
                # Dynamically construct candidate recovery plan from database suppliers
                plan = build_recovery_plan(
                    component_id=comp_id,
                    quantity_needed=500,
                    max_delivery_days=7,
                    db=db,
                    incident_id=incident_id,
                )
                db["recovery_plans"].replace_one({"incident_id": incident_id}, plan, upsert=True)
            except Exception:
                plan = None

        if not plan:
            return {
                "incident_id": incident_id,
                "options": [],
                "recommended_option_id": "",
                "recommendation_reason": incident.get("decision_brief", "No recovery plan available.") if incident else "No recovery plan has been generated.",
                "requires_human_approval": False,
                "approval_threshold_usd": 50000,
            }

    # Ensure decision brief / escalation context is attached
    if "decision_brief" not in plan and incident_id:
        inc = db["incidents"].find_one({"incident_id": incident_id}, {"_id": 0})
        if inc and inc.get("decision_brief"):
            plan["decision_brief"] = inc["decision_brief"]

    return plan


@router.post("/approve")
def approve_plan(
    decision: ApprovalDecision,
    request: Request,
    db: Database = Depends(get_mongo_db),
    _auth: None = Depends(require_api_key),
):
    """
    POST /agent/approve
    On approval, transition state WAITING_APPROVAL -> EXECUTING, log, and execute recovery plan.
    """
    check_rate_limit(request, bucket="agent_approve", max_calls=10, window_seconds=60)
    incident = db["incidents"].find_one({"incident_id": decision.incident_id}, {"_id": 0})
    if not incident:
        return {"error": "incident not found"}

    # Handle revised broken data (e.g. negative inventory / physical recount)
    corrected_inventory = None
    if decision.revised_value is not None:
        comp_id = incident.get("affected_component")
        if comp_id and decision.revised_value >= 0:
            val = int(decision.revised_value)
            db["inventory"].update_one(
                {"component_id": comp_id},
                {"$set": {"usable_stock": val, "current_stock": max(val, 0)}},
            )
            reason_text = decision.revision_reason or f"Physical stock recount by {decision.approver}"
            log_event(
                db,
                incident_id=decision.incident_id,
                action=f"Data correction applied: Component '{comp_id}' stock updated to {val}.",
                decision="CORRECTED",
                reason=reason_text,
                step_index=99,
            )
            db["incidents"].update_one(
                {"incident_id": decision.incident_id},
                {"$set": {"data_inconsistency_detected": False, "revised_value": val}},
            )
            corrected_inventory = {"component_id": comp_id, "usable_stock": val}

    db["incidents"].update_one(
        {"incident_id": decision.incident_id},
        {"$set": {"status": AgentState.EXECUTING.value, "approved_by": decision.approver}},
    )
    db["agent_sessions"].update_one(
        {"incident_id": decision.incident_id},
        {"$set": {"state": AgentState.EXECUTING.value, "updated_at": datetime.now(timezone.utc)}, "$inc": {"revision": 1}},
        upsert=True,
    )
    log_event(
        db,
        incident_id=decision.incident_id,
        action="Recovery plan approved by coordinator.",
        decision="APPROVED",
        reason=f"Approved by {decision.approver}",
    )

    plan = db["recovery_plans"].find_one({"incident_id": decision.incident_id}, {"_id": 0})
    erp_data = None
    if plan and plan.get("options"):
        option_id = plan.get("recommended_option_id", "A")
        erp_res = execute_tool("update_erp", {"incident_id": decision.incident_id, "option_id": option_id}, db)
        if erp_res.success:
            erp_data = erp_res.data

    return {
        "incident_id": decision.incident_id,
        "state": AgentState.EXECUTING.value,
        "erp_execution": erp_data,
        "corrected_inventory": corrected_inventory,
    }


@router.post("/reject")
def reject_plan(
    decision: ApprovalDecision,
    request: Request,
    db: Database = Depends(get_mongo_db),
    _auth: None = Depends(require_api_key),
):
    """
    POST /agent/reject
    On rejection, trigger REPLANNING state with 'human rejected' as context.
    """
    check_rate_limit(request, bucket="agent_reject", max_calls=10, window_seconds=60)
    incident = db["incidents"].find_one({"incident_id": decision.incident_id}, {"_id": 0})
    if not incident:
        return {"error": "incident not found"}

    db["incidents"].update_one(
        {"incident_id": decision.incident_id},
        {"$set": {"status": AgentState.REPLANNING.value}},
    )
    db["agent_sessions"].update_one(
        {"incident_id": decision.incident_id},
        {"$set": {"state": AgentState.REPLANNING.value, "updated_at": datetime.now(timezone.utc)}, "$inc": {"revision": 1}},
        upsert=True,
    )
    log_event(
        db,
        incident_id=decision.incident_id,
        action="Recovery plan rejected; replanning required.",
        decision="REJECTED",
        reason=f"Rejected by {decision.approver}",
    )
    return {
        "incident_id": decision.incident_id,
        "state": AgentState.REPLANNING.value,
    }


# ─── AGENT LIFECYCLE & SEQUENTIAL CONTROLLER ENDPOINTS (WITH RBAC) ───

from app.agent.agent_service import agent_service
from app.middleware.rbac import get_current_user_and_scope


class StockCorrectionRequest(BaseModel):
    incident_id: str
    component_id: str
    corrected_stock: int
    reason: str
    approver: str = "Operator"


@router.get("/status")
def get_agent_status_endpoint(
    db: Database = Depends(get_mongo_db),
    context: Dict[str, Any] = Depends(get_current_user_and_scope),
):
    """GET /agent/status -> returns state, message, step, queue, and metrics."""
    return agent_service.get_status(db)


@router.post("/start")
def start_agent_endpoint(
    db: Database = Depends(get_mongo_db),
    context: Dict[str, Any] = Depends(get_current_user_and_scope),
):
    """POST /agent/start -> starts the autonomous loop and triggers an initial environment scan."""
    return agent_service.start_agent(db)


@router.post("/stop")
def stop_agent_endpoint(
    context: Dict[str, Any] = Depends(get_current_user_and_scope),
):
    """POST /agent/stop -> stops the autonomous agent worker."""
    return agent_service.stop_agent()


@router.post("/scan")
def scan_environment_endpoint(
    db: Database = Depends(get_mongo_db),
    context: Dict[str, Any] = Depends(get_current_user_and_scope),
):
    """POST /agent/scan -> triggers an immediate scan of the database environment."""
    anomalies = agent_service.scan_environment(db)
    return {
        "scanned": True,
        "anomalies_found": len(anomalies),
        "queue_length": len(agent_service.queue),
        "anomalies": anomalies,
    }


@router.post("/step")
def step_agent_endpoint(
    db: Database = Depends(get_mongo_db),
    context: Dict[str, Any] = Depends(get_current_user_and_scope),
):
    """POST /agent/step -> executes one step of the current incident."""
    return agent_service.process_one_step(db)


@router.post("/correct-stock")
def correct_stock_endpoint(
    req: StockCorrectionRequest,
    db: Database = Depends(get_mongo_db),
    context: Dict[str, Any] = Depends(get_current_user_and_scope),
):
    """
    POST /agent/correct-stock
    Allows human operator/manager to input verified physical stock count for negative/missing stock incidents.
    Guarded by RBAC: Warehouse Manager can only correct stock in their assigned warehouse.
    """
    # Verify warehouse ownership
    inv = db["inventory"].find_one({"component_id": req.component_id})
    if inv:
        comp_loc = inv.get("location")
        eff_warehouse = context.get("effective_warehouse")
        if context.get("role") == "WAREHOUSE_MANAGER" and eff_warehouse and comp_loc != eff_warehouse:
            raise HTTPException(
                status_code=403,
                detail=f"Forbidden: You are manager of '{eff_warehouse}' and cannot correct stock for component located at '{comp_loc}'."
            )

    approver_name = context.get("user", {}).get("name") or req.approver
    res = agent_service.resolve_stock_correction(
        incident_id=req.incident_id,
        component_id=req.component_id,
        corrected_stock=req.corrected_stock,
        reason=req.reason,
        approver=approver_name,
        db=db,
    )
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    return res

