from fastapi import FastAPI

from ddms import __version__
from ddms.api.routes import router as api_router
from ddms.core.config import get_settings
from ddms.core.logging import configure_logging


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(title="DDMS API", version=__version__, docs_url="/api/docs", openapi_url="/api/openapi.json")

    # Include API routes under the /api prefix
    app.include_router(api_router, prefix="/api")

    @app.get("/health")
    def health() -> dict[str, str]:  # pragma: no cover - trivial
        return {"status": "ok", "env": settings.env, "version": __version__}

    return app


app = create_app()
