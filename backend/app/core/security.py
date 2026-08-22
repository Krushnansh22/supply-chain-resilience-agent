"""
app/core/security.py

Reusable FastAPI security dependencies.

DESIGN NOTES:
  - Uses `secrets.compare_digest` for constant-time comparison to prevent
    timing-oracle attacks on the API key.
  - Mirrors the existing pattern in `routes_integrations.py::verify_api_key`
    but lives in `app/core/` so it can be imported by any router without
    creating a circular import with `routes_integrations`.
  - The dependency raises HTTP 401 (not 403) — the caller is unauthenticated,
    not unauthorized. This matches RFC 7235 semantics.

USAGE:
    from app.core.security import require_api_key

    @router.get("/some-endpoint")
    def my_endpoint(_auth=Depends(require_api_key)):
        ...
"""

import secrets
from fastapi import Depends, Header, HTTPException

from app.config import settings


def require_api_key(x_api_key: str = Header(default="")) -> None:
    """
    FastAPI dependency: validates the `X-API-Key` request header against
    `settings.BACKEND_API_KEY` using constant-time comparison.

    Raises:
        HTTPException 401 — if the key is missing or does not match.

    Security:
        `secrets.compare_digest` prevents timing side-channels that could
        be exploited to enumerate valid key characters.
    """
    expected: str = settings.BACKEND_API_KEY
    if not expected:
        # Safety valve: if BACKEND_API_KEY is not configured, deny all requests
        # rather than accidentally exposing the endpoint wide open.
        raise HTTPException(
            status_code=500,
            detail="Server configuration error: BACKEND_API_KEY is not set.",
        )

    if not x_api_key or not secrets.compare_digest(x_api_key, expected):
        raise HTTPException(status_code=401, detail="Invalid API Key")
