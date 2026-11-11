"""Concrete repositories."""

from app.repositories.base import BaseRepository

from app.models.ai_system import AISystem
from app.models.organization import Organization, OrganizationMember
from app.models.user import User
from app.models.audit_event import AuditEvent


class AISystemRepository(BaseRepository[AISystem]):
    pass


class OrganizationRepository(BaseRepository[Organization]):
    pass


class UserRepository(BaseRepository[User]):
    pass


__all__ = [
    "AISystemRepository",
    "AuditEvent",
    "BaseRepository",
    "OrganizationMember",
    "OrganizationRepository",
    "UserRepository",
]
