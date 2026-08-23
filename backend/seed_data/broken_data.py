"""
backend/seed_data/broken_data.py
Owner: Developer 2 (Backend / Simulation)

Contains inconsistent, erroneous, anomalous, and edge-case data for testing:
  - LLM inconsistency detection
  - Error handling workflow paths
  - Retry logic
  - Validation failures
  - Data integrity monitoring

All collections seeded here are intentionally broken for workflow testing.
"""

from datetime import datetime, timedelta, timezone
from pymongo.database import Database

NOW = datetime.now(timezone.utc)


BROKEN_SCENARIOS = {
    "inventory",
    "suppliers",
    "purchase_orders",
    "production_orders",
    "audit_logs",
    "integration_errors",
    "all",
}


def inject_broken_data(db: Database, scenario: str = "all") -> None:
    """Injects broken/inconsistent data into the database for testing all error paths."""
    if scenario not in BROKEN_SCENARIOS:
        raise ValueError(f"Unknown broken-data scenario: {scenario}")

    # ------------------------------------------------------------------
    # INVENTORY anomalies
    # ------------------------------------------------------------------
    inventory_broken = [
        # Negative stock — impossible in reality, LLM should flag
        {
            "component_id": "CMP-BRK-001",
            "name": "Corrupted Component Alpha",
            "current_stock": -50,
            "usable_stock": -50,
            "daily_usage": 10.0,
            "safety_stock": 100,
            "days_of_supply": None,
            "location": "Warehouse-ERR",
            "anomaly": "NEGATIVE_STOCK",
            "last_updated": (NOW - timedelta(days=30)).isoformat(),
        },
        # Stock exists but zero daily usage and no production orders — orphaned
        {
            "component_id": "CMP-BRK-002",
            "name": "Orphaned Component Beta",
            "current_stock": 999,
            "usable_stock": 999,
            "daily_usage": 0.0,
            "safety_stock": 0,
            "days_of_supply": None,
            "location": "Warehouse-Dallas-TX",
            "anomaly": "ORPHANED_STOCK",
            "last_updated": (NOW - timedelta(days=180)).isoformat(),
        },
        # Usable stock higher than current stock — data integrity error
        {
            "component_id": "CMP-BRK-003",
            "name": "Integrity Error Component",
            "current_stock": 100,
            "usable_stock": 150,  # usable > current — impossible
            "daily_usage": 20.0,
            "safety_stock": 50,
            "days_of_supply": 5,
            "location": "Warehouse-Frankfurt-DE",
            "anomaly": "USABLE_EXCEEDS_CURRENT",
            "last_updated": NOW.isoformat(),
        },
    ]
    if scenario in {"inventory", "all"}:
        for item in inventory_broken:
            db["inventory"].update_one(
                {"component_id": item["component_id"]},
                {"$set": item},
                upsert=True,
            )

    # ------------------------------------------------------------------
    # SUPPLIER anomalies
    # ------------------------------------------------------------------
    supplier_broken = [
        # Missing contact — cannot send RFQ
        {
            "supplier_id": "SUP-BRK-001",
            "name": "Ghost Technologies Ltd",
            "contact_email": None,
            "quality_score": 85,
            "reliability_score": 80,
            "certifications": "ISO9001",
            "status": "ACTIVE",
            "anomaly": "MISSING_CONTACT",
        },
        # Blacklisted but still on an open PO — conflict
        {
            "supplier_id": "SUP-BRK-002",
            "name": "Rogue Electronics",
            "contact_email": "badactor@rogue-elec.com",
            "quality_score": 30,
            "reliability_score": 20,
            "certifications": "",
            "status": "BLACKLISTED",
            "anomaly": "BLACKLISTED_WITH_OPEN_PO",
        },
    ]
    if scenario in {"suppliers", "all"}:
        for s in supplier_broken:
            db["suppliers"].update_one(
                {"supplier_id": s["supplier_id"]},
                {"$set": s},
                upsert=True,
            )

    # ------------------------------------------------------------------
    # PURCHASE ORDER anomalies
    # ------------------------------------------------------------------
    po_broken = [
        # Open PO referencing blacklisted supplier
        {
            "po_id": "PO-BRK-001",
            "component_id": "CMP-004",
            "supplier_id": "SUP-BRK-002",  # blacklisted!
            "quantity": 200,
            "unit_price": 90.0,
            "total_value": 18000.0,
            "status": "OPEN",
            "promised_delivery": (NOW + timedelta(days=5)).isoformat(),
            "current_expected_delivery": (NOW + timedelta(days=5)).isoformat(),
            "delay_days": 0,
            "anomaly": "OPEN_PO_BLACKLISTED_SUPPLIER",
        },
        # PO with zero quantity — invalid
        {
            "po_id": "PO-BRK-002",
            "component_id": "CMP-002",
            "supplier_id": "SUP-002",
            "quantity": 0,
            "unit_price": 0.8,
            "total_value": 0.0,
            "status": "OPEN",
            "promised_delivery": (NOW + timedelta(days=10)).isoformat(),
            "current_expected_delivery": (NOW + timedelta(days=10)).isoformat(),
            "delay_days": 0,
            "anomaly": "ZERO_QUANTITY",
        },
        # PO with no delivery date — monitoring impossible
        {
            "po_id": "PO-BRK-003",
            "component_id": "CMP-003",
            "supplier_id": "SUP-008",
            "quantity": 500,
            "unit_price": 12.0,
            "total_value": 6000.0,
            "status": "ORDERED",
            "promised_delivery": None,  # missing!
            "current_expected_delivery": None,
            "delay_days": 0,
            "anomaly": "MISSING_DELIVERY_DATE",
        },
        # Duplicate PO (same component/supplier/qty — possible duplicate entry)
        {
            "po_id": "PO-BRK-004",
            "component_id": "CMP-004",
            "supplier_id": "SUP-001",
            "quantity": 600,          # same as PO-001
            "unit_price": 140.0,
            "total_value": 84000.0,
            "status": "OPEN",
            "promised_delivery": (NOW + timedelta(days=14)).isoformat(),
            "current_expected_delivery": (NOW + timedelta(days=14)).isoformat(),
            "delay_days": 0,
            "anomaly": "POSSIBLE_DUPLICATE",
            "notes": "Potential duplicate of PO-001 — same supplier, component, quantity",
        },
    ]
    if scenario in {"purchase_orders", "all"}:
        for po in po_broken:
            db["purchase_orders"].update_one(
                {"po_id": po["po_id"]},
                {"$set": po},
                upsert=True,
            )

    # ------------------------------------------------------------------
    # PRODUCTION ORDER anomalies
    # ------------------------------------------------------------------
    prod_broken = [
        # References non-existent component
        {
            "production_id": "WO-BRK-001",
            "product": "Ghost Product",
            "component_id": "CMP-GHOST",  # does not exist
            "quantity": 100,
            "component_per_unit": 2,
            "components_needed": 200,
            "deadline": (NOW + timedelta(days=10)).isoformat(),
            "priority": "MEDIUM",
            "status": "ON_TRACK",
            "anomaly": "NONEXISTENT_COMPONENT",
        },
        # Already past deadline but status still ON_TRACK
        {
            "production_id": "WO-BRK-002",
            "product": "Overdue Unit",
            "component_id": "CMP-001",
            "quantity": 50,
            "component_per_unit": 1,
            "components_needed": 50,
            "deadline": (NOW - timedelta(days=5)).isoformat(),  # past!
            "priority": "HIGH",
            "status": "ON_TRACK",  # should be OVERDUE — data inconsistency
            "anomaly": "PAST_DEADLINE_NOT_OVERDUE",
        },
    ]
    if scenario in {"production_orders", "all"}:
        for p in prod_broken:
            db["production_orders"].update_one(
                {"production_id": p["production_id"]},
                {"$set": p},
                upsert=True,
            )

    # ------------------------------------------------------------------
    # AUDIT LOG anomalies — for error path testing
    # ------------------------------------------------------------------
    audit_broken = [
        # Audit log with no incident_id — orphaned
        {
            "event_id": "AUD-BRK-001",
            "timestamp": (NOW - timedelta(hours=6)).isoformat(),
            "source": "n8n",
            "workflow": "ERP_EVENT_SYNC",
            "event_type": "WORKFLOW_FAILED",
            "incident_id": None,
            "entity_type": "ERP_EVENT",
            "entity_id": "ERP-UNKNOWN",
            "action": "VALIDATE_ERP_EVENT",
            "status": "FAILURE",
            "tool": "VALIDATE_ERP_EVENT",
            "result": "FAILURE",
            "decision": "WORKFLOW_FAILED",
            "reason": "Missing required fields: po_id, supplier_id",
            "retry_count": 3,
            "error_details": "ValidationError: field 'po_id' is required",
            "anomaly": "FAILED_WITH_MAX_RETRIES",
            "ingested_at": (NOW - timedelta(hours=6)).isoformat(),
        },
        # Audit log with duplicate event_id — should not happen
        {
            "event_id": "AUD-DUP-001",
            "timestamp": NOW.isoformat(),
            "source": "n8n",
            "workflow": "DELIVERY_COMMITMENT_MONITOR",
            "event_type": "DELIVERY_COMMITMENT_BREACH",
            "incident_id": "INC-001",
            "entity_type": "PURCHASE_ORDER",
            "entity_id": "PO-001",
            "action": "TRIGGER_AI_AGENT",
            "status": "SUCCESS",
            "tool": "TRIGGER_AI_AGENT",
            "result": "SUCCESS",
            "decision": "DELIVERY_COMMITMENT_BREACH",
            "reason": "Duplicate event — idempotency check missed",
            "retry_count": 0,
            "anomaly": "DUPLICATE_EVENT",
            "ingested_at": NOW.isoformat(),
        },
    ]
    if scenario in {"audit_logs", "all"}:
        for log in audit_broken:
            db["audit_logs"].update_one(
                {"event_id": log["event_id"]},
                {"$set": log},
                upsert=True,
            )

    # ------------------------------------------------------------------
    # INTEGRATION ERROR RECORDS — for retry/error testing
    # ------------------------------------------------------------------
    integration_errors = [
        {
            "error_id": "ERR-001",
            "timestamp": (NOW - timedelta(hours=2)).isoformat(),
            "workflow": "ERP_EVENT_SYNC",
            "node": "POST /integrations/erp/event",
            "error_type": "HTTP_5XX",
            "error_message": "503 Service Unavailable — backend not responding",
            "payload": {"po_id": "PO-001", "status": "DELAYED"},
            "retry_count": 2,
            "max_retries": 4,
            "retryable": True,
            "resolved": True,
            "resolved_at": (NOW - timedelta(hours=1, minutes=55)).isoformat(),
        },
        {
            "error_id": "ERR-002",
            "timestamp": (NOW - timedelta(hours=1)).isoformat(),
            "workflow": "SUPPLIER_RESPONSE_SYNC",
            "node": "Validate Supplier Response",
            "error_type": "VALIDATION_FAILURE",
            "error_message": "Missing required fields: rfq_id, quantity_available",
            "payload": {"supplier_id": "SUP-007", "component_id": "CMP-006"},
            "retry_count": 0,
            "max_retries": 0,
            "retryable": False,
            "resolved": False,
            "escalated": True,
            "escalated_at": NOW.isoformat(),
        },
        {
            "error_id": "ERR-003",
            "timestamp": (NOW - timedelta(minutes=15)).isoformat(),
            "workflow": "AI_AGENT",
            "node": "Groq LLM — LLaMA-3.3-70B",
            "error_type": "LLM_TIMEOUT",
            "error_message": "Groq API timeout after 30s",
            "payload": {"incident_id": "INC-002"},
            "retry_count": 1,
            "max_retries": 2,
            "retryable": True,
            "resolved": False,
        },
    ]
    if scenario in {"integration_errors", "all"}:
        for err in integration_errors:
            db["integration_errors"].update_one(
                {"error_id": err["error_id"]},
                {"$set": err},
                upsert=True,
            )

    print(f"✅ Broken-data scenario injected: {scenario}")