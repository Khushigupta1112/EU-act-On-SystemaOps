"""Common pagination and response wrapper schemas."""

from __future__ import annotations

from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated list wrapper."""

    items: list[T]
    total: int
    page: int
    page_size: int
    pages: int

    @classmethod
    def create(
        cls, items: list[T], total: int, page: int, page_size: int
    ) -> "PaginatedResponse[T]":
        import math
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            pages=math.ceil(total / page_size) if page_size else 0,
        )


class MessageResponse(BaseModel):
    """Simple acknowledgement response."""
    message: str


class ErrorResponse(BaseModel):
    """Standard error response body."""
    error: ErrorDetail


class ErrorDetail(BaseModel):
    code: str
    message: str
    request_id: str | None = None
    metadata: dict = Field(default_factory=dict)
