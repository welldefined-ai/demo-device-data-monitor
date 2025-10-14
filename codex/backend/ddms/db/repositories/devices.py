from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from ddms.db.models import Device, DeviceStatus, GroupDevice


def list_devices(session: Session) -> list[Device]:
    stmt = select(Device).order_by(Device.id.asc())
    return list(session.scalars(stmt).all())


def get_device(session: Session, device_id: int) -> Device | None:
    return session.get(Device, device_id)


def create_device(
    session: Session,
    *,
    name: str,
    description: str,
    unit: str,
    sampling_interval: int,
    thresholds: dict[str, Any],
    modbus_config: dict[str, Any],
) -> Device:
    d = Device(
        name=name,
        description=description,
        unit=unit,
        sampling_interval=sampling_interval,
        thresholds=json_dumps(thresholds),
        modbus_config=json_dumps(modbus_config),
        status=DeviceStatus.OFFLINE,
    )
    session.add(d)
    session.commit()
    session.refresh(d)
    return d


def update_device(
    session: Session,
    device: Device,
    *,
    name: str | None = None,
    description: str | None = None,
    unit: str | None = None,
    sampling_interval: int | None = None,
    thresholds: dict[str, Any] | None = None,
    modbus_config: dict[str, Any] | None = None,
    status: DeviceStatus | None = None,
) -> Device:
    if name is not None:
        device.name = name
    if description is not None:
        device.description = description
    if unit is not None:
        device.unit = unit
    if sampling_interval is not None:
        device.sampling_interval = sampling_interval
    if thresholds is not None:
        device.thresholds = json_dumps(thresholds)
    if modbus_config is not None:
        device.modbus_config = json_dumps(modbus_config)
    if status is not None:
        device.status = status
    session.add(device)
    session.commit()
    session.refresh(device)
    return device


def delete_device(session: Session, device: Device) -> None:
    # Remove from group_devices mapping
    session.execute(delete(GroupDevice).where(GroupDevice.device_id == device.id))
    session.delete(device)
    session.commit()


def json_dumps(data: dict[str, Any]) -> str:
    import json

    return json.dumps(data, separators=(",", ":"))

