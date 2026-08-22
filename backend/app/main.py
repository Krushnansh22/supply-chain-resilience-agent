"""
app/main.py
Owner: Developer 2 (Backend / Simulation)

FastAPI application entrypoint. Mounts every router from app/api/*, enables CORS
for the React frontend, and initializes MongoDB + seed data on startup.

NOTE: LLM logic is handled entirely in the n8n workflow (Groq AI Agent node).
This backend is a pure CRUD / data API — no LLM provider configured here.

RECEIVES: nothing (this is the process entrypoint)
DELIVERS:
  - Swagger UI at /docs — fastest API contract sanity-check for the full team
  - /integrations/* — n8n-only endpoints (ERP event, delivery breach, supplier response, audit)
  - /agent/* — agent state machine (trigger, approve, reject, state, plan)
  - /incidents, /inventory, /suppliers, /production, /audit, /simulator — frontend + agent
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.mongo_database import get_mongo_db, ping_mongo
from seed_data.seed_data import run as seed_run
from seed_data.broken_data import inject_broken_data

from app.api import (
    routes_inventory,
    routes_suppliers,
    routes_production,
    routes_incidents,
    routes_audit,
    routes_agent,
    routes_simulator,
    routes_integrations,
)

app = FastAPI(
    title="Supply Chain Disruption Control Agent",
    description="Autonomous incident triage & multi-modal re-routing engine (HOP 2026)",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    ping_mongo()
    db = get_mongo_db()
    seed_run(db)
    inject_broken_data(db)


@app.get("/health")
def health():
    """Simple liveness check used by docker-compose / judges' curl sanity check."""
    return {"status": "ok", "service": "supply-chain-disruption-control-agent"}


# --- Mount all routers. Prefixes MUST match docs/API_CONTRACTS.md exactly. ---
app.include_router(routes_inventory.router, prefix="/inventory", tags=["Inventory"])
app.include_router(routes_suppliers.router, prefix="/suppliers", tags=["Suppliers"])
app.include_router(routes_production.router, prefix="/production", tags=["Production"])
app.include_router(routes_incidents.router, prefix="/incidents", tags=["Incidents"])
app.include_router(routes_audit.router, prefix="/audit", tags=["Audit"])
app.include_router(routes_agent.router, prefix="/agent", tags=["Agent"])
app.include_router(routes_simulator.router, prefix="/simulator", tags=["Simulator"])
# --- n8n integration layer (called by n8n workflow, not frontend) ---
app.include_router(routes_integrations.router, prefix="/integrations", tags=["N8N Integrations"])
