"""Organization CRUD schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.organization import OrganizationStatus


class OrganizationCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    display_name: str | None = None
    description: str | None = None
    country: str | None = Field(None, min_length=2, max_length=2)

    @field_validator("name")
    @classmethod
    def generate_slug(cls, v: str) -> str:
        return v  # slug generated in service layer


class OrganizationUpdate(BaseModel):
    display_name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    country: str | None = Field(None, min_length=2, max_length=2)
    logo_url: str | None = None
    website: str | None = None


class OrganizationResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    display_name: str
    description: str | None
    status: OrganizationStatus
    plan: str
    max_users: int
    country: str | None
    logo_url: str | None
    website: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
