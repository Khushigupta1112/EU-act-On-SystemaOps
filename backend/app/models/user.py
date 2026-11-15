"""
User model for SystemaOps.

Users are global platform entities that can belong to one or more
Organizations through the OrganizationMember join table.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class User(BaseModel):
    """
    Platform user entity.

    Authentication attributes
    -------------------------
    - ``email`` is the primary identifier (unique across the platform).
    - ``hashed_password`` stores only a bcrypt hash; the plain-text is never persisted.
    - ``failed_login_attempts`` + ``locked_until`` implement account lockout.
    - ``is_verified`` gates access until email is confirmed.
    - ``is_superuser`` grants SUPER_ADMIN access to all tenants (internal staff only).
    """

    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email", name="uq_users_email"),
        Index("ix_users_email", "email"),
        Index("ix_users_is_active", "is_active"),
        Index("ix_users_created_at", "created_at"),
    )

    email: Mapped[str] = mapped_column(
        String(320),  # RFC 5321 max
        nullable=False,
        comment="Primary identifier. Must be lowercase and unique.",
    )
    hashed_password: Mapped[str] = mapped_column(
        String(1024), nullable=False, comment="bcrypt hash — never store plaintext."
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="True once the user has confirmed their email address.",
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Platform super-admin flag. Grant only to internal staff.",
    )
    last_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    failed_login_attempts: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Account is locked until this timestamp (None = not locked).",
    )
    password_changed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    avatar_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    timezone: Mapped[str] = mapped_column(
        String(50), nullable=False, default="UTC"
    )
    locale: Mapped[str] = mapped_column(
        String(10), nullable=False, default="en"
    )

    # ---- Relationships -------------------------------------------------------
    memberships: Mapped[list["OrganizationMember"]] = relationship(  # noqa: F821
        "OrganizationMember",
        foreign_keys="OrganizationMember.user_id",
        back_populates=None,
        lazy="select",
        cascade="all, delete-orphan",
    )

    @property
    def is_locked(self) -> bool:
        """Return True if the account is currently locked out."""
        from datetime import UTC

        if self.locked_until is None:
            return False
        from datetime import datetime

        return datetime.now(UTC) < self.locked_until

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User id={self.id} email={self.email!r}>"
