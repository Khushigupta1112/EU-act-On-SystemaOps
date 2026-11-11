"""Pydantic schemas for AI System CRUD endpoints."""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.ai_system import AISystemStatus, DeploymentEnvironment, RiskClassification


class AISystemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    business_purpose: str | None = None
    department: str | None = None
    provider: str | None = None
    model_name: str | None = None
    model_version: str | None = None
    deployment_environment: DeploymentEnvironment | None = None
    business_domain: str | None = None
    user_count_estimate: int | None = Field(None, ge=0)
    data_categories: list[str] = Field(default_factory=list)
    lifecycle_status: AISystemStatus = AISystemStatus.DRAFT
    review_date: date | None = None
    metadata_: dict = Field(default_factory=dict, alias="metadata")

    model_config = {"populate_by_name": True}


class AISystemUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    business_purpose: str | None = None
    department: str | None = None
    provider: str | None = None
    model_name: str | None = None
    model_version: str | None = None
    deployment_environment: DeploymentEnvironment | None = None
    business_domain: str | None = None
    user_count_estimate: int | None = Field(None, ge=0)
    data_categories: list[str] | None = None
    lifecycle_status: AISystemStatus | None = None
    review_date: date | None = None
    metadata_: dict | None = Field(None, alias="metadata")

    model_config = {"populate_by_name": True}


class AISystemResponse(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    description: str | None
    business_purpose: str | None
    owner_id: UUID | None
    department: str | None
    provider: str | None
    model_name: str | None
    model_version: str | None
    deployment_environment: DeploymentEnvironment | None
    business_domain: str | None
    user_count_estimate: int | None
    data_categories: list[str]
    risk_classification: RiskClassification
    lifecycle_status: AISystemStatus
    regulatory_status: str | None
    review_date: date | None
    created_at: datetime
    updated_at: datetime
    version: int

    model_config = {"from_attributes": True}
