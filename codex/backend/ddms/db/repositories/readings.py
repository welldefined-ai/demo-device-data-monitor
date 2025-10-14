from __future__ import annotations

from datetime import datetime

from sqlalchemy import Select, desc, select
from sqlalchemy.orm import Session

from ddms.db.models import Reading


def create_reading(
    session: Session, *, device_id: int, timestamp: datetime, value: float
) -> Reading:
    r = Reading(device_id=device_id, timestamp=timestamp, value=value)
    session.add(r)
    session.commit()
    session.refresh(r)
    return r


def list_recent_readings(
    session: Session, *, device_id: int, limit: int = 20
) -> list[Reading]:
    stmt: Select[tuple[Reading]] = select(Reading).where(Reading.device_id == device_id).order_by(
        desc(Reading.timestamp)
    ).limit(limit)
    return list(session.scalars(stmt).all())
