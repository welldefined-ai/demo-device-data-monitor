"""Health check endpoints."""

from fastapi import APIRouter

from ddms.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def system_health() -> dict[str, str]:
    """
    System health check.

    Returns:
        Health status with environment information
    """
    return {
        "status": "ok",
        "env": settings.environment,
    }


@router.get("/api/health")
async def api_health() -> dict[str, str]:
    """
    API health check.

    Returns:
        Health status matching root health endpoint
    """
    return {
        "status": "ok",
        "env": settings.environment,
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
