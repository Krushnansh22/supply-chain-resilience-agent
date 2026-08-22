"""
Comprehensive verification test for the Supply Chain Resilience Agent Backend.
Tests all REST endpoints, all 5 scenarios, all Python tools, and all decision engine modules.
Supports direct execution via FastAPI TestClient (self-contained, no external process needed).
"""
import sys
sys.path.insert(0, '.')

from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal, init_db
from app.decision_engine.inventory_calc import compute_days_of_supply, is_below_safety_stock
from app.decision_engine.production_risk import assess_production_risk
from app.decision_engine.supplier_scoring import score_supplier
from app.decision_engine.recovery_planner import build_recovery_plan
from app.tools.inventory_tools import get_inventory
from app.tools.supplier_tools import get_supplier, send_supplier_message, get_tracking_status
from app.tools.rfq_tools import request_rfq
from app.tools.approval_tools import check_approval

# Initialize database and seed data
init_db()
client = TestClient(app)

results = []

def chk(name, ok, detail=""):
    results.append((name, ok))
    print(f"{'PASS' if ok else 'FAIL'} | {name} | {detail}")

print("=" * 60)
print("1. REST API ENDPOINTS")
print("=" * 60)

r = client.get("/health")
chk("GET /health", r.status_code == 200 and r.json().get("status") == "ok", r.json().get("status"))

r = client.get("/inventory/")
chk("GET /inventory/ (>=20 items)", r.status_code == 200 and len(r.json()) >= 20, f"{len(r.json())} items")

# Get actual current stock (don't hardcode expected value)
r = client.get("/inventory/COMP-104")
h = r.json()
chk("GET /inventory/COMP-104", r.status_code == 200 and h.get("days_of_supply") is not None, f"days_of_supply={h.get('days_of_supply')}")

# Adjust inventory +50, verify increase, then reset
old_stock = h.get("usable_stock", 0)
r_adj = client.post("/inventory/COMP-104/adjust", json={"delta": 50, "reason": "test"})
chk("POST /inventory/COMP-104/adjust (+50)", r_adj.status_code == 200 and r_adj.json().get("usable_stock") == old_stock + 50, f"stock {old_stock} -> {r_adj.json().get('usable_stock')}")
client.post("/inventory/COMP-104/adjust", json={"delta": -50, "reason": "reset"})

# Negative guard
r_neg = client.post("/inventory/COMP-104/adjust", json={"delta": -999999, "reason": "bad"})
chk("Negative stock guard (expect 422)", r_neg.status_code == 422, f"HTTP {r_neg.status_code}")

# 404 on missing component
r_404 = client.get("/inventory/COMP-FAKE")
chk("GET /inventory/COMP-FAKE (expect 404)", r_404.status_code == 404, f"HTTP {r_404.status_code}")

r = client.get("/suppliers/")
chk("GET /suppliers/ (>=10)", r.status_code == 200 and len(r.json()) >= 10, f"{len(r.json())} suppliers")

r = client.get("/suppliers/SUP-21")
chk("GET /suppliers/SUP-21", r.status_code == 200 and r.json().get("name") == "Alpha Components Pvt Ltd", r.json().get("name"))

r = client.get("/suppliers/SUP-21/messages")
chk("GET /suppliers/SUP-21/messages", r.status_code == 200, f"{len(r.json())} messages")

r = client.get("/suppliers/SUP-FAKE")
chk("GET /suppliers/SUP-FAKE (expect 404)", r.status_code == 404, f"HTTP {r.status_code}")

r = client.get("/production/")
chk("GET /production/ (>=8)", r.status_code == 200 and len(r.json()) >= 8, f"{len(r.json())} orders")

r = client.get("/production/PROD-882")
chk("GET /production/PROD-882 (Widget-X)", r.status_code == 200 and r.json().get("product") == "Widget-X", r.json().get("product"))

r = client.get("/audit/")
chk("GET /audit/", r.status_code == 200, f"{len(r.json())} entries")

print()
print("=" * 60)
print("2. SIMULATOR INJECTIONS (ALL 5 SCENARIOS)")
print("=" * 60)

injected_ids = []
for sc in ["SUPPLIER_DELAY", "STALE_INVENTORY", "SUPPLIER_LIE", "QUALITY_FAILURE", "BUDGET_OVERRUN"]:
    r = client.post("/simulator/inject", json={"scenario": sc})
    d = r.json()
    ok = r.status_code == 200 and d.get("type") == sc and d.get("status") == "DETECTED"
    if ok:
        injected_ids.append(d["incident_id"])
    chk(f"Inject: {sc}", ok, f"id={d.get('incident_id')} status={d.get('status')}")

r = client.post("/simulator/inject", json={"scenario": "INVALID_SCENARIO"})
chk("Inject INVALID (expect 422)", r.status_code == 422, f"HTTP {r.status_code}")

print()
print("=" * 60)
print("3. INCIDENTS & ACTIVITY FEED")
print("=" * 60)

r = client.get("/incidents/")
inc_list = r.json()
chk("GET /incidents/ (>=5)", r.status_code == 200 and len(inc_list) >= 5, f"{len(inc_list)} incidents")

