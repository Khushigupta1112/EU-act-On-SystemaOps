from uuid import uuid4
from datetime import UTC, datetime, timedelta
import jwt
import pytest
from pydantic_core import ValidationError

from app.config import Settings, settings
from app.core.exceptions import TokenExpiredError, TokenInvalidError
from app.core.security import decode_token, hash_password, verify_password


def test_production_rejects_default_credentials():
    """Verify production settings reject dev credentials, localhost, and weak secrets."""
    with pytest.raises(ValidationError):
        Settings(
            ENVIRONMENT="production",
            DATABASE_URL="postgresql+asyncpg://systemaops:systemaops_dev@localhost:5432/systemaops",
            SECRET_KEY="supersecretkeyforproductionmustbelongenough123456",
        )


def test_production_rejects_short_secret_key():
    """Verify production settings reject short secrets (< 32 chars)."""
    with pytest.raises(ValidationError):
        Settings(
            ENVIRONMENT="production",
            DATABASE_URL="postgresql+asyncpg://prod_user:SecureProdPass123!@db.prod.internal:5432/systemaops_prod",
            SECRET_KEY="shortsecret",
        )


def test_testing_allows_sqlite_url():
    """Verify testing environment allows sqlite database URLs."""
    cfg = Settings(
        ENVIRONMENT="testing",
        DATABASE_URL="sqlite+aiosqlite:///:memory:",
    )
    assert cfg.ENVIRONMENT == "testing"
    assert "sqlite" in cfg.DATABASE_URL


def test_password_longer_than_72_bytes_rejected():
    """Verify bcrypt 72-byte limit is enforced without silent truncation."""
    long_pass = "A" * 73
    with pytest.raises(ValueError, match="Password cannot exceed 72 bytes"):
        hash_password(long_pass)

    assert verify_password(long_pass, "$2b$12$somevalidhashhere") is False


def test_jwt_expired_token_rejected():
    """Verify expired JWT tokens raise TokenExpiredError."""
    past = datetime.now(UTC) - timedelta(minutes=10)
    payload = {
        "sub": str(uuid4()),
        "type": "access",
        "exp": past,
        "iat": past - timedelta(minutes=10),
    }
    expired_token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    with pytest.raises(TokenExpiredError):
        decode_token(expired_token, expected_type="access")


def test_jwt_tampered_signature_rejected():
    """Verify tampered JWT tokens raise TokenInvalidError."""
    future = datetime.now(UTC) + timedelta(minutes=10)
    payload = {
        "sub": str(uuid4()),
        "type": "access",
        "exp": future,
        "iat": future - timedelta(minutes=10),
    }
    token = jwt.encode(payload, "differentsecretkey12345678901234567890", algorithm=settings.ALGORITHM)
    with pytest.raises(TokenInvalidError):
        decode_token(token, expected_type="access")


def test_jwt_wrong_type_rejected():
    """Verify refresh token presented as access token raises TokenInvalidError."""
    future = datetime.now(UTC) + timedelta(minutes=10)
    payload = {
        "sub": str(uuid4()),
        "type": "refresh",
        "exp": future,
        "iat": future - timedelta(minutes=10),
    }
    refresh_token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    with pytest.raises(TokenInvalidError):
        decode_token(refresh_token, expected_type="access")

