"""
Pydantic schemas for authentication endpoints.

These schemas validate request bodies and shape response objects for the
auth API. They are separate from the ORM models (User) to avoid accidentally
exposing internal fields (hashed_password, failed_login_attempts, etc.).
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


# ---------------------------------------------------------------------------
# Requests
# ---------------------------------------------------------------------------


class RegisterRequest(BaseModel):
    """Schema for POST /auth/register."""

    email: EmailStr = Field(..., description="Valid email address (used as login).")
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="At least 8 characters.",
    )
    full_name: str = Field(..., min_length=1, max_length=255)
    organization_name: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Creates a new Organisation for this user.",
    )

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, v: str) -> str:
        return v.lower().strip()

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        """Enforce basic password complexity."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit.")
        return v


class LoginRequest(BaseModel):
    """Schema for POST /auth/login."""

    email: EmailStr
    password: str = Field(..., min_length=1)
    remember_me: bool = False

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, v: str) -> str:
        return v.lower().strip()


class RefreshRequest(BaseModel):
    """Schema for POST /auth/refresh."""

    refresh_token: str = Field(..., min_length=1)


class ForgotPasswordRequest(BaseModel):
    """Schema for POST /auth/forgot-password."""

    email: EmailStr

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, v: str) -> str:
        return v.lower().strip()


class ResetPasswordRequest(BaseModel):
    """Schema for POST /auth/reset-password."""

    token: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit.")
        return v


class UpdateProfileRequest(BaseModel):
    """Schema for PATCH /auth/me."""

    full_name: str | None = Field(None, min_length=1, max_length=255)
    timezone: str | None = Field(None, max_length=50)
    locale: str | None = Field(None, max_length=10)


# ---------------------------------------------------------------------------
# Responses
# ---------------------------------------------------------------------------


class TokenResponse(BaseModel):
    """Returned by login and token refresh."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Access token TTL in seconds.")
    user: dict | None = None


class UserResponse(BaseModel):
    """Safe user representation — no sensitive fields."""

    id: UUID
    email: str
    full_name: str
    is_active: bool
    is_verified: bool
    is_superuser: bool
    avatar_url: str | None
    timezone: str
    locale: str
    last_login: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class MeResponse(BaseModel):
    """Extended profile response for GET /auth/me."""

    id: UUID
    email: str
    full_name: str
    is_active: bool
    is_verified: bool
    is_superuser: bool
    avatar_url: str | None = None
    timezone: str = "UTC"
    locale: str = "en"
    last_login: datetime | None = None
    created_at: datetime | None = None
    user: UserResponse | None = None
    memberships: list[dict] = Field(default_factory=list)  # org_id, org_name, role, is_primary

    model_config = {"from_attributes": True}
