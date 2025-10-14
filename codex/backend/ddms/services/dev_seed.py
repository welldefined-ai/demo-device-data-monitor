from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ddms.core.config import Settings
from ddms.db.models import Device
from ddms.db.repositories.devices import create_device
from ddms.scheduler.manager import IngestionScheduler


def ensure_demo_device(
    session: Session, settings: Settings, scheduler: IngestionScheduler | None = None
) -> None:
    """Seed a demo device in development envs if no devices exist."""
    if not settings.dev_autoconfig:
        return
    # Only seed when table exists and is empty
    try:
        exists = session.scalar(select(Device.id).limit(1))
    except Exception:
        return
    if exists:
        return

    d = create_device(
        session,
        name="Simulator-1",
        description="Demo Modbus TCP device",
        unit="units",
        sampling_interval=5,
        thresholds={"warning": 50, "critical": 80},
        modbus_config={
            "type": "tcp",
            "host": "simulator",
            "port": 1502,
            "unit_id": 1,
            "register": 0,
            "data_type": "uint16",
            "byteorder": "big",
        },
    )
    if scheduler is not None:
        try:
            scheduler.add_or_update_device_job(d.id, d.sampling_interval)
        except Exception:
            pass

