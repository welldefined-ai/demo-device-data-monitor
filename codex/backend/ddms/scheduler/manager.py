from __future__ import annotations

import logging
from typing import Any

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session, sessionmaker

from ddms.db.models import Device
from ddms.ingestion.poller import poll_device

logger = logging.getLogger(__name__)


class IngestionScheduler:
    """Manage APScheduler jobs for device polling."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory
        self._scheduler = BackgroundScheduler()

    def start(self) -> None:
        if not self._scheduler.running:
            self._scheduler.start()
            logger.info("Scheduler started")

    def shutdown(self) -> None:
        if self._scheduler.running:
            self._scheduler.shutdown(wait=False)
            logger.info("Scheduler stopped")

    def _job_id(self, device_id: int) -> str:
        return f"poller:{device_id}"

    def add_or_update_device_job(self, device_id: int, interval_seconds: int) -> None:
        job_id = self._job_id(device_id)
        trigger = IntervalTrigger(seconds=max(1, interval_seconds))
        # Replace existing job if present
        self._scheduler.add_job(
            poll_device,
            id=job_id,
            trigger=trigger,
            replace_existing=True,
            kwargs={"session_factory": self._session_factory, "device_id": device_id},
            max_instances=1,
            coalesce=True,
        )
        logger.info("Scheduled device %s every %ss", device_id, interval_seconds)

    def remove_device_job(self, device_id: int) -> None:
        job_id = self._job_id(device_id)
        try:
            self._scheduler.remove_job(job_id)
            logger.info("Removed schedule for device %s", device_id)
        except Exception:  # pragma: no cover - harmless if not present
            pass

    def refresh_all_jobs(self) -> None:
        """Load all devices and ensure jobs reflect sampling intervals."""
        session = self._session_factory()
        try:
            for d in session.query(Device).order_by(Device.id.asc()).all():
                self.add_or_update_device_job(d.id, d.sampling_interval)
        finally:
            session.close()

