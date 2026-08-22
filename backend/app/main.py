"""
app/main.py
Owner: Developer 2 (Backend / Simulation)

FastAPI application entrypoint. Mounts every router from app/api/*, enables CORS
for the React frontend, and initializes the SQLite DB + seed data on startup.

RECEIVES: nothing (this is the process entrypoint)
DELIVERS: the running HTTP API that Dev4's frontend and Dev1's agent both talk to.
  - Swagger UI at /docs is the fastest way for all 4 devs to sanity-check the API
    contract in docs/API_CONTRACTS.md without waiting on the frontend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.mongo_database import get_mongo_db
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
