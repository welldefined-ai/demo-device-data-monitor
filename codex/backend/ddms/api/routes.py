from fastapi import APIRouter, Depends

from ddms import __version__
from ddms.core.config import Settings, get_settings


router = APIRouter(tags=["system"])


@router.get("/health", summary="API health check")
def api_health(settings: Settings = Depends(get_settings)) -> dict[str, str]:
    """Return API health information."""
    return {"status": "ok", "env": settings.env, "version": __version__}


@router.get("/version", summary="API version")
def api_version() -> dict[str, str]:
    """Return the current API version."""
    return {"version": __version__}
