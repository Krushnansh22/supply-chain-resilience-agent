"""
app/main.py
Owner: Developer 2 (Backend / Simulation)

FastAPI application entrypoint. Mounts every router from app/api/*, enables CORS
for the React frontend, and initializes the SQLite DB + seed data on startup.

RECEIVES: nothing (this is the process entrypoint)
DELIVERS: the running HTTP API that Dev4's frontend and Dev1's agent both talk to.
  - Swagger UI at /docs is the fastest way for all 4 devs to sanity-check the API
    contract in docs/API_CONTRACTS.md without waiting on the frontend.

SECURITY ADDITIONS (non-breaking):
  - SecurityHeadersMiddleware: injects X-Content-Type-Options, X-Frame-Options, etc.
  - Global 500 handler: shields internal error details from API clients.
  - CORS: restricted to configured allowed methods (GET, POST, OPTIONS by default).
"""

import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db
from app.middleware.security import SecurityHeadersMiddleware

from app.api import (
    routes_inventory,
    routes_suppliers,
    routes_production,
    routes_incidents,
    routes_audit,
    routes_agent,
    routes_simulator,
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Supply Chain Disruption Control Agent",
    description="Autonomous incident triage & multi-modal re-routing engine (HOP 2026)",
    version="0.1.0",
)

# ── Security headers on every response ──────────────────────────────────────
app.add_middleware(SecurityHeadersMiddleware)

# ── CORS: restricted to known origins and explicit HTTP methods ──────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=settings.cors_allowed_methods_list,   # GET, POST, OPTIONS (from config)
    allow_headers=["Content-Type", "Accept", "X-API-Key"],
)


# ── Global exception handler: never leak raw tracebacks to clients ───────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Catches any unhandled exception and returns a safe, opaque 500 response.
    Full details are logged server-side only — nothing leaks to the API client.
    """
    logger.exception("Unhandled server error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again later."},
    )


@app.on_event("startup")
def on_startup():
    init_db()


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
