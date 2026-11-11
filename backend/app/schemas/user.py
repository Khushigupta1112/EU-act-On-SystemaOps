"""User management schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.role import UserRole


class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    is_active: bool
    is_verified: bool
    avatar_url: str | None
    timezone: str
    locale: str
    last_login: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class InviteMemberRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=255)
    role: UserRole = UserRole.READ_ONLY


class UpdateMemberRoleRequest(BaseModel):
    role: UserRole


class MemberResponse(BaseModel):
    user_id: UUID
    email: str
    full_name: str
    role: str
    is_primary: bool
    joined_at: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
