"""API v1 router — mounts all endpoint modules."""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.ai_systems import router as ai_systems_router
from app.api.v1.organizations import organizations_router, audit_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(ai_systems_router, tags=["AI Systems"])
api_router.include_router(organizations_router, tags=["Organizations"])
api_router.include_router(audit_router, tags=["Audit"])
