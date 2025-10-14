from __future__ import annotations

import json
import socket

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy import select

from ddms.api.deps import SessionDep, require_roles
from ddms.db.models import Device, Role
from ddms.db.repositories.devices import (
    create_device,
    delete_device,
    get_device,
    list_devices,
    update_device,
)
from ddms.schemas.devices import (
    DeviceCreate,
    DeviceOut,
    DeviceUpdate,
    TestConnectionResponse,
)

router = APIRouter(prefix="/devices", tags=["devices"])


@router.get(
    "/",
    response_model=list[DeviceOut],
    dependencies=[Depends(require_roles(Role.ADMIN, Role.OWNER, Role.VIEWER))],
)
def devices_list(session: SessionDep) -> list[DeviceOut]:
    return [device_to_out(d) for d in list_devices(session)]


@router.post(
    "/",
    response_model=DeviceOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(Role.ADMIN, Role.OWNER))],
)
def devices_create(payload: DeviceCreate, session: SessionDep) -> DeviceOut:
    if session.scalar(select(Device.id).where(Device.name == payload.name)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Device name already exists"
        )
    d = create_device(
        session,
        name=payload.name,
        description=payload.description,
        unit=payload.unit,
        sampling_interval=payload.sampling_interval,
        thresholds=payload.thresholds,
        modbus_config=payload.modbus_config,
    )
    return device_to_out(d)


@router.get("/{device_id}", response_model=DeviceOut)
def devices_get(session: SessionDep, device_id: int = Path(..., ge=1)) -> DeviceOut:
    d = get_device(session, device_id)
    if not d:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return device_to_out(d)


@router.patch(
    "/{device_id}",
    response_model=DeviceOut,
    dependencies=[Depends(require_roles(Role.ADMIN, Role.OWNER))],
)
def devices_patch(
    payload: DeviceUpdate, session: SessionDep, device_id: int = Path(..., ge=1)
) -> DeviceOut:
    d = get_device(session, device_id)
    if not d:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    updated = update_device(
        session,
        d,
        name=payload.name,
        description=payload.description,
        unit=payload.unit,
        sampling_interval=payload.sampling_interval,
        thresholds=payload.thresholds,
        modbus_config=payload.modbus_config,
    )
    return device_to_out(updated)


@router.delete("/{device_id}", dependencies=[Depends(require_roles(Role.ADMIN, Role.OWNER))])
def devices_delete(session: SessionDep, device_id: int = Path(..., ge=1)) -> dict[str, bool]:
    d = get_device(session, device_id)
    if not d:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    delete_device(session, d)
    return {"ok": True}


@router.post("/{device_id}/test-connection", response_model=TestConnectionResponse)
def devices_test_connection(
    session: SessionDep, device_id: int = Path(..., ge=1)
) -> TestConnectionResponse:
    d = get_device(session, device_id)
    if not d:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    try:
        cfg = json.loads(d.modbus_config or "{}")
        typ = cfg.get("type")
        if typ == "tcp":
            host = cfg.get("host")
            port = int(cfg.get("port", 502))
            ok = _ping_tcp(host, port)
            return TestConnectionResponse(ok=ok, error=None if ok else "unreachable")
        # Stubbed for RTU or others
        return TestConnectionResponse(ok=False, error="unsupported")
    except Exception as err:  # pragma: no cover - network
        return TestConnectionResponse(ok=False, error=str(err))


def _ping_tcp(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1.5)
        try:
            s.connect((host, port))
            return True
        except Exception:
            return False


def device_to_out(d: Device) -> DeviceOut:
    # Expand JSON fields for API response
    thresholds = json.loads(d.thresholds or "{}")
    modbus_config = json.loads(d.modbus_config or "{}")
    return DeviceOut(
        id=d.id,
        name=d.name,
        description=d.description,
        unit=d.unit,
        sampling_interval=d.sampling_interval,
        thresholds=thresholds,
        modbus_config=modbus_config,
        status=d.status,
        last_reading_at=d.last_reading_at,
        created_at=d.created_at,
        updated_at=d.updated_at,
    )
