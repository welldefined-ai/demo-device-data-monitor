"""Scheduler manager for device polling jobs."""

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from ddms.db.base import async_session_maker
from ddms.ingestion.poller import poll_device

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler: AsyncIOScheduler | None = None


def get_scheduler() -> AsyncIOScheduler:
    """
    Get or create the global scheduler instance.

    Returns:
        AsyncIOScheduler instance
    """
    global scheduler
    if scheduler is None:
        scheduler = AsyncIOScheduler()
        scheduler.start()
        logger.info("APScheduler started")
    return scheduler


def stop_scheduler() -> None:
    """Stop the global scheduler instance."""
    global scheduler
    if scheduler is not None:
        scheduler.shutdown()
        scheduler = None
        logger.info("APScheduler stopped")


async def poll_device_job(device_id: int) -> None:
    """
    Job function to poll a device.

    This is called by APScheduler at the configured interval.

    Args:
        device_id: ID of device to poll
    """
    async with async_session_maker() as session:
        await poll_device(device_id, session)


def add_device_job(device_id: int, sampling_interval: int) -> None:
    """
    Add a polling job for a device.

    Args:
        device_id: ID of device
        sampling_interval: Polling interval in seconds
    """
    sched = get_scheduler()
    job_id = f"device_{device_id}"

    # Remove existing job if present
    if sched.get_job(job_id):
        sched.remove_job(job_id)

    # Add new job with interval trigger
    sched.add_job(
        poll_device_job,
        trigger=IntervalTrigger(seconds=sampling_interval),
        args=[device_id],
        id=job_id,
        name=f"Poll device {device_id}",
        replace_existing=True,
    )

    logger.info(f"Added polling job for device {device_id} with interval {sampling_interval}s")


def update_device_job(device_id: int, sampling_interval: int) -> None:
    """
    Update the polling interval for a device job.

    Args:
        device_id: ID of device
        sampling_interval: New polling interval in seconds
    """
    sched = get_scheduler()
    job_id = f"device_{device_id}"

    # Check if job exists
    job = sched.get_job(job_id)
    if job:
        # Reschedule with new interval
        sched.reschedule_job(
            job_id,
            trigger=IntervalTrigger(seconds=sampling_interval),
        )
        logger.info(f"Updated polling interval for device {device_id} to {sampling_interval}s")
    else:
        # Job doesn't exist, create it
        add_device_job(device_id, sampling_interval)


def remove_device_job(device_id: int) -> None:
    """
    Remove the polling job for a device.

    Args:
        device_id: ID of device
    """
    sched = get_scheduler()
    job_id = f"device_{device_id}"

    if sched.get_job(job_id):
        sched.remove_job(job_id)
        logger.info(f"Removed polling job for device {device_id}")


async def initialize_all_device_jobs() -> None:
    """
    Initialize polling jobs for all existing devices.

    Called during application startup.
    """
    from ddms.db.models import Device

    async with async_session_maker() as session:
        # Fetch all devices
        from sqlalchemy import select

        result = await session.execute(select(Device))
        devices = result.scalars().all()

        for device in devices:
            add_device_job(device.id, device.sampling_interval)

        logger.info(f"Initialized polling jobs for {len(devices)} devices")
