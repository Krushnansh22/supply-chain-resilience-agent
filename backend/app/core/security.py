"""
app/core/security.py
Reusable security, API key validation, password hashing, and token helpers.
"""

import secrets
import hashlib
import hmac
import json
import base64
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from fastapi import Header, HTTPException

from app.config import settings


def require_api_key(x_api_key: str = Header(default="")) -> None:
    """Validates the X-API-Key request header against settings.BACKEND_API_KEY."""
    expected: str = settings.BACKEND_API_KEY
    if not expected:
        raise HTTPException(
            status_code=500,
            detail="Server configuration error: BACKEND_API_KEY is not set.",
        )
    if not x_api_key or not secrets.compare_digest(x_api_key, expected):
        raise HTTPException(status_code=401, detail="Invalid API Key")


def hash_password(password: str) -> str:
    """Hashes password with SHA256 + salt using PBKDF2."""
    salt = "atlas_salt_2026"
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000).hex()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against the stored hash."""
    return hmac.compare_digest(hash_password(plain_password), hashed_password)


def create_jwt_token(payload: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Generates an HMAC-SHA256 signed JWT token."""
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.JWT_EXPIRE_MINUTES))
    data = {**payload, "exp": expire.timestamp()}
    
    header_b64 = base64.urlsafe_b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).decode().rstrip("=")
    payload_b64 = base64.urlsafe_b64encode(json.dumps(data).encode()).decode().rstrip("=")
    
    signing_input = f"{header_b64}.{payload_b64}".encode()
    signature = hmac.new(settings.JWT_SECRET.encode(), signing_input, hashlib.sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    
    return f"{header_b64}.{payload_b64}.{sig_b64}"


def decode_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """Validates and decodes an HMAC-SHA256 signed JWT token."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header_b64, payload_b64, sig_b64 = parts
        
        # Verify signature
        signing_input = f"{header_b64}.{payload_b64}".encode()
        expected_sig = hmac.new(settings.JWT_SECRET.encode(), signing_input, hashlib.sha256).digest()
        
        # Pad base64 if needed
        sig_padded = sig_b64 + "=" * (-len(sig_b64) % 4)
        received_sig = base64.urlsafe_b64decode(sig_padded)
        
        if not hmac.compare_digest(expected_sig, received_sig):
            return None
        
        payload_padded = payload_b64 + "=" * (-len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_padded).decode())
        
        if "exp" in payload and payload["exp"] < datetime.now(timezone.utc).timestamp():
            return None  # Expired
            
        return payload
    except Exception:
        return None
