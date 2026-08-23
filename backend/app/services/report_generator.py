"""
app/services/report_generator.py
Owner: Backend & Intelligence Services

Generates comprehensive, easy-to-understand, information-rich Operations Reports
using LLM synthesis and professional PDF generation via fpdf2.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import httpx
from pymongo.database import Database
from fpdf import FPDF

from app.config import settings


# ==============================================================================
# 1. TEXT SANITIZATION (LATIN-1 SAFETY FOR FPDF2)
# ==============================================================================

def sanitize_text(text: Any) -> str:
    """
    Sanitize text for standard fpdf2 Helvetica/Times font encodings (Latin-1).
    Replaces common Unicode typography (quotes, dashes, bullets, arrows)
    with safe ASCII/Latin-1 equivalents before rendering.
    """
    if text is None:
        return ""
    s = str(text)
    replacements = {
        "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
        "\u2013": "-", "\u2014": " -- ", "\u2026": "...",
        "\u2022": "*", "\u25cf": "*", "\u25aa": "*", "\u2192": "->",
        "\u2190": "<-", "\u2713": "[OK]", "\u2714": "[OK]", "\u2717": "[X]",
        "\u2718": "[X]", "\u2248": "~", "\u2264": "<=", "\u2265": ">=",
        "\u00b1": "+/-", "\u00d7": "x", "\u20ac": "EUR ", "\u00a3": "GBP ",
        "\u00a5": "JPY ", "\u20bd": "RUB ", "\u20b9": "INR ",
    }
    for orig, rep in replacements.items():
        s = s.replace(orig, rep)
    
    # Encode to latin-1 replacing any unknown characters with '?'
    return s.encode("latin-1", "replace").decode("latin-1")


# ==============================================================================
# 2. CONTEXT AGGREGATION
# ==============================================================================

def fetch_report_context(
    db: Database,
    incident_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    include_diagnostics: bool = False,
    order_id: Optional[str] = None,
    supplier_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Collects complete operational facts from MongoDB:
    incidents, inventory, purchase orders, suppliers, production orders,
    recovery plans, and audit activity.
    """
    # 1. Query Incidents
    incident_query: Dict[str, Any] = {}
    if incident_id:
        incident_query = {"incident_id": incident_id}
    else:
        incident_query = {"type": {"$ne": "DATA_INCONSISTENCY"}}
        if start_date or end_date:
            date_filter: Dict[str, str] = {}
            if start_date:
                date_filter["$gte"] = start_date.isoformat()
            if end_date:
                date_filter["$lte"] = end_date.isoformat()
            incident_query["created_at"] = date_filter

    incidents = list(db["incidents"].find(incident_query, {"_id": 0}).sort("created_at", -1))
    incident_ids = [inc.get("incident_id") for inc in incidents if inc.get("incident_id")]

    # 2. Audit logs
    audit_filter: Dict[str, Any] = {"incident_id": {"$in": incident_ids}} if incident_ids else {}
    if not incident_id and not incident_ids:
        logs = list(db["audit_logs"].find({}, {"_id": 0}).sort("timestamp", -1).limit(50))
    else:
        logs = list(db["audit_logs"].find(audit_filter, {"_id": 0}).sort("timestamp", 1)) if incident_ids else []

    # 3. Affected Components & Inventory
    affected_components = list({
        inc.get("affected_component") for inc in incidents if inc.get("affected_component")
    })
    
    inv_query = {"component_id": {"$in": affected_components}} if affected_components else {}
    inventory = list(db["inventory"].find(inv_query, {"_id": 0})) if (affected_components or not incident_id) else []
    if not affected_components and not incident_id:
        inventory = list(db["inventory"].find({}, {"_id": 0}).limit(20))

    # Compute inventory runway
    for item in inventory:
        daily = float(item.get("daily_usage") or 0)
        usable = float(item.get("usable_stock") or 0)
        current = float(item.get("current_stock") or 0)
        safety = float(item.get("safety_stock") or 0)
        runway = round(usable / daily, 1) if daily > 0 else 999.0
        item["days_of_supply"] = runway
        item["stockout_risk"] = "HIGH" if runway < 3.0 else ("MEDIUM" if runway < 7.0 else "LOW")
        item["safety_stock_deficit"] = max(0.0, safety - usable)

    # 4. Purchase Orders
    affected_pos = list({inc.get("affected_po") for inc in incidents if inc.get("affected_po")})
    po_query: Dict[str, Any] = {}
    if affected_components or affected_pos:
        clauses = []
        if affected_components:
            clauses.append({"component_id": {"$in": affected_components}})
        if affected_pos:
            clauses.append({"po_id": {"$in": affected_pos}})
        po_query = {"$or": clauses} if len(clauses) > 1 else clauses[0]
    
    purchase_orders = list(db["purchase_orders"].find(po_query, {"_id": 0})) if (po_query or not incident_id) else []
    if not po_query and not incident_id:
        purchase_orders = list(db["purchase_orders"].find({}, {"_id": 0}).limit(25))

    # 5. Suppliers
    supplier_ids = list({po.get("supplier_id") for po in purchase_orders if po.get("supplier_id")})
    supp_query = {"supplier_id": {"$in": supplier_ids}} if supplier_ids else {}
    suppliers = list(db["suppliers"].find(supp_query, {"_id": 0})) if (supp_query or not incident_id) else []
    if not supp_query and not incident_id:
        suppliers = list(db["suppliers"].find({}, {"_id": 0}).limit(20))

    # 6. Production Orders
    prod_query = {"component_id": {"$in": affected_components}} if affected_components else {}
    production_orders = list(db["production_orders"].find(prod_query, {"_id": 0})) if (prod_query or not incident_id) else []
    if not prod_query and not incident_id:
        production_orders = list(db["production_orders"].find({}, {"_id": 0}).limit(20))

    # 7. Recovery Plans
    plan_query = {"incident_id": {"$in": incident_ids}} if incident_ids else {}
    recovery_plans = list(db["recovery_plans"].find(plan_query, {"_id": 0})) if incident_ids else []

    # 8. Diagnostics
    diagnostics = []
    if include_diagnostics:
        diagnostics = list(db["integration_errors"].find({}, {"_id": 0}).sort("timestamp", -1).limit(20))
        orphaned_logs = list(db["audit_logs"].find({"incident_id": None}, {"_id": 0}).sort("timestamp", -1).limit(20))
        logs.extend(orphaned_logs)

    # High-level aggregated statistics
    total_po_value = sum(float(po.get("total_value") or 0) for po in purchase_orders)
    critical_count = sum(1 for inc in incidents if str(inc.get("severity", "")).upper() == "CRITICAL")
    high_count = sum(1 for inc in incidents if str(inc.get("severity", "")).upper() == "HIGH")
    
    primary_incident = incidents[0] if incidents else None
    primary_plan = recovery_plans[0] if recovery_plans else None

    # Calculate min runway
    min_runway = min([item["days_of_supply"] for item in inventory], default=0.0)

    # Determine primary recovery cost
    recommended_option = None
    if primary_plan and primary_plan.get("options"):
        rec_id = primary_plan.get("recommended_option_id")
        recommended_option = next((opt for opt in primary_plan.get("options", []) if opt.get("option_id") == rec_id), primary_plan["options"][0])

    summary_stats = {
        "scope": incident_id or "Multi-Incident Operations Scope",
        "incident_count": len(incidents),
        "critical_count": critical_count,
        "high_count": high_count,
        "min_days_of_supply": min_runway if inventory else "N/A",
        "total_po_value_exposed": total_po_value,
        "affected_components_count": len(inventory),
        "impacted_production_orders_count": len(production_orders),
        "recommended_recovery_cost": recommended_option.get("total_cost") if recommended_option else 0.0,
        "requires_human_approval": primary_plan.get("requires_human_approval", False) if primary_plan else False,
        "approval_threshold_usd": primary_plan.get("approval_threshold_usd", settings.AUTONOMOUS_APPROVAL_LIMIT_USD) if primary_plan else settings.AUTONOMOUS_APPROVAL_LIMIT_USD,
        "generation_time_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    }

    return {
        "summary_stats": summary_stats,
        "primary_incident": primary_incident,
        "incidents": incidents,
        "inventory": inventory,
        "purchase_orders": purchase_orders,
        "suppliers": suppliers,
        "production_orders": production_orders,
        "recovery_plans": recovery_plans,
        "primary_plan": primary_plan,
        "recommended_option": recommended_option,
        "audit_logs": logs,
        "diagnostics": diagnostics,
        "include_diagnostics": include_diagnostics,
    }


# ==============================================================================
# 3. LLM SYNTHESIS LAYER
# ==============================================================================

def _build_deterministic_narrative(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Intelligent domain-expert narrative synthesizer used as a reliable fallback
    when no LLM API key is present or network calls are unavailable.
    Produces rich, clear, professional executive prose.
    """
    stats = context["summary_stats"]
    primary_inc = context.get("primary_incident")
    primary_plan = context.get("primary_plan")
    rec_opt = context.get("recommended_option")
    inventory = context.get("inventory", [])
    production = context.get("production_orders", [])
    suppliers = context.get("suppliers", [])
    pos = context.get("purchase_orders", [])

    # 1. Executive Summary
    if primary_inc:
        inc_type = str(primary_inc.get("type", "Disruption")).replace("_", " ").title()
        sev = str(primary_inc.get("severity", "MEDIUM")).upper()
        comp = primary_inc.get("affected_component") or "Component"
        delay = primary_inc.get("delay_days", 0)
        status = primary_inc.get("status", "ACTIVE")
        exec_summary = (
            f"An operational incident ({primary_inc.get('incident_id')}) classified as {sev} severity "
            f"has been detected, involving {inc_type.lower()} on {comp}. The disruption introduces an "
            f"estimated delay of {delay} day(s), creating immediate pressure on assembly schedules and "
            f"downstream fulfillment. The incident is currently in '{status}' status under automated "
            f"agent surveillance."
        )
    else:
        inc_count = stats["incident_count"]
        exec_summary = (
            f"This operational report encompasses {inc_count} supply chain event(s) across recent operations. "
            f"Analysis reveals {stats['critical_count']} critical and {stats['high_count']} high-severity issue(s) "
            f"requiring proactive resilience measures. Active mitigation workflows are continuously managing "
            f"inventory buffer thresholds and purchase order schedules."
        )

    # 2. Impact Assessment
    if inventory:
        inv_items_text = ", ".join([
            f"{item.get('component_id')} ({item.get('days_of_supply', 'N/A')} days supply remaining, usable: {item.get('usable_stock')}/{item.get('current_stock')})"
            for item in inventory[:3]
        ])
        prod_count = len(production)
        po_val = stats["total_po_value_exposed"]
        impact = (
            f"Inventory analysis indicates stock runway constraints across key parts: {inv_items_text}. "
            f"A total of {prod_count} active production order(s) and Rs. {po_val:,.2f} in purchase order value "
            f"are currently exposed to delivery variance. Without mitigation, critical stockouts could compromise "
            f"production continuity within {stats['min_days_of_supply']} days."
        )
    else:
        impact = (
            f"Overall financial exposure across monitored purchase orders stands at Rs. {stats['total_po_value_exposed']:,.2f}. "
            f"Production schedules remain operational, though supplier delivery timelines require close tracking."
        )

    # 3. Decision & Recovery Strategy
    if primary_plan and rec_opt:
        cost = rec_opt.get("total_cost", 0.0)
        threshold = stats["approval_threshold_usd"]
        supp_name = rec_opt.get("supplier_name") or rec_opt.get("supplier_id") or "designated supplier"
        lead_time = rec_opt.get("lead_time_days", "N/A")
        reason = primary_plan.get("recommendation_reason") or "Optimal balance between recovery speed and financial cost."
        
        gov_text = (
            f"At Rs. {cost:,.2f}, this recovery plan exceeds the Rs. {threshold:,.2f} autonomous threshold, "
            f"requiring Human-in-the-Loop coordinator authorization."
            if stats["requires_human_approval"]
            else f"At Rs. {cost:,.2f}, this plan is below the Rs. {threshold:,.2f} threshold and is authorized for autonomous execution."
        )

        recovery_strategy = (
            f"The decision engine evaluated alternative mitigation pathways and selected Option '{rec_opt.get('option_id')}' "
            f"utilizing {supp_name} (Estimated lead time: {lead_time} days, Total cost: Rs. {cost:,.2f}). "
            f"Rationale: {reason}. {gov_text}"
        )
    else:
        recovery_strategy = (
            "Multi-source supplier evaluations are actively monitored. Where delays occur, expedited shipping "
            "and secondary qualified supplier allocations are evaluated against autonomous budget thresholds."
        )

    # 4. Governance & Policy Notes
    threshold = stats["approval_threshold_usd"]
    governance = (
        f"All automated decisions strictly adhere to corporate governance limits. Recovery expenditures above "
        f"Rs. {threshold:,.2f} require formal coordinator sign-off. Full cryptographic audit trails and ERP "
        f"synchronization events are recorded for every state transition."
    )

    # 5. Action Items
    action_items = [
        "Monitor supplier dispatch status and verify carrier tracking updates daily.",
        f"Ensure buffer inventory for affected components does not breach minimum safety stock ({stats['min_days_of_supply']} days remaining).",
        "Validate production scheduling priority for high-value orders approaching commitment deadlines.",
        "Review autonomous threshold limits with procurement leadership if disruption frequency escalates.",
    ]
    if stats["requires_human_approval"]:
        action_items.insert(0, "URGENT: Human Coordinator approval required for pending recovery plan expenditure.")

    return {
        "executive_summary": exec_summary,
        "impact_assessment": impact,
        "recovery_strategy": recovery_strategy,
        "governance_and_approval": governance,
        "action_items": action_items,
    }


def generate_report_narrative(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synthesizes operational data into a clear, comprehensive, executive narrative.
    Attempts LLM generation via Groq/OpenAI compatible API if configured,
    and falls back cleanly to the deterministic narrative generator.
    """
    api_key = settings.GROQ_API_KEY
    provider = settings.LLM_PROVIDER.lower() if settings.LLM_PROVIDER else "groq"
    model = settings.GROQ_MODEL or "llama-3.3-70b-versatile"

    if not api_key or api_key.startswith("gsk_xxxx") or api_key == "changeme":
        # No active API key configured -> Use deterministic synthesis
        return _build_deterministic_narrative(context)

    # Build prompt for LLM
    stats = context["summary_stats"]
    primary_inc = context.get("primary_incident", {})
    primary_plan = context.get("primary_plan", {})
    inventory_summary = [
        {"component": i.get("component_id"), "usable": i.get("usable_stock"), "daily_usage": i.get("daily_usage"), "days_of_supply": i.get("days_of_supply")}
        for i in context.get("inventory", [])[:5]
    ]
    po_summary = [
        {"po_id": p.get("po_id"), "supplier": p.get("supplier_id"), "status": p.get("status"), "value": p.get("total_value")}
        for p in context.get("purchase_orders", [])[:5]
    ]

    prompt_data = {
        "scope": stats["scope"],
        "incident": primary_inc,
        "summary_metrics": stats,
        "inventory_status": inventory_summary,
        "purchase_orders": po_summary,
        "recovery_plan": primary_plan,
    }

    system_instruction = """You are the Chief Supply Chain Resilience Officer. 
Generate a clear, comprehensive, professional, and easy-to-understand executive operations report based on the provided supply chain facts.

Output ONLY valid JSON with the following exact keys:
{
  "executive_summary": "<2-3 sentence plain-English executive summary of the incident/operations, root cause, and current state>",
  "impact_assessment": "<2-3 sentences detailing stockout risk, days of supply runway, and affected production lines>",
  "recovery_strategy": "<2-3 sentences explaining the recommended recovery option, supplier choice, cost vs speed trade-offs, and approval status>",
  "governance_and_approval": "<1-2 sentences summarizing compliance with the $50,000 autonomous approval threshold>",
  "action_items": [
    "<Action item 1>",
    "<Action item 2>",
    "<Action item 3>",
    "<Action item 4>"
  ]
}
No markdown backticks, no preamble, output pure JSON only."""

    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": f"Synthesize this operational context:\n{json.dumps(prompt_data, default=str)}"}
            ],
            "temperature": 0.1,
            "max_tokens": 1000,
            "response_format": {"type": "json_object"} if "llama" in model.lower() else None
        }

        with httpx.Client(timeout=6.0) as client:
            resp = client.post(
                url,
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={k: v for k, v in payload.items() if v is not None}
            )
            if resp.status_code == 200:
                res_data = resp.json()
                content = res_data["choices"][0]["message"]["content"]
                # Parse JSON
                parsed = json.loads(content)
                if all(k in parsed for k in ["executive_summary", "impact_assessment", "recovery_strategy", "action_items"]):
                    return parsed
    except Exception:
        # Graceful fallback on network timeout or parse failure
        pass

    return _build_deterministic_narrative(context)


