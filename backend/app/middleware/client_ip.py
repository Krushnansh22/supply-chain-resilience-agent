"""
app/middleware/client_ip.py
Owner: Developer 2 (Backend / Simulation)

Resolves client IP securely, honoring X-Forwarded-For ONLY when the direct peer
is in the configured TRUSTED_PROXY_IPS list.
"""

from fastapi import Request
from app.config import settings


def get_trusted_client_ip(request: Request) -> str:
    """
    Extract client IP safely.
    Only trusts X-Forwarded-For if request.client.host is explicitly in settings.trusted_proxy_ip_list.
    Otherwise, always returns request.client.host directly to prevent IP spoofing / rate-limit bypass.
    """
    client_host = request.client.host if request.client else "unknown"
    trusted_proxies = settings.trusted_proxy_ip_list

    if trusted_proxies and client_host in trusted_proxies:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # X-Forwarded-For may contain a comma-separated list of IPs: client, proxy1, proxy2...
            return forwarded.split(",")[0].strip()

    return client_host
