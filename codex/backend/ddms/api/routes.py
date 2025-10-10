from fastapi import APIRouter


router = APIRouter()


@router.get("/health", tags=["system"])
def api_health() -> dict[str, str]:
    """Simple health endpoint under /api."""
    return {"status": "ok"}

