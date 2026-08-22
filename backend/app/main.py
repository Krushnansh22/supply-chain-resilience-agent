"""
app/main.py
Owner: Developer 2 (Backend / Simulation)

FastAPI application entrypoint. Mounts every router from app/api/*, enables CORS
for the React frontend, and initializes the SQLite DB + seed data on startup.

RECEIVES: nothing (this is the process entrypoint)
DELIVERS: the running HTTP API that Dev4's frontend and Dev1's agent both talk to.

SECURITY LAYERS (all non-breaking):
  Layer 1 — RequestSizeLimitMiddleware : reject bodies > 64 KB (header + streaming check)
  Layer 2 — GeneralRateLimitMiddleware : global sliding-window rate limit (60/60s, /health exempt)
  Layer 3 — SecurityHeadersMiddleware  : X-Frame-Options, CSP, HSTS, etc. on all responses
  Layer 4 — SecurityEventLoggerMiddleware : log all 4xx/5xx events with IP for monitoring
  Layer 5 — CORSMiddleware             : restricted origins, methods, and headers
  Layer 6 — Global 500 handler         : never leak raw tracebacks to API clients
  Layer 7 — Custom 422 handler         : sanitize validation error output
  Layer 8 — Path param regex           : per-route, blocks injection/traversal (see routes_*)
  Layer 9 — API Key dependency         : opt-in via settings.API_KEY on mutating endpoints
"""

import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.config import settings
from app.database import init_db
from app.middleware.security import (
    SecurityHeadersMiddleware,
    SecurityEventLoggerMiddleware,
    RequestSizeLimitMiddleware,
)
from app.middleware.general_rate_limiter import GeneralRateLimitMiddleware

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
    docs_url="/docs" if settings.DOCS_ENABLED else None,
    redoc_url="/redoc" if settings.DOCS_ENABLED else None,
    openapi_url="/openapi.json" if settings.DOCS_ENABLED else None,
)

# ── Layer 1: Request body size limit (64 KB, stream counting + header check) ─
app.add_middleware(RequestSizeLimitMiddleware, max_bytes=65_536)

# ── Layer 2: Global general rate limiter (60 req/60s across all routes, /health exempt) ──
app.add_middleware(GeneralRateLimitMiddleware)

# ── Layer 3: Security headers on every response ──────────────────────────────
app.add_middleware(SecurityHeadersMiddleware)

# ── Layer 4: Security event logger (4xx / 5xx monitoring) ────────────────────
app.add_middleware(SecurityEventLoggerMiddleware)

# ── Layer 5: CORS — restricted to known origins and explicit HTTP methods ─────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=settings.cors_allowed_methods_list,   # GET, POST, OPTIONS
    allow_headers=["Content-Type", "Accept", "X-API-Key"],
)


# ── Layer 6: Global 500 handler — never leak tracebacks ──────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled server error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again later."},
    )


# ── Layer 7: Custom 422 handler — sanitize validation errors ──────────────────
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Return safe, simplified validation errors.
    Strips internal field paths and Python type names that could fingerprint the backend.
    """
    safe_errors = []
    for error in exc.errors():
        safe_errors.append({
            "field": " -> ".join(str(loc) for loc in error.get("loc", [])),
            "issue": error.get("msg", "Invalid value"),
        })
    return JSONResponse(
        status_code=422,
        content={"detail": "Request validation failed.", "errors": safe_errors},
    )


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health():
    """Simple liveness check. Does not expose version or internal state."""
    return {"status": "ok", "service": "supply-chain-disruption-control-agent"}


# --- Mount all routers. Prefixes MUST match docs/API_CONTRACTS.md exactly. ---
app.include_router(routes_inventory.router, prefix="/inventory", tags=["Inventory"])
app.include_router(routes_suppliers.router, prefix="/suppliers", tags=["Suppliers"])
app.include_router(routes_production.router, prefix="/production", tags=["Production"])
app.include_router(routes_incidents.router, prefix="/incidents", tags=["Incidents"])
app.include_router(routes_audit.router, prefix="/audit", tags=["Audit"])
app.include_router(routes_agent.router, prefix="/agent", tags=["Agent"])
app.include_router(routes_simulator.router, prefix="/simulator", tags=["Simulator"])
