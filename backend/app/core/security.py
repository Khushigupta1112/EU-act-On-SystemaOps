"""
JWT creation/verification and password hashing utilities.

Security primitives used across the auth service. No framework imports here –
this module must remain dependency-free from FastAPI to be easily testable.
"""

from __future__ import annotations

import secrets
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from jose import JWTError, jwt
import bcrypt

# Ensure passlib recognizes modern bcrypt version cleanly
if not hasattr(bcrypt, "__about__"):
    bcrypt.__about__ = type("about", (), {"__version__": bcrypt.__version__})()

from passlib.context import CryptContext

from app.config import settings
from app.core.exceptions import TokenExpiredError, TokenInvalidError

# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

_pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,  # OWASP-recommended minimum
)


def hash_password(plain: str) -> str:
    """Return a bcrypt hash of *plain*. Never store plain-text passwords."""
    if len(plain.encode("utf-8")) > 72:
        raise ValueError("Password cannot exceed 72 bytes to prevent bcrypt silent truncation.")
    return _pwd_context.hash(plain)


get_password_hash = hash_password  # Alias for backward compatibility


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if *plain* matches the stored *hashed* password."""
    if len(plain.encode("utf-8")) > 72:
        return False
    return _pwd_context.verify(plain, hashed)


def needs_rehash(hashed: str) -> bool:
    """
    Return True if the hash was created with deprecated settings.

    Call after a successful login to upgrade legacy hashes transparently.
    """
    return _pwd_context.needs_update(hashed)


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------

TokenData = dict[str, Any]


def _utcnow() -> datetime:
    return datetime.now(UTC)


def create_access_token(
    user_id: UUID,
    organization_id: UUID | None,
    role: str,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """
    Create a short-lived JWT access token.

    Payload claims:
    - ``sub``    – user ID (string)
    - ``org_id`` – current organisation ID (string | None)
    - ``role``   – role name within the organisation
    - ``type``   – literal ``"access"``
    - ``jti``    – unique token identifier (for future revocation support)
    - ``iat``    – issued-at timestamp
    - ``exp``    – expiry timestamp
    """
    now = _utcnow()
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "org_id": str(organization_id) if organization_id else None,
        "role": role,
        "type": "access",
        "jti": secrets.token_hex(16),
        "iat": now,
        "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(
    user_id: UUID,
    organization_id: UUID | None,
    role: str,
) -> str:
    """
    Create a long-lived JWT refresh token.

    Refresh tokens carry a ``jti`` that is stored server-side (Redis) to enable
    rotation and revocation. The token type is ``"refresh"`` to prevent
    accidental use as an access token.
    """
    now = _utcnow()
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "org_id": str(organization_id) if organization_id else None,
        "role": role,
        "type": "refresh",
        "jti": secrets.token_hex(16),
        "iat": now,
        "exp": now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str, expected_type: str = "access") -> TokenData:
    """
    Decode and validate a JWT, returning its payload.

    Raises:
        TokenExpiredError: if the token has expired.
        TokenInvalidError: if the signature is invalid or claims are wrong.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except JWTError as exc:
        if "expired" in str(exc).lower():
            raise TokenExpiredError() from exc
        raise TokenInvalidError() from exc

    token_type = payload.get("type")
    if token_type != expected_type:
        raise TokenInvalidError()

    if "sub" not in payload:
        raise TokenInvalidError()

    return payload


def generate_secure_token(nbytes: int = 32) -> str:
    """Generate a cryptographically secure random URL-safe token string."""
    return secrets.token_urlsafe(nbytes)


def generate_password_reset_token(email: str) -> str:
    """
    Create a short-lived (1 hour) signed token embedding the user's email.

    Used for password-reset links. The ``type`` claim is ``"password_reset"``
    to prevent reuse as an auth token.
    """
    now = _utcnow()
    payload = {
        "sub": email,
        "type": "password_reset",
        "jti": secrets.token_hex(16),
        "iat": now,
        "exp": now + timedelta(hours=1),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_password_reset_token(token: str) -> str:
    """
    Decode a password-reset token and return the embedded email.

    Raises:
        TokenExpiredError | TokenInvalidError on any problem.
    """
    payload = decode_token(token, expected_type="password_reset")
    email = payload.get("sub")
    if not email or not isinstance(email, str):
        raise TokenInvalidError()
    return email


def generate_email_verification_token(email: str) -> str:
    """
    Create a signed email-verification token (24-hour validity).

    The ``type`` claim is ``"email_verify"`` to prevent cross-purpose use.
    """
    now = _utcnow()
    payload = {
        "sub": email,
        "type": "email_verify",
        "jti": secrets.token_hex(16),
        "iat": now,
        "exp": now + timedelta(hours=24),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_email_verification_token(token: str) -> str:
    """
    Decode an email-verification token and return the embedded email.

    Raises:
        TokenExpiredError | TokenInvalidError on any problem.
    """
    payload = decode_token(token, expected_type="email_verify")
    email = payload.get("sub")
    if not email or not isinstance(email, str):
        raise TokenInvalidError()
    return email
