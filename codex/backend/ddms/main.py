from fastapi import FastAPI

from ddms.api.routes import router as api_router
from ddms.core.config import Settings


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = Settings()
    app = FastAPI(title="DDMS API", version="0.0.0", docs_url="/api/docs", openapi_url="/api/openapi.json")

    # Include API routes under the /api prefix
    app.include_router(api_router, prefix="/api")

    @app.get("/health")
    def health() -> dict[str, str]:  # pragma: no cover - trivial
        return {"status": "ok", "env": settings.env}

    return app


app = create_app()

