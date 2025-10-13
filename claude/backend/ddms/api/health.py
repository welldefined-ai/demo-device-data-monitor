"""Health check endpoints."""

from fastapi import APIRouter

from ddms.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/api/health")
async def api_health() -> dict[str, str]:
    """
    API health check.

    Returns:
        Health status with environment
    """
    return {
        "status": "ok",
        "env": settings.env,
    }


@router.get("/api/version")
async def api_version() -> dict[str, str]:
    """
    API version information.

    Returns:
        API version
    """
    return {
        "version": settings.api_version,
    }
