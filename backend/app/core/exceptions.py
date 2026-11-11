"""
Custom exception hierarchy for SystemaOps.

All exceptions raised in service/repository layers should be subclasses of
SystemaOpsError. FastAPI exception handlers convert these into structured
JSON responses. Never leak internal details (stack traces, SQL, secrets).
"""

from __future__ import annotations

from typing import Any


class SystemaOpsError(Exception):
    """Base class for all application exceptions."""

    code: str = "INTERNAL_ERROR"
    message: str = "An unexpected error occurred."
    status_code: int = 500

    def __init__(
        self,
        message: str | None = None,
        code: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.message = message or self.__class__.message
        self.code = code or self.__class__.code
        self.metadata = metadata or {}
        super().__init__(self.message)


# ---------------------------------------------------------------------------
# Authentication & Authorisation
# ---------------------------------------------------------------------------


class AuthenticationError(SystemaOpsError):
    """Raised when authentication fails (bad credentials, expired token, etc.)."""

    code = "AUTHENTICATION_FAILED"
    message = "Authentication failed."
    status_code = 401


class TokenExpiredError(AuthenticationError):
    code = "TOKEN_EXPIRED"
    message = "The token has expired. Please log in again."


class TokenInvalidError(AuthenticationError):
    code = "TOKEN_INVALID"
    message = "The token is invalid or malformed."


class AccountLockedError(AuthenticationError):
    code = "ACCOUNT_LOCKED"
    message = "Account is temporarily locked due to too many failed login attempts."
    status_code = 403


class EmailNotVerifiedError(AuthenticationError):
    code = "EMAIL_NOT_VERIFIED"
    message = "Please verify your email address before logging in."
    status_code = 403


class PermissionDeniedError(SystemaOpsError):
    """Raised when an authenticated user lacks the required permission."""

    code = "PERMISSION_DENIED"
    message = "You do not have permission to perform this action."
    status_code = 403


class TenantViolationError(SystemaOpsError):
    """
    Raised when a request would cross tenant boundaries.

    This is a security-critical exception. Occurrences should be treated
    as potential access-control bypass attempts and alerted on.
    """

    code = "TENANT_VIOLATION"
    message = "Access denied: resource belongs to a different organisation."
    status_code = 403


# ---------------------------------------------------------------------------
# Resource errors
# ---------------------------------------------------------------------------


class NotFoundError(SystemaOpsError):
    """Resource could not be found (within the tenant scope)."""

    code = "NOT_FOUND"
    message = "The requested resource was not found."
    status_code = 404


class ConflictError(SystemaOpsError):
    """Raised when a create/update would violate a uniqueness constraint."""

    code = "CONFLICT"
    message = "A resource with the same identifier already exists."
    status_code = 409


class ValidationError(SystemaOpsError):
    """Business-logic validation failure (distinct from Pydantic schema errors)."""

    code = "VALIDATION_ERROR"
    message = "The request contains invalid data."
    status_code = 422


class OptimisticLockError(SystemaOpsError):
    """Raised when an optimistic-lock version mismatch is detected on update."""

    code = "OPTIMISTIC_LOCK_CONFLICT"
    message = "The resource was modified by another operation. Please refresh and retry."
    status_code = 409


# ---------------------------------------------------------------------------
# Integration / adapter errors
# ---------------------------------------------------------------------------


class IntegrationError(SystemaOpsError):
    """Base class for errors from external integrations / adapters."""

    code = "INTEGRATION_ERROR"
    message = "An external integration encountered an error."
    status_code = 502


class IntegrationUnavailableError(IntegrationError):
    """The external service is unavailable."""

    code = "INTEGRATION_UNAVAILABLE"
    message = "The external integration is currently unavailable."


class IntegrationAuthError(IntegrationError):
    """Authentication with the external service failed."""

    code = "INTEGRATION_AUTH_FAILED"
    message = "Authentication with the external integration failed."


# ---------------------------------------------------------------------------
# File / evidence errors
# ---------------------------------------------------------------------------


class FileTooLargeError(SystemaOpsError):
    code = "FILE_TOO_LARGE"
    message = "The uploaded file exceeds the maximum allowed size."
    status_code = 413


class FileTypeNotAllowedError(SystemaOpsError):
    code = "FILE_TYPE_NOT_ALLOWED"
    message = "The uploaded file type is not permitted."
    status_code = 415


# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------


class RateLimitExceededError(SystemaOpsError):
    code = "RATE_LIMIT_EXCEEDED"
    message = "Too many requests. Please slow down and try again later."
    status_code = 429
