"""FastAPI application entry point."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ddms.api.auth import router as auth_router
from ddms.api.devices import router as devices_router
from ddms.api.groups import router as groups_router
from ddms.api.health import router as health_router
from ddms.api.users import router as users_router
from ddms.core.config import settings
from ddms.core.logging import setup_logging
from ddms.realtime.websocket import router as websocket_router

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DDMS API",
    description="Device Data Monitoring System",
    version=settings.api_version,
    debug=settings.debug,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(devices_router)
app.include_router(groups_router)
app.include_router(websocket_router)


@app.on_event("startup")
async def startup_event() -> None:
    """Application startup event."""
    logger.info(
        "Starting DDMS API",
        extra={
            "version": settings.api_version,
            "environment": settings.env,
        },
    )

    # Initialize device polling jobs (skip in test environment)
    if settings.env != "test":
        from ddms.scheduler.manager import initialize_all_device_jobs

        await initialize_all_device_jobs()
        logger.info("Device polling scheduler initialized")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Application shutdown event."""
    from ddms.scheduler.manager import stop_scheduler

    stop_scheduler()
    logger.info("Shutting down DDMS API")
