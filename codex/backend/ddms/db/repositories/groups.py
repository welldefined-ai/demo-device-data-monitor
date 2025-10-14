from __future__ import annotations

from sqlalchemy import delete, insert, select, update
from sqlalchemy.orm import Session

from ddms.db.models import Device, Group, GroupDevice


def list_groups(session: Session) -> list[Group]:
    stmt = select(Group).order_by(Group.id.asc())
    return list(session.scalars(stmt).all())


def create_group(session: Session, *, name: str, description: str = "") -> Group:
    g = Group(name=name, description=description)
    session.add(g)
    session.commit()
    session.refresh(g)
    return g


def rename_group(session: Session, group: Group, *, name: str | None = None, description: str | None = None) -> Group:
    if name is not None:
        group.name = name
    if description is not None:
        group.description = description
    session.add(group)
    session.commit()
    session.refresh(group)
    return group


def delete_group(session: Session, group: Group) -> None:
    session.execute(delete(GroupDevice).where(GroupDevice.group_id == group.id))
    session.delete(group)
    session.commit()


def assign_device(session: Session, group: Group, device: Device) -> None:
    # Enforce single-group per device by making device_id primary key of mapping
    # Upsert-like semantics: delete existing mapping for device then insert
    session.execute(delete(GroupDevice).where(GroupDevice.device_id == device.id))
    session.add(GroupDevice(group_id=group.id, device_id=device.id))
    session.commit()


def remove_device(session: Session, group: Group, device: Device) -> None:
    session.execute(
        delete(GroupDevice).where(GroupDevice.group_id == group.id, GroupDevice.device_id == device.id)
    )
    session.commit()

