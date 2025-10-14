from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, Path, status

from ddms.api.deps import SessionDep, require_roles
from ddms.db.models import Group, Role
from ddms.db.repositories.devices import get_device
from ddms.db.repositories.groups import (
    assign_device,
    create_group,
    delete_group,
    list_group_devices,
    list_groups,
    remove_device,
    rename_group,
)
from ddms.schemas.devices import DeviceOut
from ddms.schemas.groups import GroupCreate, GroupOut, GroupUpdate

router = APIRouter(prefix="/groups", tags=["groups"])


@router.get("/", response_model=list[GroupOut])
def groups_list(session: SessionDep) -> list[GroupOut]:
    return [GroupOut.model_validate(g) for g in list_groups(session)]


@router.post(
    "/",
    response_model=GroupOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(Role.ADMIN, Role.OWNER))],
)
def groups_create(payload: GroupCreate, session: SessionDep) -> GroupOut:
    g = create_group(session, name=payload.name, description=payload.description)
    return GroupOut.model_validate(g)


@router.patch(
    "/{group_id}",
    response_model=GroupOut,
    dependencies=[Depends(require_roles(Role.ADMIN, Role.OWNER))],
)
def groups_rename(
    payload: GroupUpdate, session: SessionDep, group_id: int = Path(..., ge=1)
) -> GroupOut:
    g = session.get(Group, group_id)
    if not g:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    g = rename_group(session, g, name=payload.name, description=payload.description)
    return GroupOut.model_validate(g)


@router.delete("/{group_id}", dependencies=[Depends(require_roles(Role.ADMIN, Role.OWNER))])
def groups_delete(session: SessionDep, group_id: int = Path(..., ge=1)) -> dict[str, bool]:
    g = session.get(Group, group_id)
    if not g:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    delete_group(session, g)
    return {"ok": True}


@router.post(
    "/{group_id}/devices/{device_id}",
    dependencies=[Depends(require_roles(Role.ADMIN, Role.OWNER))],
)
def groups_assign(
    session: SessionDep, group_id: int = Path(..., ge=1), device_id: int = Path(..., ge=1)
) -> dict[str, bool]:
    g = session.get(Group, group_id)
    if not g:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    d = get_device(session, device_id)
    if not d:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    assign_device(session, g, d)
    return {"ok": True}


@router.delete(
    "/{group_id}/devices/{device_id}",
    dependencies=[Depends(require_roles(Role.ADMIN, Role.OWNER))],
)
def groups_unassign(
    session: SessionDep, group_id: int = Path(..., ge=1), device_id: int = Path(..., ge=1)
) -> dict[str, bool]:
    g = session.get(Group, group_id)
    if not g:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    d = get_device(session, device_id)
    if not d:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    remove_device(session, g, d)
    return {"ok": True}


@router.get("/{group_id}/devices", response_model=list[DeviceOut])
def groups_devices(session: SessionDep, group_id: int = Path(..., ge=1)) -> list[DeviceOut]:
    g = session.get(Group, group_id)
    if not g:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    devices = list_group_devices(session, g)
    out: list[DeviceOut] = []
    for d in devices:
        thresholds = json.loads(d.thresholds or "{}")
        modbus = json.loads(d.modbus_config or "{}")
        out.append(
            DeviceOut(
                id=d.id,
                name=d.name,
                description=d.description,
                unit=d.unit,
                sampling_interval=d.sampling_interval,
                thresholds=thresholds,
                modbus_config=modbus,
                status=d.status,
                last_reading_at=d.last_reading_at,
                created_at=d.created_at,
                updated_at=d.updated_at,
            )
        )
    return out