if injected_ids:
    iid = injected_ids[0]
    r = client.get(f"/incidents/{iid}")
    chk(f"GET /incidents/{iid}", r.status_code == 200 and r.json().get("incident_id") == iid, f"type={r.json().get('type')}")

    r = client.get(f"/incidents/{iid}/activity")
    chk(f"GET /incidents/{iid}/activity", r.status_code == 200, f"{len(r.json())} entries")

    r = client.get(f"/agent/state/{iid}")
    chk(f"GET /agent/state/{iid}", r.status_code == 200 and r.json().get("state") is not None, f"state={r.json().get('state')}")

r = client.get("/incidents/INC-FAKE")
chk("GET /incidents/INC-FAKE (expect 404)", r.status_code == 404, f"HTTP {r.status_code}")

print()
print("=" * 60)
print("4. DECISION ENGINE (PYTHON MODULES)")
print("=" * 60)

dos = compute_days_of_supply(390, 90.0)
chk("compute_days_of_supply(390, 90)", dos == 4.33, f"= {dos}")

chk("compute_days_of_supply(0, 0) = inf", compute_days_of_supply(0, 0) == float("inf"), "div-by-zero guarded")

chk("is_below_safety_stock(80, 100) = True", is_below_safety_stock(80, 100) is True, "80 < 100")
chk("is_below_safety_stock(150, 100) = False", is_below_safety_stock(150, 100) is False, "150 >= 100")

risk = assess_production_risk("PROD-882", 4.33, datetime.now() + timedelta(days=10), "HIGH")
chk("assess_production_risk (high prio, tight supply)", risk.risk_level in ["HIGH", "CRITICAL"], f"risk={risk.risk_level}")

risk_safe = assess_production_risk("PROD-801", 30.0, datetime.now() + timedelta(days=5), "LOW")
chk("assess_production_risk (safe supply)", risk_safe.risk_level == "LOW", f"risk={risk_safe.risk_level}")

scored = score_supplier(supplier_id="SUP-18", quality_score=95, reliability_score=90,
                        unit_price=135.0, delivery_days=3,
                        max_acceptable_delivery_days=10, max_acceptable_price=200.0)
chk("score_supplier (high quality)", scored.score > 0.5, f"score={scored.score}")

plan = build_recovery_plan(
    incident_id="INC-VTEST",
    required_quantity=600,
    rfq_candidates=[
        {"supplier_id": "SUP-18", "unit_price": 135.0, "delivery_days": 3, "certifications": "ISO9001,RoHS"},
        {"supplier_id": "SUP-42", "unit_price": 125.0, "delivery_days": 6, "certifications": "RoHS"},
    ],
    required_cert="ISO9001",
    required_by_days=5,
)
chk("build_recovery_plan (2 options)", len(plan.options) == 2, f"recommended={plan.recommended_option_id}")
chk("build_recovery_plan recommended ISO9001", plan.recommended_option_id == "A", f"SUP-18 passes ISO9001, SUP-42 fails")

print()
print("=" * 60)
print("5. AGENT TOOLS (PYTHON LAYER)")
print("=" * 60)

db = SessionLocal()
try:
    t = get_inventory("COMP-104", db)
    chk("Tool: get_inventory COMP-104", t.success, t.summary[:70])

    t = get_inventory("COMP-FAKE", db)
    chk("Tool: get_inventory COMP-FAKE (not found)", t.success is False, t.error)

    t = get_supplier("SUP-21", db)
    chk("Tool: get_supplier SUP-21", t.success, t.summary[:70])

    t = send_supplier_message("SUP-21", "PO-7712", "Please confirm shipment status.", db)
    chk("Tool: send_supplier_message", t.success and "reply" in t.data, t.summary[:70])

    t = get_tracking_status("PO-7712", db)
    chk("Tool: get_tracking_status PO-7712", t.success and t.data.get("tracking_status") in ["IN_TRANSIT", "OUT_FOR_DELIVERY", "NO_PICKUP_SCAN"], t.data.get("tracking_status"))

    # SUPPLIER_LIE: after injecting SUPPLIER_LIE, PO-7712 should give NO_PICKUP_SCAN
    t_lie = get_tracking_status("PO-7712", db)
    chk("SUPPLIER_LIE: tracking=NO_PICKUP_SCAN for PO-7712", t_lie.data.get("tracking_status") == "NO_PICKUP_SCAN", t_lie.data.get("tracking_status"))

    t = request_rfq("COMP-104", 600, ["SUP-18", "SUP-42", "SUP-07"], db)
    chk("Tool: request_rfq (3 suppliers)", t.success and len(t.data) == 3, t.summary[:70])

    t_low = check_approval(35000.0)
    chk("Tool: check_approval $35k (auto)", t_low.data["requires_approval"] is False, "auto-approved")

    t_high = check_approval(75000.0)
    chk("Tool: check_approval $75k (human)", t_high.data["requires_approval"] is True, "human required")

    t_exact = check_approval(50000.0)
    chk("Tool: check_approval exactly $50k (auto)", t_exact.data["requires_approval"] is False, "boundary: <= auto")
finally:
    db.close()

print()
print("=" * 60)
passed = sum(1 for _, ok in results if ok)
total = len(results)
print(f"FINAL RESULT: {passed}/{total} PASSED")
if passed == total:
    print(">>> ALL BACKEND SYSTEMS OPERATIONAL <<<")
else:
    print(f">>> {total - passed} FAILURE(S) <<<")
    for name, ok in results:
        if not ok:
            print(f"  FAILED: {name}")
print("=" * 60)
