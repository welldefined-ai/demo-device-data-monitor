from fastapi import FastAPI

from ddms import __version__
from ddms.api.routes import router as api_router
from ddms.api.routes_auth import router as auth_router
from ddms.api.routes_users import router as users_router
from ddms.core.config import get_settings
from ddms.core.logging import configure_logging
from ddms.db.session import SessionLocal
from ddms.services.bootstrap import ensure_owner_account


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(
        title="DDMS API",
        version=__version__,
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
    )

    # Include API routes under the /api prefix
    app.include_router(api_router, prefix="/api")
    app.include_router(auth_router, prefix="/api")
    app.include_router(users_router, prefix="/api")

    @app.on_event("startup")
    def _bootstrap_owner() -> None:
        # Ensure owner account exists after migrations are applied
        with SessionLocal() as session:
            ensure_owner_account(session, settings)

    return app


app = create_app()
