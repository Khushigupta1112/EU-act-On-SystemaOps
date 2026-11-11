"""
ORM model registry — imports all models so Alembic autogenerate can discover them.
"""

from app.models.ai_system import AISystem, AISystemStatus, DeploymentEnvironment, RiskClassification
from app.models.audit_event import AuditEvent
from app.models.base import BaseModel, SoftDeleteMixin, TimestampMixin
from app.models.organization import Organization, OrganizationMember, OrganizationStatus
from app.models.role import Permission, ROLE_PERMISSIONS, UserRole, get_permissions, has_permission
from app.models.user import User

__all__ = [
    "AISystem",
    "AISystemStatus",
    "AuditEvent",
    "BaseModel",
    "DeploymentEnvironment",
    "Organization",
    "OrganizationMember",
    "OrganizationStatus",
    "Permission",
    "RiskClassification",
    "ROLE_PERMISSIONS",
    "SoftDeleteMixin",
    "TimestampMixin",
    "User",
    "UserRole",
    "get_permissions",
    "has_permission",
]
