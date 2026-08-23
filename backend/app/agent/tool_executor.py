"""
app/agent/tool_executor.py
Owner: Developer 1 (Agent)

Executes agent tool calls by name against underlying domain functions,
injecting database session, validating parameters, and returning structured ToolResult objects.
"""

from typing import Any
from pymongo.database import Database
from datetime import datetime, timezone

from app.tools import (
    inventory_tools,
    production_tools,
    supplier_tools,
    rfq_tools,
    approval_tools,
    erp_tools,
    purchase_tools,
)
from app.decision_engine.recovery_planner import build_recovery_plan
from app.decision_engine.replanning import get_replanning_context
from app.agent.escalation_engine import evaluate_escalation
from app.agent.states import AgentState
from app.schemas.tool_io import ToolResult
from app.schemas.recovery_plan import RecoveryPlanOption, SupplierAllocation
from app.audit.audit_logger import log_event


def execute_tool(tool_name: str, tool_input: dict[str, Any], db: Database) -> ToolResult:
    """
    Executes a tool call by name with input parameters and DB session.
    Guards against missing keys or runtime exceptions with graceful ToolResult errors.
    """
    try:
        # 1. Inventory Tools
        if tool_name == "get_inventory":
            comp_id = tool_input.get("component_id")
            if not comp_id:
                return ToolResult(tool_name=tool_name, success=False, error="Missing required 'component_id'", summary="Missing component_id.")
            return inventory_tools.get_inventory(comp_id, db)

        # 2. Purchase Order Tools
        if tool_name in ("get_purchase_orders", "get_purchase_order"):
            return purchase_tools.get_purchase_orders(
                component_id=tool_input.get("component_id"),
                po_id=tool_input.get("po_id"),
                db=db,
            )

        # 3. Production Schedule Tools
        if tool_name in ("get_production_schedule", "get_production_orders"):
            comp_id = tool_input.get("component_id")
            if not comp_id:
                return ToolResult(tool_name=tool_name, success=False, error="Missing required 'component_id'", summary="Missing component_id.")
            return production_tools.get_production_orders(comp_id, db)

        # 4. Supplier Tools
        if tool_name == "get_supplier":
            supp_id = tool_input.get("supplier_id")
            if not supp_id:
                return ToolResult(tool_name=tool_name, success=False, error="Missing required 'supplier_id'", summary="Missing supplier_id.")
            return supplier_tools.get_supplier(supp_id, db)

        if tool_name == "get_suppliers":
            return supplier_tools.get_suppliers(tool_input.get("component_id"), db)

        if tool_name == "send_supplier_message":
            return supplier_tools.send_supplier_message(
                supplier_id=tool_input["supplier_id"],
                po_id=tool_input["po_id"],
                message=tool_input["message"],
                db=db,
            )

        if tool_name == "request_clarification":
            return supplier_tools.request_clarification(
                supplier_id=tool_input["supplier_id"],
                po_id=tool_input["po_id"],
                question=tool_input["question"],
                previous_claim=tool_input.get("previous_claim"),
                db=db,
            )

        if tool_name == "get_tracking_status":
            return supplier_tools.get_tracking_status(tool_input["po_id"], db)

        # 5. RFQ Tools
        if tool_name in ("request_rfq", "request_supplier_quote"):
            return rfq_tools.request_rfq(
                component_id=tool_input["component_id"],
                quantity=int(tool_input["quantity"]),
                supplier_ids=list(tool_input["supplier_ids"]),
                db=db,
            )

        # 6. Deterministic Decision Engine Recovery Planning
        if tool_name in ("compute_recovery_options", "build_recovery_plan"):
            component_id = tool_input.get("component_id")
            req_qty = int(tool_input.get("required_quantity", 500))
            req_days = int(tool_input.get("required_by_days", 7))
            req_cert = tool_input.get("required_cert")
            max_budget = float(tool_input.get("max_budget", 100000.0))
            incident_id = tool_input.get("incident_id", "INC-PLAN")

            # Look up recent RFQs from DB for this component
            rfq_candidates = list(db["rfqs"].find({"component_id": component_id}, {"_id": 0}).sort("created_at", -1).limit(6))
            if not rfq_candidates:
                # If no RFQs exist, discover candidate suppliers and solicit synthetic quotes
                cand_suppliers = db["suppliers"].distinct("supplier_id") or ["SUP-001", "SUP-002", "SUP-003"]
                rfq_res = rfq_tools.request_rfq(component_id or "COMP-001", req_qty, cand_suppliers[:3], db)
                rfq_candidates = rfq_res.data

            plan = build_recovery_plan(
                incident_id=incident_id,
                required_quantity=req_qty,
                rfq_candidates=rfq_candidates,
                required_cert=req_cert,
                required_by_days=req_days,
                max_budget=max_budget,
            )

            # Persist plan to DB
            plan_dict = plan.model_dump()
            db["recovery_plans"].update_one(
                {"incident_id": incident_id},
                {"$set": plan_dict},
                upsert=True,
            )

            options_summary = []
            for o in plan.options:
                alloc_text = ", ".join([f"{a.quantity}x from {a.supplier_id} (${a.unit_price}/u, {a.delivery_days}d)" for a in o.allocations])
                status = "PASS" if o.constraints_satisfied else f"FAIL ({o.rejection_reason})"
                options_summary.append(f"Option {o.option_id} (${o.total_cost:,.2f}, {o.max_delivery_days}d): {alloc_text} [{status}]")

            return ToolResult(
                tool_name=tool_name,
                success=True,
                data=plan_dict,
                summary=(
                    f"Computed {len(plan.options)} recovery options. "
                    f"Recommended: Option {plan.recommended_option_id} ({plan.recommendation_reason}). "
                    f"Summary:\n" + "\n".join(options_summary)
                ),
            )

        # 7. Plan Proposal
        if tool_name == "propose_plan":
            incident_id = tool_input["incident_id"]
            option_id = tool_input["option_id"]
            justification = tool_input["justification"]

            db["recovery_plans"].update_one(
                {"incident_id": incident_id},
                {"$set": {
                    "recommended_option_id": option_id,
                    "recommendation_reason": justification,
                    "updated_at": datetime.now(timezone.utc),
                }},
            )
            db["incidents"].update_one(
                {"incident_id": incident_id},
                {"$set": {"status": AgentState.PLAN_READY.value}},
            )

            return ToolResult(
                tool_name=tool_name,
                success=True,
                data={"incident_id": incident_id, "option_id": option_id, "justification": justification},
                summary=f"Proposed recovery Option {option_id} for incident {incident_id}. Justification: {justification}",
            )

        # 8. Approval & Escalation Checks
        if tool_name in ("check_approval", "check_approval_threshold"):
            cost = float(tool_input["cost"])
            incident_id = tool_input.get("incident_id")
            base_res = approval_tools.check_approval(cost)

            eval_res = None
            if incident_id:
                inc = db["incidents"].find_one({"incident_id": incident_id}, {"_id": 0})
                plan_doc = db["recovery_plans"].find_one({"incident_id": incident_id}, {"_id": 0})
                if inc and plan_doc:
                    from app.schemas.recovery_plan import RecoveryPlan
                    try:
                        plan_obj = RecoveryPlan(**plan_doc)
                        eval_res = evaluate_escalation(
                            incident_id=incident_id,
                            incident_type=inc.get("type", "SUPPLIER_DELAY"),
                            severity=inc.get("severity", "MEDIUM"),
                            component_id=inc.get("affected_component"),
                            plan=plan_obj,
                        )
                    except Exception:
                        pass

            data = base_res.data
            if eval_res:
                data["escalation_evaluation"] = eval_res.model_dump()

            return ToolResult(
                tool_name=tool_name,
                success=True,
                data=data,
                summary=base_res.summary,
            )

        if tool_name == "escalate_to_human":
            incident_id = tool_input["incident_id"]
            reason = tool_input["reason"]
            criterion = tool_input.get("trigger_criterion", "COST_EXCEEDS_THRESHOLD")
            decision_brief = tool_input.get("decision_brief", "")

            db["incidents"].update_one(
                {"incident_id": incident_id},
                {"$set": {
                    "status": AgentState.WAITING_APPROVAL.value,
                    "escalation_reason": reason,
                    "escalation_criterion": criterion,
                    "decision_brief": decision_brief,
                }},
            )
            log_event(
                db,
                incident_id=incident_id,
                action=f"Incident escalated to human coordinator: {reason}",
                tool="escalate_to_human",
                decision="WAITING_APPROVAL",
                reason=reason,
                escalation_details={"criterion": criterion, "decision_brief": decision_brief},
            )

            return ToolResult(
                tool_name=tool_name,
                success=True,
                data={"incident_id": incident_id, "status": AgentState.WAITING_APPROVAL.value, "criterion": criterion},
                summary=f"Escalated incident {incident_id} ({criterion}): {reason}",
            )

        # 9. ERP Execution
        if tool_name == "update_erp":
            incident_id = tool_input["incident_id"]
            option_id = tool_input.get("option_id", "A")

            plan_doc = db["recovery_plans"].find_one({"incident_id": incident_id}, {"_id": 0})
            if not plan_doc or not plan_doc.get("options"):
                return ToolResult(
                    tool_name=tool_name,
                    success=False,
                    error=f"No recovery plan found for incident {incident_id}",
                    summary=f"ERP update failed: no recovery plan exists for {incident_id}.",
                )

            chosen_opt_dict = next((o for o in plan_doc["options"] if o["option_id"] == option_id), plan_doc["options"][0])
            allocations = [
                SupplierAllocation(
                    supplier_id=a["supplier_id"],
                    quantity=a["quantity"],
                    unit_price=a["unit_price"],
                    delivery_days=a["delivery_days"],
                )
                for a in chosen_opt_dict.get("allocations", [])
            ]
            opt_obj = RecoveryPlanOption(
                option_id=chosen_opt_dict["option_id"],
                allocations=allocations,
                total_cost=chosen_opt_dict["total_cost"],
                max_delivery_days=chosen_opt_dict["max_delivery_days"],
                constraints_satisfied=chosen_opt_dict.get("constraints_satisfied", True),
                rejection_reason=chosen_opt_dict.get("rejection_reason"),
            )

            erp_res = erp_tools.update_erp(incident_id, opt_obj, db)
            if erp_res.success:
                log_event(
                    db,
                    incident_id=incident_id,
                    action="Executed approved recovery plan in ERP.",
                    tool="update_erp",
                    decision="RESOLVED",
                    reason=f"Option {option_id} executed. Created POs: {erp_res.data.get('purchase_orders_created')}",
                    erp_updates_made=erp_res.data.get("purchase_orders_created", []),
                )
            return erp_res

        # 10. Replanning Trigger
        if tool_name == "replan_incident":
            incident_id = tool_input["incident_id"]
            invalidation_reason = tool_input["invalidation_reason"]
            affected_supp = tool_input.get("affected_supplier")

            db["incidents"].update_one(
                {"incident_id": incident_id},
                {"$set": {"status": AgentState.REPLANNING.value, "replan_reason": invalidation_reason}},
            )
            log_event(
                db,
                incident_id=incident_id,
                action="Active recovery plan invalidated. Transitioning to REPLANNING.",
                tool="replan_incident",
                decision="REPLANNING",
                reason=invalidation_reason,
            )

            plan_doc = db["recovery_plans"].find_one({"incident_id": incident_id}, {"_id": 0})
            replan_ctx = {}
            if plan_doc:
                from app.schemas.recovery_plan import RecoveryPlan
                try:
                    p_obj = RecoveryPlan(**plan_doc)
                    replan_ctx = get_replanning_context(
                        p_obj,
                        new_incident_affected_supplier=affected_supp,
                    )
                except Exception:
                    pass

            return ToolResult(
                tool_name=tool_name,
                success=True,
                data={"incident_id": incident_id, "state": AgentState.REPLANNING.value, "replanning_context": replan_ctx},
                summary=f"Incident {incident_id} entered REPLANNING state: {invalidation_reason}",
            )

        return ToolResult(
            tool_name=tool_name,
            success=False,
            error=f"Unknown tool '{tool_name}'",
            summary=f"Unknown tool requested: {tool_name}",
        )

    except KeyError as e:
        return ToolResult(
            tool_name=tool_name,
            success=False,
            error=f"Missing required parameter: {e}",
            summary=f"Tool {tool_name} failed: missing required parameter {e}.",
        )
    except Exception as e:
        return ToolResult(
            tool_name=tool_name,
            success=False,
            error=str(e),
            summary=f"Tool {tool_name} encountered an error: {e}",
        )
