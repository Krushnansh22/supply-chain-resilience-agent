"""
app/agent/escalation_engine.py
Owner: Developer 1 (Agent) / Developer 3 (Decision Engine)

Comprehensive multi-criteria escalation evaluation and Decision Brief generation.
Implements the escalation governance rules from PS Section 4.9 and references/decision-frameworks.md.
"""

from typing import Optional
from pydantic import BaseModel, Field
from app.config import settings
from app.schemas.recovery_plan import RecoveryPlan, RecoveryPlanOption


class EscalationCriterion:
    COST_EXCEEDS_THRESHOLD = "COST_EXCEEDS_THRESHOLD"
    NO_SUPPLIER_MEETS_DEADLINE = "NO_SUPPLIER_MEETS_DEADLINE"
    HIGH_QUALITY_RISK = "HIGH_QUALITY_RISK"
    SERIOUS_MULTI_OBJECTIVE_TRADEOFFS = "SERIOUS_MULTI_OBJECTIVE_TRADEOFFS"
    UNAVOIDABLE_PRODUCTION_SHUTDOWN = "UNAVOIDABLE_PRODUCTION_SHUTDOWN"
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"
    DATA_INCONSISTENCY = "DATA_INCONSISTENCY"


class EscalationEvaluation(BaseModel):
    requires_escalation: bool
    trigger_criterion: Optional[str] = None
    trigger_reason: str = ""
    decision_brief: Optional[str] = None


