"""
Tenant-aware generic repository base.

Every concrete repository inherits from this class. The core guarantee is:
**every method that reads or writes tenant data accepts and filters by
``organization_id``**. This is the primary enforcement point for tenant
isolation, complementing the JWT-level org_id claim and the FK constraint
on the database.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, OptimisticLockError, TenantViolationError
from app.models.base import BaseModel

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """
    Generic async repository with built-in tenant isolation.

    All methods that accept ``organization_id`` MUST filter on it.
    Methods that return a single record raise ``NotFoundError`` (not None)
    so callers do not need to check for None separately.

    Soft-delete convention
    ----------------------
    Records with ``deleted_at IS NOT NULL`` are considered deleted. All
    ``list`` and ``get`` methods exclude them by default.
    """

    def __init__(self, model: type[ModelType], db: AsyncSession) -> None:
        self.model = model
        self.db = db

    # -------------------------------------------------------------------------
    # Read
    # -------------------------------------------------------------------------

    async def get(
        self,
        id: UUID,
        organization_id: UUID,
        *,
        include_deleted: bool = False,
    ) -> ModelType:
        """
        Fetch a single record by PK within the given tenant.

        Raises
        ------
        NotFoundError
            If the record does not exist (or has been soft-deleted).
        TenantViolationError
            If the record exists but belongs to a different tenant.
        """
        stmt = select(self.model).where(self.model.id == id)
        if not include_deleted:
            stmt = stmt.where(self.model.deleted_at.is_(None))

        result = await self.db.execute(stmt)
        obj: ModelType | None = result.scalar_one_or_none()

        if obj is None:
            raise NotFoundError(
                f"{self.model.__name__} with id={id} was not found."
            )

        # Tenant isolation check — even if we found the record
        if hasattr(obj, "organization_id") and obj.organization_id != organization_id:
            logger.warning(
                "tenant_violation_attempt",
                extra={
                    "model": self.model.__name__,
                    "resource_id": str(id),
                    "expected_org": str(organization_id),
                    "actual_org": str(obj.organization_id),
                },
            )
            raise TenantViolationError()

        return obj

    async def list(
        self,
        organization_id: UUID,
        *,
        skip: int = 0,
        limit: int = 50,
        include_deleted: bool = False,
        order_by: Any = None,
    ) -> tuple[list[ModelType], int]:
        """
        Return a paginated list of records for the given tenant.

        Returns
        -------
        (items, total)
            ``items`` is the page slice; ``total`` is the full count.
        """
        base_stmt = select(self.model).where(
            self.model.organization_id == organization_id
        )
        if not include_deleted:
            base_stmt = base_stmt.where(self.model.deleted_at.is_(None))

        # Total count
        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total: int = (await self.db.execute(count_stmt)).scalar_one()

        # Data page
        if order_by is not None:
            base_stmt = base_stmt.order_by(order_by)
        else:
            base_stmt = base_stmt.order_by(self.model.created_at.desc())

        result = await self.db.execute(base_stmt.offset(skip).limit(limit))
        items: list[ModelType] = list(result.scalars().all())

        return items, total

    # -------------------------------------------------------------------------
    # Write
    # -------------------------------------------------------------------------

    async def create(self, data: dict[str, Any]) -> ModelType:
        """
        Insert a new record.

        The caller is responsible for including ``organization_id`` in ``data``.
        """
        obj = self.model(**data)
        self.db.add(obj)
        await self.db.flush()  # populate defaults (id, created_at, …)
        await self.db.refresh(obj)
        return obj

    async def update(
        self,
        id: UUID,
        organization_id: UUID,
        data: dict[str, Any],
        *,
        expected_version: int | None = None,
    ) -> ModelType:
        """
        Update fields on an existing record.

        Supports optimistic locking via ``expected_version``: if provided and
        the current version differs, ``OptimisticLockError`` is raised.
        """
        obj = await self.get(id, organization_id)

        if expected_version is not None and obj.version != expected_version:
            raise OptimisticLockError()

        for field, value in data.items():
            if value is not None or field in data:
                setattr(obj, field, value)

        obj.version += 1
        obj.updated_at = datetime.now(UTC)

        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def soft_delete(self, id: UUID, organization_id: UUID) -> None:
        """Mark a record as deleted without removing it from the database."""
        obj = await self.get(id, organization_id)
        obj.deleted_at = datetime.now(UTC)
        await self.db.flush()

    async def hard_delete(self, id: UUID, organization_id: UUID) -> None:
        """Permanently remove a record. Use with caution."""
        obj = await self.get(id, organization_id)
        await self.db.delete(obj)
        await self.db.flush()