# ==============================================================================
# 4. PROFESSIONAL PDF BUILDER (FPDF2)
# ==============================================================================

class SupplyChainReportPDF(FPDF):
    """
    Styled PDF Document generator for Supply Chain Operations & Resilience Reports.
    """

    def __init__(self, scope_title: str):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.scope_title = scope_title
        self.set_auto_page_break(auto=True, margin=15)
        self.alias_nb_pages()

    def header(self):
        # Top branding header bar
        self.set_fill_color(30, 58, 138)  # Deep Navy Blue
        self.rect(0, 0, 210, 8, "F")

        # Subtle top text
        self.set_y(10)
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(100, 116, 139)  # Slate-500
        self.cell(0, 4, sanitize_text("SUPPLY CHAIN RESILIENCE INTELLIGENCE SYSTEM"), align="L")
        self.cell(0, 4, sanitize_text(f"SCOPE: {self.scope_title.upper()}"), align="R", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "", 7)
        self.set_text_color(148, 163, 184)  # Slate-400
        self.cell(0, 4, sanitize_text("Confidential -- Automated Operational Brief generated by Supply Chain Resilience Agent"), align="L")
        self.cell(0, 4, sanitize_text(f"Page {self.page_no()} of {{nb}}"), align="R")


def build_operations_pdf(context: Dict[str, Any], narrative: Dict[str, Any]) -> bytes:
    """
    Constructs a clean, professional, publication-grade PDF report using fpdf2.
    """
    stats = context["summary_stats"]
    primary_inc = context.get("primary_incident")
    primary_plan = context.get("primary_plan")
    rec_opt = context.get("recommended_option")
    inventory = context.get("inventory", [])
    production = context.get("production_orders", [])
    pos = context.get("purchase_orders", [])
    suppliers = context.get("suppliers", [])
    audit_logs = context.get("audit_logs", [])
    diagnostics = context.get("diagnostics", [])

    pdf = SupplyChainReportPDF(scope_title=str(stats.get("scope", "Operations")))
    pdf.add_page()
    
    # ── 1. Document Title Banner ──────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(15, 23, 42)  # Slate-900
    pdf.cell(0, 8, sanitize_text("Supply Chain Resilience & Operations Report"), new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 5, sanitize_text(f"Generated: {stats['generation_time_utc']}  |  Scope: {stats['scope']}"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # ── 2. KPI Summary Cards Strip ────────────────────────────────────────────
    card_w = 44
    card_h = 18
    start_y = pdf.get_y()

    # Severity color
    sev = str(primary_inc.get("severity", "MEDIUM") if primary_inc else "OPERATIONAL").upper()
    sev_bg = (254, 242, 242) if sev == "CRITICAL" else ((255, 247, 237) if sev == "HIGH" else (241, 245, 249))
    sev_fg = (220, 38, 38) if sev == "CRITICAL" else ((234, 88, 12) if sev == "HIGH" else (30, 58, 138))

    cards_data = [
        {"title": "SEVERITY", "value": sev, "sub": primary_inc.get("status", "ACTIVE") if primary_inc else "NORMAL", "bg": sev_bg, "fg": sev_fg},
        {"title": "STOCK RUNWAY", "value": f"{stats['min_days_of_supply']} Days", "sub": f"{len(inventory)} Parts Monitored", "bg": (241, 245, 249), "fg": (30, 58, 138)},
        {"title": "EXPOSED PO VALUE", "value": f"Rs. {stats['total_po_value_exposed']:,.0f}", "sub": f"{len(pos)} Orders Tracked", "bg": (241, 245, 249), "fg": (30, 58, 138)},
        {"title": "GOVERNANCE", "value": "HUMAN REVIEW" if stats["requires_human_approval"] else "AUTONOMOUS", "sub": f"Threshold: Rs. {stats['approval_threshold_usd']:,.0f}", "bg": (254, 243, 199) if stats["requires_human_approval"] else (240, 253, 244), "fg": (180, 83, 9) if stats["requires_human_approval"] else (22, 101, 52)},
    ]

    for idx, card in enumerate(cards_data):
        x = pdf.l_margin + idx * (card_w + 3.3)
        pdf.set_fill_color(*card["bg"])
        pdf.set_draw_color(203, 213, 225)
        pdf.rect(x, start_y, card_w, card_h, "DF")

        pdf.set_xy(x + 2, start_y + 2)
        pdf.set_font("Helvetica", "B", 6.5)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(card_w - 4, 3, sanitize_text(card["title"]), align="L")

        pdf.set_xy(x + 2, start_y + 6)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*card["fg"])
        pdf.cell(card_w - 4, 6, sanitize_text(card["value"]), align="L")

        pdf.set_xy(x + 2, start_y + 12)
        pdf.set_font("Helvetica", "", 6.5)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(card_w - 4, 4, sanitize_text(card["sub"]), align="L")

    pdf.set_y(start_y + card_h + 5)

    def render_section_heading(title: str):
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(30, 58, 138)  # Cobalt Navy
        # Left blue accent bar
        pdf.set_fill_color(30, 58, 138)
        pdf.rect(pdf.l_margin, pdf.get_y() + 1, 2.5, 5, "F")
        pdf.set_x(pdf.l_margin + 5)
        pdf.cell(0, 7, sanitize_text(title), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)

    # ── 3. Executive Summary Narrative ────────────────────────────────────────
    render_section_heading("Executive Summary")
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(226, 232, 240)
    
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(30, 41, 59)
    pdf.multi_cell(pdf.epw, 4.5, sanitize_text(narrative.get("executive_summary", "")), border=0)
    pdf.ln(2)

    # ── 4. Impact Assessment Narrative ────────────────────────────────────────
    render_section_heading("Supply Chain Impact Assessment")
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(30, 41, 59)
    pdf.multi_cell(pdf.epw, 4.5, sanitize_text(narrative.get("impact_assessment", "")))
    pdf.ln(2)

    # Inventory Runway Table
    if inventory:
        pdf.set_font("Helvetica", "B", 7.5)
        pdf.set_fill_color(241, 245, 249)
        pdf.set_text_color(51, 65, 85)
        
        col_w = [30, 28, 28, 28, 32, 40]
        headers = ["Component", "Usable Stock", "Total Stock", "Daily Burn", "Days of Supply", "Location / Status"]
        
        for i, h in enumerate(headers):
            pdf.cell(col_w[i], 5.5, sanitize_text(h), border=1, fill=True, align="C")
        pdf.ln()

        pdf.set_font("Helvetica", "", 7.5)
        pdf.set_text_color(15, 23, 42)
        for item in inventory[:6]:
            fill = (item.get("days_of_supply", 999) < 3.0)
            if fill:
                pdf.set_fill_color(254, 242, 242)
            else:
                pdf.set_fill_color(255, 255, 255)
            
            pdf.cell(col_w[0], 5, sanitize_text(item.get("component_id", "-")), border=1, fill=True)
            pdf.cell(col_w[1], 5, sanitize_text(str(item.get("usable_stock", "-"))), border=1, fill=True, align="R")
            pdf.cell(col_w[2], 5, sanitize_text(str(item.get("current_stock", "-"))), border=1, fill=True, align="R")
            pdf.cell(col_w[3], 5, sanitize_text(str(item.get("daily_usage", "-"))), border=1, fill=True, align="R")
            pdf.cell(col_w[4], 5, sanitize_text(f"{item.get('days_of_supply', 'N/A')} days"), border=1, fill=True, align="R")
            pdf.cell(col_w[5], 5, sanitize_text(f"{item.get('location', '-')} ({item.get('stockout_risk', 'LOW')} Risk)"), border=1, fill=True)
            pdf.ln()
        pdf.ln(3)

    # ── 5. Recovery Strategy & Options Evaluated ──────────────────────────────
    render_section_heading("Strategic Recovery & Decision Rationale")
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(30, 41, 59)
    pdf.multi_cell(pdf.epw, 4.5, sanitize_text(narrative.get("recovery_strategy", "")))
    pdf.ln(2)

    # Recovery Options Table (if plan exists)
    if primary_plan and primary_plan.get("options"):
        pdf.set_font("Helvetica", "B", 7.5)
        pdf.set_fill_color(241, 245, 249)
        pdf.set_text_color(51, 65, 85)
        
        opt_cols = [22, 50, 40, 26, 22, 26]
        opt_headers = ["Option", "Action Description", "Supplier / Route", "Total Cost", "Lead Time", "Status"]
        for i, h in enumerate(opt_headers):
            pdf.cell(opt_cols[i], 5.5, sanitize_text(h), border=1, fill=True, align="C")
        pdf.ln()

        pdf.set_font("Helvetica", "", 7.5)
        rec_id = primary_plan.get("recommended_option_id")
        for opt in primary_plan.get("options", [])[:4]:
            is_rec = (opt.get("option_id") == rec_id)
            if is_rec:
                pdf.set_fill_color(240, 253, 244)  # Light Green highlight
                pdf.set_text_color(22, 101, 52)
            else:
                pdf.set_fill_color(255, 255, 255)
                pdf.set_text_color(15, 23, 42)

            pdf.cell(opt_cols[0], 5, sanitize_text(f"{opt.get('option_id')}{' [REC]' if is_rec else ''}"), border=1, fill=True)
            pdf.cell(opt_cols[1], 5, sanitize_text(str(opt.get("action", opt.get("description", "-")))[:32]), border=1, fill=True)
            pdf.cell(opt_cols[2], 5, sanitize_text(str(opt.get("supplier_name", opt.get("supplier_id", "-")))[:24]), border=1, fill=True)
            pdf.cell(opt_cols[3], 5, sanitize_text(f"Rs. {float(opt.get('total_cost', 0)):,.2f}"), border=1, fill=True, align="R")
            pdf.cell(opt_cols[4], 5, sanitize_text(f"{opt.get('lead_time_days', '-')} days"), border=1, fill=True, align="R")
            pdf.cell(opt_cols[5], 5, sanitize_text("RECOMMENDED" if is_rec else "ALTERNATIVE"), border=1, fill=True, align="C")
            pdf.ln()
        pdf.ln(3)

    # ── 6. Governance & Action Items ──────────────────────────────────────────
    render_section_heading("Actionable Roadmap & Operational Directives")
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(30, 41, 59)
    for idx, item in enumerate(narrative.get("action_items", [])):
        pdf.set_x(pdf.l_margin + 2)
        pdf.cell(5, 4.5, sanitize_text(f"{idx + 1}."), align="L")
        pdf.set_x(pdf.l_margin + 7)
        pdf.multi_cell(pdf.epw - 7, 4.5, sanitize_text(item))
    pdf.ln(2)

    # ── 7. Activity & Audit Trail Timeline ────────────────────────────────────
    if audit_logs:
        render_section_heading("Audited Milestones & State Transitions")
        pdf.set_font("Helvetica", "B", 7.5)
        pdf.set_fill_color(241, 245, 249)
        pdf.set_text_color(51, 65, 85)

        log_cols = [38, 42, 32, 74]
        log_headers = ["Timestamp (UTC)", "Action / Event", "Decision State", "Details / Rationale"]
        for i, h in enumerate(log_headers):
            pdf.cell(log_cols[i], 5.5, sanitize_text(h), border=1, fill=True, align="C")
        pdf.ln()

        pdf.set_font("Helvetica", "", 7.0)
        pdf.set_text_color(15, 23, 42)
        for log in audit_logs[-8:]:  # Show recent 8 events
            ts = str(log.get("timestamp", log.get("ingested_at", "-"))).replace("T", " ")[:19]
            action = str(log.get("action", log.get("event_type", "Event")))[:28]
            dec = str(log.get("decision", log.get("status", "-")))[:20]
            reason = str(log.get("reason", log.get("result", "-")))[:50]

            pdf.cell(log_cols[0], 5, sanitize_text(ts), border=1)
            pdf.cell(log_cols[1], 5, sanitize_text(action), border=1)
            pdf.cell(log_cols[2], 5, sanitize_text(dec), border=1)
            pdf.cell(log_cols[3], 5, sanitize_text(reason), border=1)
            pdf.ln()
        pdf.ln(2)

    # ── 8. Diagnostics Appendix (Optional) ────────────────────────────────────
    if diagnostics:
        render_section_heading("Diagnostics & Engineering Appendix")
        pdf.set_font("Helvetica", "", 7.0)
        for err in diagnostics[:5]:
            ts = str(err.get("timestamp", "-")).replace("T", " ")[:19]
            wf = str(err.get("workflow", "-"))
            etype = str(err.get("error_type", "-"))
            msg = str(err.get("error_message", "-"))[:75]
            pdf.cell(0, 4.5, sanitize_text(f"[{ts}] {wf} | {etype}: {msg}"), new_x="LMARGIN", new_y="NEXT")

    return bytes(pdf.output())


def generate_report_bundle(
    db: Database,
    incident_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    include_diagnostics: bool = False,
    order_id: Optional[str] = None,
    supplier_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Convenience method that aggregates context, runs LLM synthesis,
    and returns both the structured narrative and the compiled PDF bytes.
    """
    context = fetch_report_context(
        db=db,
        incident_id=incident_id,
        start_date=start_date,
        end_date=end_date,
        include_diagnostics=include_diagnostics,
        order_id=order_id,
        supplier_id=supplier_id,
    )
    narrative = generate_report_narrative(context)
    pdf_bytes = build_operations_pdf(context, narrative)
    
    return {
        "context": context,
        "narrative": narrative,
        "pdf_bytes": pdf_bytes,
        "summary_stats": context["summary_stats"],
    }
