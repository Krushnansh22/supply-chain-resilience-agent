"""
app/middleware/security.py
Owner: Developer 2 (Backend / Simulation)

Security middleware components:
  1. SecurityHeadersMiddleware — injects defensive HTTP response headers on every response.
  2. api_key_dependency        — optional FastAPI Depends() that enforces X-API-Key on
                                  mutating endpoints when API_KEY is set in config.

IMPORTANT: None of this changes business logic, DB models, or existing route behavior.
"""

from fastapi import Request, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.config import settings

# ---------------------------------------------------------------------------
# 1. HTTP Security Headers Middleware
# ---------------------------------------------------------------------------

SECURITY_HEADERS = {
    # Prevent browsers from MIME-sniffing a response away from the declared content-type.
    "X-Content-Type-Options": "nosniff",
    # Block the page from being displayed inside a frame (prevents clickjacking).
    "X-Frame-Options": "DENY",
    # Legacy XSS filter for older browsers.
    "X-XSS-Protection": "1; mode=block",
    # Control how much referrer information is sent.
    "Referrer-Policy": "strict-origin-when-cross-origin",
    # Restrict access to browser features (camera, mic, geolocation).
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    # Remove the X-Powered-By style server fingerprint (FastAPI doesn't add it by default,
    # but some reverse proxies do — explicitly nuke it).
    "Server": "scda",
}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Injects defensive security headers into every HTTP response."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        for header, value in SECURITY_HEADERS.items():
            response.headers[header] = value
        return response


# ---------------------------------------------------------------------------
# 2. Optional API Key Dependency
# ---------------------------------------------------------------------------

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def require_api_key(api_key: str = Security(_api_key_header)) -> None:
    """
    FastAPI dependency for optional API key enforcement.

    - If settings.API_KEY is empty (default), this is a no-op — open access.
    - If settings.API_KEY is set, the caller MUST provide a matching X-API-Key header.

    Usage on a router:
        router = APIRouter(dependencies=[Depends(require_api_key)])

    Usage on a single endpoint:
        @router.post("/inject")
        def inject(req: InjectRequest, _: None = Depends(require_api_key)):
            ...
    """
    if not settings.API_KEY:
        # API_KEY not configured → open access (local dev / hackathon demo mode)
        return

    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key. Provide a valid X-API-Key header.",
        )
