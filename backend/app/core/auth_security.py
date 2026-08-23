"""
app/core/auth_security.py

JWT token creation/validation and password hashing for user auth.
Uses HS256 JWT (via PyJWT) and bcrypt directly (avoiding buggy passlib wrappers).

Never stores plain passwords. Tokens are short-lived; no refresh tokens
in v1 to keep the implementation simple and auditable.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
import bcrypt

from jose import JWTError, jwt
from app.config import settings

# ── Password helpers using bcrypt directly ────────────────────────────────────

def hash_password(plain: str) -> str:
    """Return bcrypt hash of the plain-text password."""
    pw_bytes = plain.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(pw_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain: str, hashed: str) -> bool:
    """Constant-time comparison of plain password against its hash."""
    try:
        pw_bytes = plain.encode('utf-8')
        hash_bytes = hashed.encode('utf-8')
        return bcrypt.checkpw(pw_bytes, hash_bytes)
    except Exception:
        return False


# ── JWT helpers ───────────────────────────────────────────────────────────────

ALGORITHM = "HS256"


def create_access_token(
    subject: str,
    role: str,
    extra: Optional[dict] = None,
    expires_minutes: Optional[int] = None,
) -> str:
    """
    Create a signed JWT access token.

    Args:
        subject:  Unique user identifier (user_id / email)
        role:     "admin" | "supplier" | "user"
        extra:    Optional additional claims
        expires_minutes: Override token TTL (defaults to settings.JWT_EXPIRE_MINUTES)

    Returns:
        Signed JWT string
    """
    if expires_minutes is None:
        expires_minutes = settings.JWT_EXPIRE_MINUTES

    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    payload = {
        "sub": subject,
        "role": role,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    if extra:
        payload.update(extra)

    return jwt.encode(payload, settings.JWT_SECRET, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and validate a JWT access token.

    Returns the payload dict on success, or None if the token is
    invalid, expired, or tampered with.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def create_reset_token(email: str) -> str:
    """
    Create a short-lived (15 min) single-use password-reset token.
    The 'purpose' claim prevents reset tokens from being used as access tokens.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    payload = {
        "sub": email,
        "purpose": "password_reset",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=ALGORITHM)


def decode_reset_token(token: str) -> Optional[str]:
    """
    Decode a password-reset token. Returns the email on success, None on failure.
    Validates that the token has the 'password_reset' purpose claim.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
        if payload.get("purpose") != "password_reset":
            return None
        return payload.get("sub")
    except JWTError:
        return None
