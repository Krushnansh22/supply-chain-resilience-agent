"""
app/middleware/security.py
Owner: Developer 2 (Backend / Simulation)

Security middleware components:
  1. SecurityHeadersMiddleware — injects defensive HTTP response headers on every response.
  2. SecurityEventLoggerMiddleware — logs all 4xx/5xx responses with IP + path for monitoring.
  3. require_api_key — optional FastAPI Depends() enforcing X-API-Key on mutating endpoints.

IMPORTANT: None of this changes business logic, DB models, or existing route behavior.
"""

import logging
from fastapi import Request, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.config import settings

logger = logging.getLogger("security")

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
    # Remove server fingerprint (replace default with opaque name).
    "Server": "scda",
    # Content Security Policy — restricts what sources the browser will load.
    # 'self' + localhost for API + Vite dev server. Adjust for production domain.
    "Content-Security-Policy": (
        "default-src 'self'; "
        "connect-src 'self' http://localhost:8000 http://localhost:5173; "
        "script-src 'self' 'unsafe-inline'; "   # Swagger UI needs unsafe-inline
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "frame-ancestors 'none';"
    ),
    # HTTP Strict Transport Security — forces HTTPS in production.
    # max-age=31536000 = 1 year. includeSubDomains is intentionally omitted for local dev safety.
    "Strict-Transport-Security": "max-age=31536000",
    # Prevent browser from sending data cross-origin.
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Resource-Policy": "same-site",
}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Injects comprehensive defensive security headers into every HTTP response."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        for header, value in SECURITY_HEADERS.items():
            response.headers[header] = value
        return response


# ---------------------------------------------------------------------------
# 2. Security Event Logger Middleware
# ---------------------------------------------------------------------------

class SecurityEventLoggerMiddleware(BaseHTTPMiddleware):
    """
    Logs every HTTP 4xx and 5xx response with IP, method, path, and status code.
    Provides a basic audit trail for detecting abuse, scanning, and auth failures.
    Does NOT log request bodies or query params to avoid leaking sensitive data.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        if response.status_code >= 400:
            ip = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
            if not ip:
                ip = request.client.host if request.client else "unknown"

            level = logging.WARNING if response.status_code < 500 else logging.ERROR
            logger.log(
                level,
                "SECURITY_EVENT | status=%d | method=%s | path=%s | ip=%s",
                response.status_code,
                request.method,
                request.url.path,
                ip,
            )

        return response


# ---------------------------------------------------------------------------
# 3. Request Body Size Limiter
# ---------------------------------------------------------------------------

class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """
    Rejects requests with a body larger than max_bytes (default: 64 KB).
    Prevents large-payload DoS attacks without needing a reverse proxy.
    """

    def __init__(self, app, max_bytes: int = 65_536):
        super().__init__(app)
        self.max_bytes = max_bytes

    async def dispatch(self, request: Request, call_next) -> Response:
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_bytes:
            from fastapi.responses import JSONResponse
            logger.warning(
                "SECURITY_EVENT | OVERSIZED_REQUEST | content-length=%s | ip=%s | path=%s",
                content_length,
                request.client.host if request.client else "unknown",
                request.url.path,
            )
            return JSONResponse(
                status_code=413,
                content={"detail": f"Request body too large. Maximum allowed: {self.max_bytes} bytes."},
            )
        return await call_next(request)


# ---------------------------------------------------------------------------
# 4. Optional API Key Dependency
# ---------------------------------------------------------------------------

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def require_api_key(api_key: str = Security(_api_key_header)) -> None:
    """
    FastAPI dependency for optional API key enforcement on mutating endpoints.

    - If settings.API_KEY is empty (default): open access — safe for local dev/demo.
    - If settings.API_KEY is set in .env: all mutating endpoints require matching X-API-Key.

    Usage:
        from app.middleware.security import require_api_key
        @router.post("/inject", dependencies=[Depends(require_api_key)])
    """
    if not settings.API_KEY:
        return  # Open mode — API_KEY not configured

    if not api_key or api_key != settings.API_KEY:
        logger.warning("SECURITY_EVENT | INVALID_API_KEY | provided=%s", bool(api_key))
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key. Provide a valid X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
