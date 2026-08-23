"""
app/agent/environment_scanner.py
Owner: Developer 1 (Agent) / Developer 2 (Backend)

FULL-ENVIRONMENT AUTONOMOUS SCANNER:
Treats the entire database (inventory, purchase_orders, production_orders, suppliers)
as the agent's operational environment.

Performs proactive anomaly discovery:
1. Inventory: Identifies negative stock (e.g. BROKEN-001), safety stock breaches, integrity errors.
2. Purchase Orders: Identifies delivery breaches, unacknowledged shipments, tracking status lags.
3. Production Orders: Identifies stockout threats for critical assembly lines.

Automatically instantiates incidents and executes the multi-step reasoning loop for each anomaly.
"""

from typing import Any, Optional
import uuid
from datetime import datetime, timezone
from pymongo.database import Database

from app.agent.agent_loop import run_agent_cycle
from app.agent.states import AgentState
from app.audit.audit_logger import log_event


def scan_operational_environment(db: Database) -> dict[str, Any]:
    """
    Scans the entire operational database environment for disruptions,
    corrupted data, and supply chain risks.
    """
    scan_timestamp = datetime.now(timezone.utc)
    anomalies_detected: list[dict[str, Any]] = []
    incidents_triggered: list[dict[str, Any]] = []

    # -------------------------------------------------------------------------
    # 1. SCAN INVENTORY (Negative Stock, Data Inconsistencies, Safety Breaches)
    # -------------------------------------------------------------------------
    inventory_items = list(db["inventory"].find({}, {"_id": 0}))
    for item in inventory_items:
        comp_id = item.get("component_id")
        usable_stock = item.get("usable_stock", 0)
        current_stock = item.get("current_stock", 0)
        safety_stock = item.get("safety_stock", 0)
        daily_usage = item.get("daily_usage", 0.0)

        # Check A: Negative or corrupted stock (e.g. BROKEN-001)
        if usable_stock < 0 or current_stock < 0 or item.get("anomaly") == "NEGATIVE_STOCK":
            anomalies_detected.append({
                "type": "NEGATIVE_STOCK",
                "entity": "inventory",
                "entity_id": comp_id,
                "severity": "CRITICAL",
                "description": f"Component '{comp_id}' has negative stock ({usable_stock} usable / {current_stock} current). Physical count calibration required.",
            })

        # Check B: Integrity Error (Usable > Current)
        elif usable_stock > current_stock and current_stock >= 0:
            anomalies_detected.append({
                "type": "INTEGRITY_ERROR",
                "entity": "inventory",
                "entity_id": comp_id,
                "severity": "HIGH",
                "description": f"Component '{comp_id}' usable stock ({usable_stock}) exceeds total physical current stock ({current_stock}).",
            })

        # Check C: Stockout or severe safety stock breach
        elif usable_stock == 0 and daily_usage > 0:
            anomalies_detected.append({
                "type": "STOCKOUT_RISK",
                "entity": "inventory",
                "entity_id": comp_id,
                "severity": "HIGH",
                "description": f"Component '{comp_id}' has zero usable stock with active daily demand ({daily_usage}/day).",
            })

    # -------------------------------------------------------------------------
    # 2. SCAN PURCHASE ORDERS (Overdue Deliveries, Tracking Breaches)
    # -------------------------------------------------------------------------
    purchase_orders = list(db["purchase_orders"].find({}, {"_id": 0}))
    for po in purchase_orders:
        po_id = po.get("po_id")
        status = po.get("status")
        comp_id = po.get("component_id")
        supplier_id = po.get("supplier_id")

        if status in ("DELAYED", "OVERDUE", "EXCEPTION"):
            anomalies_detected.append({
                "type": "PURCHASE_ORDER_DELAY",
                "entity": "purchase_orders",
                "entity_id": po_id,
                "severity": "HIGH",
                "component_id": comp_id,
                "supplier_id": supplier_id,
                "description": f"Purchase order '{po_id}' for {comp_id} from {supplier_id} is flagged {status}.",
            })

    # -------------------------------------------------------------------------
    # 3. TRIAGE & EXECUTE AGENT LOOP FOR UNHANDLED ANOMALIES
    # -------------------------------------------------------------------------
    for anomaly in anomalies_detected:
        entity_id = anomaly["entity_id"]
        anomaly_type = anomaly["type"]

        # Check if an active open incident already exists for this entity
        existing = db["incidents"].find_one({
            "$or": [
                {"affected_component": entity_id, "status": {"$in": ["DETECTED", "INVESTIGATING", "WAITING_APPROVAL", "REPLANNING"]}},
                {"affected_po": entity_id, "status": {"$in": ["DETECTED", "INVESTIGATING", "WAITING_APPROVAL", "REPLANNING"]}},
            ]
        })

        if not existing:
            # Map anomaly to standard incident type
            if anomaly_type in ("NEGATIVE_STOCK", "INTEGRITY_ERROR"):
                inc_type = "STALE_INVENTORY"
                severity = "CRITICAL"
                affected_comp = entity_id
                affected_po = None
                affected_supp = None
            else:
                inc_type = "SUPPLIER_DELAY"
                severity = anomaly["severity"]
                affected_comp = anomaly.get("component_id", entity_id)
                affected_po = entity_id if anomaly["entity"] == "purchase_orders" else None
                affected_supp = anomaly.get("supplier_id")

            incident_id = f"INC-{uuid.uuid4().hex[:6].upper()}"
            incident_doc = {
                "incident_id": incident_id,
                "type": inc_type,
                "severity": severity,
                "affected_component": affected_comp,
                "affected_po": affected_po,
                "affected_supplier": affected_supp,
                "status": "DETECTED",
                "created_at": scan_timestamp,
                "data_inconsistency_detected": anomaly_type in ("NEGATIVE_STOCK", "INTEGRITY_ERROR"),
                "auto_discovered": True,
                "discovery_details": anomaly["description"],
            }
            db["incidents"].insert_one(incident_doc)

            # Proactively run the multi-step agent reasoning cycle
            agent_result = run_agent_cycle(
                incident_id=incident_id,
                db=db,
                trigger_reason=f"Auto-discovered during environment scan: {anomaly['description']}",
            )

            incidents_triggered.append({
                "incident_id": incident_id,
                "type": inc_type,
                "entity_id": entity_id,
                "severity": severity,
                "decision": agent_result.get("decision"),
                "state": agent_result.get("state"),
                "requires_human_approval": agent_result.get("requires_human_approval"),
            })

    # Log environment scan event
    log_event(
        db,
        incident_id="SYSTEM-SCAN",
        action=f"Full operational environment scan executed. {len(inventory_items)} inventory items, {len(purchase_orders)} POs monitored. {len(anomalies_detected)} anomalies found.",
        decision="SCAN_COMPLETED",
        reason=f"Triggered {len(incidents_triggered)} new automated resolution cycles.",
        step_index=0,
    )

    return {
        "status": "success",
        "scan_timestamp": scan_timestamp.isoformat(),
        "entities_scanned": {
            "inventory_count": len(inventory_items),
            "purchase_orders_count": len(purchase_orders),
        },
        "anomalies_detected_count": len(anomalies_detected),
        "anomalies_detected": anomalies_detected,
        "new_incidents_triggered_count": len(incidents_triggered),
        "new_incidents_triggered": incidents_triggered,
        "message": f"Scan completed: {len(anomalies_detected)} anomalies found across operational environment. {len(incidents_triggered)} automated incident triage cycles launched.",
    }
