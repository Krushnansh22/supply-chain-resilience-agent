"""
app/middleware/rate_limiter.py
Owner: Developer 2 (Backend / Simulation)

Simple in-memory sliding-window rate limiter — no external dependencies.

Default limits (configurable via config.py):
  - General endpoints:   60 requests / 60 seconds per IP
  - Mutating endpoints:  20 requests / 60 seconds per IP (inject, adjust, trigger)

On limit exceeded → HTTP 429 Too Many Requests.
"""

import time
import threading
from collections import defaultdict, deque
from fastapi import Request, HTTPException

# Thread-safe store: { (ip, bucket) -> deque of timestamps }
_store: dict = defaultdict(deque)
_lock = threading.Lock()


def _get_client_ip(request: Request) -> str:
    """
    Extract real client IP.
    Handles reverse proxies via X-Forwarded-For.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def check_rate_limit(request: Request, bucket: str = "general", max_calls: int = 60, window_seconds: int = 60) -> None:
    """
    FastAPI dependency. Raises HTTP 429 if the caller exceeds the rate limit.

    Usage:
        @router.post("/inject")
        def inject(req, _=Depends(lambda r=Request: check_rate_limit(r, "mutate", 20, 60))):
            ...
    """
    ip = _get_client_ip(request)
    key = (ip, bucket)
    now = time.monotonic()
    cutoff = now - window_seconds

    with _lock:
        dq = _store[key]
        # Remove timestamps outside the window
        while dq and dq[0] < cutoff:
            dq.popleft()

        if len(dq) >= max_calls:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Max {max_calls} requests per {window_seconds}s. Please slow down.",
                headers={"Retry-After": str(window_seconds)},
            )
        dq.append(now)
