"""
HTTP middleware for SystemaOps FastAPI application.

Provides:
- Request ID injection (X-Request-ID header)
- Correlation ID propagation
- Structured access logging
- Timing / latency header (X-Process-Time)
- Security headers (CSP, HSTS, etc.)
"""

from __future__ import annotations

import secrets
import time
import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from app.core.logging import correlation_id_var, request_id_var

logger = logging.getLogger(__name__)


class RequestIdMiddleware(BaseHTTPMiddleware):
    """
    Inject a unique request ID into every request/response cycle.

    - If the client sends ``X-Request-ID``, we echo it back (useful for
      end-to-end correlation in distributed tracing).
    - Otherwise we generate a new random ID.
    - The ID is stored in a ContextVar so it is accessible from any log call
      within the request scope.
    """

    def __init__(self, app: ASGIApp, header_name: str = "X-Request-ID") -> None:
        super().__init__(app)
        self.header_name = header_name

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        request_id = request.headers.get(self.header_name) or secrets.token_hex(16)
        token = request_id_var.set(request_id)
        try:
            response = await call_next(request)
            response.headers[self.header_name] = request_id
            return response
        finally:
            request_id_var.reset(token)


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Propagate the X-Correlation-ID header for distributed tracing."""

    def __init__(self, app: ASGIApp, header_name: str = "X-Correlation-ID") -> None:
        super().__init__(app)
        self.header_name = header_name

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        correlation_id = request.headers.get(self.header_name) or secrets.token_hex(16)
        token = correlation_id_var.set(correlation_id)
        try:
            response = await call_next(request)
            response.headers[self.header_name] = correlation_id
            return response
        finally:
            correlation_id_var.reset(token)


class TimingMiddleware(BaseHTTPMiddleware):
    """Add X-Process-Time header and emit access log entries."""

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Process-Time"] = f"{elapsed_ms:.2f}ms"

        logger.info(
            "http_request",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "latency_ms": round(elapsed_ms, 2),
            },
        )
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security-related HTTP response headers.

    These defaults are suitable for a JSON API. Adjust CSP if the backend
    serves any HTML pages.
    """

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=()"
        # HSTS — enable only when TLS is confirmed in production
        # response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
        return response


# Type alias for middleware dispatch callable
Any = object  # avoid importing typing.Any at module level
