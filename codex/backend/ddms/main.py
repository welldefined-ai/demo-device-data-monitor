from fastapi import FastAPI
from sqlalchemy.exc import SQLAlchemyError

from ddms import __version__
from ddms.api.routes import router as api_router
from ddms.api.routes_auth import router as auth_router
from ddms.api.routes_devices import router as devices_router
from ddms.api.routes_groups import router as groups_router
from ddms.api.routes_users import router as users_router
from ddms.core.config import get_settings
from ddms.core.logging import configure_logging
from ddms.db.session import SessionLocal
from ddms.services.bootstrap import ensure_owner_account
from ddms.scheduler.manager import IngestionScheduler
from ddms.services.dev_seed import ensure_demo_device


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
    app.include_router(devices_router, prefix="/api")
    app.include_router(groups_router, prefix="/api")

    # Initialize scheduler
    app.state.scheduler = IngestionScheduler(SessionLocal)

    @app.on_event("startup")
    def _startup() -> None:
        # Ensure owner account exists after migrations are applied; skip if DB unavailable
        try:
            with SessionLocal() as session:
                ensure_owner_account(session, settings)
        except SQLAlchemyError:
            pass
        # Start scheduler (rebuilt here to honor any runtime SessionLocal patches)
        try:
            app.state.scheduler = IngestionScheduler(SessionLocal)
            app.state.scheduler.start()
            app.state.scheduler.refresh_all_jobs()
        except Exception:
            # Do not fail app startup because of scheduler issues
            pass
        # Dev seed (optional)
        try:
            with SessionLocal() as session:
                ensure_demo_device(session, settings, app.state.scheduler)
        except Exception:
            pass

    @app.on_event("shutdown")
    def _shutdown() -> None:
        try:
            app.state.scheduler.shutdown()
        except Exception:
            pass

    return app


app = create_app()
