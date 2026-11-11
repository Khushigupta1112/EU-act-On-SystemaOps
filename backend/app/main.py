"""
SystemaOps FastAPI application entry point.

Configures middleware, exception handlers, health endpoints, and mounts
the versioned API router. Import this module to run with uvicorn:

    uvicorn app.main:app --reload
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.v1.router import api_router
from app.config import settings
from app.core.exceptions import SystemaOpsError
from app.core.logging import configure_logging
from app.core.middleware import (
    CorrelationIdMiddleware,
    RequestIdMiddleware,
    SecurityHeadersMiddleware,
    TimingMiddleware,
)
from app.database import engine

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Application lifespan
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Startup and shutdown lifecycle hooks."""
    configure_logging(level="DEBUG" if settings.DEBUG else "INFO")
    logger.info(
        "startup",
        extra={
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
        },
    )
    yield
    # Dispose the connection pool gracefully on shutdown
    await engine.dispose()
    logger.info("shutdown", extra={"app": settings.APP_NAME})


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    app = FastAPI(
        title="SystemaOps API",
        description=(
            "Enterprise AI Governance and Compliance Control Plane.\n\n"
            "> **Disclaimer**: SystemaOps provides evidence-based governance, "
            "assessment, workflow and monitoring capabilities. It does not "
            "constitute legal advice or legal certification of compliance. "
            "Final compliance determinations remain the responsibility of "
            "qualified organisational and legal stakeholders."
        ),
        version=settings.APP_VERSION,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    # ---- Middleware (outermost → innermost) ---------------------------------

    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(TimingMiddleware)
    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(o) for o in settings.CORS_ORIGINS],
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
        expose_headers=["X-Request-ID", "X-Correlation-ID", "X-Process-Time"],
    )

    # ---- Exception handlers ------------------------------------------------

    @app.exception_handler(SystemaOpsError)
    async def systemaops_error_handler(
        request: Request, exc: SystemaOpsError
    ) -> JSONResponse:
        from app.core.logging import request_id_var

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "request_id": request_id_var.get(),
                }
            },
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        from app.core.logging import request_id_var

        logger.exception("unhandled_exception", extra={"path": str(request.url)})
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred. Please try again.",
                    "request_id": request_id_var.get(),
                }
            },
        )

    # ---- Health endpoints --------------------------------------------------

    @app.get("/health", tags=["Health"], include_in_schema=False)
    async def health() -> dict:
        """Basic liveness check — returns 200 if the process is alive."""
        return {"status": "ok", "version": settings.APP_VERSION}

    @app.get("/ready", tags=["Health"], include_in_schema=False)
    async def ready() -> dict:
        """
        Readiness check — verifies database connectivity.

        Returns 503 if any dependency is unavailable so that load balancers
        and Kubernetes readiness probes can route traffic away.
        """
        from fastapi import status as http_status
        from app.database import AsyncSessionLocal

        try:
            async with AsyncSessionLocal() as session:
                await session.execute(text("SELECT 1"))
            db_ok = True
        except Exception:
            db_ok = False
            logger.exception("readiness_check_db_failed")

        overall = "ready" if db_ok else "degraded"
        code = 200 if db_ok else 503

        return JSONResponse(
            status_code=code,
            content={
                "status": overall,
                "checks": {"database": "ok" if db_ok else "error"},
            },
        )

    # ---- API router --------------------------------------------------------

    app.include_router(api_router)

    return app


app = create_app()