def evaluate_escalation(
    incident_id: str,
    incident_type: str,
    severity: str,
    component_id: Optional[str],
    plan: Optional[RecoveryPlan] = None,
    production_orders: Optional[list[dict]] = None,
    days_of_supply: float = 0.0,
    budget_exhausted: bool = False,
    custom_reason: Optional[str] = None,
) -> EscalationEvaluation:
    """
    Evaluates whether an incident requires human escalation based on core criteria.
    If escalated, formats a professional Decision Brief matching references/decision-frameworks.md.
    """
    # 1. Budget exhausted trigger
    if budget_exhausted:
        brief = _build_decision_brief(
            situation=f"Incident {incident_id} ({incident_type}) reached the maximum agent tool-call budget without finding a definitive autonomous resolution.",
            cost_of_inaction="Delayed recovery decision risks unexpected stockout or unplanned production interruption.",
            options_summary="Options explored during autonomous investigation have been logged to the audit timeline.",
            recommendation="Manual operator intervention required to select or configure a custom procurement recovery plan.",
            trigger=EscalationCriterion.BUDGET_EXHAUSTED,
            time_sensitivity="Immediate operator review recommended within 2 hours.",
        )
        return EscalationEvaluation(
            requires_escalation=True,
            trigger_criterion=EscalationCriterion.BUDGET_EXHAUSTED,
            trigger_reason="Tool call step budget exhausted before achieving autonomous terminal state.",
            decision_brief=brief,
        )

    # 2. Data Inconsistency / Stale or Negative Data Trigger
    if incident_type == "STALE_INVENTORY" or (custom_reason and "data inconsistency" in custom_reason.lower()):
        comp = component_id or "affected component"
        brief = _build_decision_brief(
            situation=f"Data Inconsistency / Physical Count Discrepancy for {comp} ({incident_id}): Physical inventory differs from system count or contains negative values.",
            cost_of_inaction="Procuring against an uncalibrated stock baseline leads to severe over-spend or unexpected stockouts.",
            options_summary=f"- Input verified physical count on the Approvals page to calibrate system inventory for {comp}.",
            recommendation=f"Please provide revised physical stock count for {comp} in the Approval form to update the database properly.",
            trigger=EscalationCriterion.DATA_INCONSISTENCY,
            time_sensitivity="Input verified physical stock count to calibrate baseline.",
        )
        return EscalationEvaluation(
            requires_escalation=True,
            trigger_criterion=EscalationCriterion.DATA_INCONSISTENCY,
            trigger_reason=f"Data discrepancy detected for {comp}. Revised physical count required from coordinator.",
            decision_brief=brief,
        )

    # 3. Plan-based checks
    if plan and plan.options:
        rec_opt = next((o for o in plan.options if o.option_id == plan.recommended_option_id), None)
        valid_options = [o for o in plan.options if o.constraints_satisfied]

        # Check A: No valid option meets deadlines/constraints
        if not valid_options:
            brief = _build_decision_brief(
                situation=f"Supply disruption for {component_id} ({incident_id}): No available supplier candidate can fulfill the required quantity within the required SLA deadline.",
                cost_of_inaction=f"Production line stoppage for dependent orders ({len(production_orders or [])} orders at risk).",
                options_summary="\n".join([f"- Option {o.option_id}: Rejected due to: {o.rejection_reason}" for o in plan.options[:4]]),
                recommendation="Evaluate whether downstream production schedule can be shifted, or authorize emergency premium freight.",
                trigger=EscalationCriterion.NO_SUPPLIER_MEETS_DEADLINE,
                time_sensitivity="Urgent: Production schedule slips if no resolution within 24 hours.",
            )
            return EscalationEvaluation(
                requires_escalation=True,
                trigger_criterion=EscalationCriterion.NO_SUPPLIER_MEETS_DEADLINE,
                trigger_reason="No candidate supplier can meet the required delivery deadline without constraint violations.",
                decision_brief=brief,
            )

        # Check B: Recommended plan exceeds autonomous dollar threshold
        if rec_opt and rec_opt.total_cost > settings.AUTONOMOUS_APPROVAL_LIMIT_USD:
            options_lines = []
            for opt in plan.options:
                alloc_str = ", ".join([f"{a.quantity}x from {a.supplier_id} (${a.unit_price}/unit, {a.delivery_days}d)" for a in opt.allocations])
                status = "RECOMMENDED" if opt.option_id == plan.recommended_option_id else ("VALID" if opt.constraints_satisfied else f"REJECTED ({opt.rejection_reason})")
                options_lines.append(f"- Option {opt.option_id} (${opt.total_cost:,.2f}, {opt.max_delivery_days}d): {alloc_str} — {status}")

            brief = _build_decision_brief(
                situation=f"Supply disruption for {component_id} ({incident_id}): Recommended recovery plan cost (${rec_opt.total_cost:,.2f}) exceeds autonomous limit (${settings.AUTONOMOUS_APPROVAL_LIMIT_USD:,.2f}).",
                cost_of_inaction=f"Production line stoppage for dependent orders with safety stock remaining at {days_of_supply:.1f} days.",
                options_summary="\n".join(options_lines[:4]),
                recommendation=f"Approve Option {rec_opt.option_id} (${rec_opt.total_cost:,.2f}, delivery in {rec_opt.max_delivery_days} days).",
                trigger=f"{EscalationCriterion.COST_EXCEEDS_THRESHOLD} (Cost ${rec_opt.total_cost:,.2f} > ${settings.AUTONOMOUS_APPROVAL_LIMIT_USD:,.2f})",
                time_sensitivity="Decision required before supplier quotation validity window expires.",
            )
            return EscalationEvaluation(
                requires_escalation=True,
                trigger_criterion=EscalationCriterion.COST_EXCEEDS_THRESHOLD,
                trigger_reason=f"Recovery plan cost ${rec_opt.total_cost:,.2f} exceeds autonomous approval threshold of ${settings.AUTONOMOUS_APPROVAL_LIMIT_USD:,.2f}.",
                decision_brief=brief,
            )

    # 4. Critical severity with zero inventory coverage
    if severity == "CRITICAL" and days_of_supply <= 0.5:
        brief = _build_decision_brief(
            situation=f"CRITICAL inventory emergency for {component_id}: Usable stock buffer depleted ({days_of_supply:.1f} days of supply).",
            cost_of_inaction="Immediate production line halt and breach of contractual customer delivery dates.",
            options_summary="Emergency RFQs dispatched; immediate executive coordination required.",
            recommendation="Authorize emergency expedited procurement and partial production rescheduling.",
            trigger=EscalationCriterion.UNAVOIDABLE_PRODUCTION_SHUTDOWN,
            time_sensitivity="CRITICAL: Line impact imminent within 12 hours.",
        )
        return EscalationEvaluation(
            requires_escalation=True,
            trigger_criterion=EscalationCriterion.UNAVOIDABLE_PRODUCTION_SHUTDOWN,
            trigger_reason="Immediate line shutdown risk with near-zero days of supply.",
            decision_brief=brief,
        )

    # Default: autonomous execution permitted
    return EscalationEvaluation(
        requires_escalation=False,
        trigger_criterion=None,
        trigger_reason="All recovery criteria within autonomous authority limits.",
        decision_brief=None,
    )


def _build_decision_brief(
    situation: str,
    cost_of_inaction: str,
    options_summary: str,
    recommendation: str,
    trigger: str,
    time_sensitivity: str,
) -> str:
    """Formats a concise, high-impact Decision Brief matching references/decision-frameworks.md."""
    return f"""=======================================================
DECISION BRIEF (HUMAN COORDINATOR ESCALATION)
=======================================================
SITUATION:
  {situation}

COST OF INACTION:
  {cost_of_inaction}

OPTIONS CONSIDERED:
{options_summary}

RECOMMENDATION:
  {recommendation}

WHY THIS NEEDS APPROVAL:
  {trigger}

TIME SENSITIVITY:
  {time_sensitivity}
======================================================="""
