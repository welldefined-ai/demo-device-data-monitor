from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Role(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    VIEWER = "viewer"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    role: Mapped[Role] = mapped_column(
        SAEnum(Role, name="userrole", values_callable=lambda enum: [e.value for e in enum]),
        nullable=False,
        default=Role.OWNER,
    )
    language_preference: Mapped[str] = mapped_column(String(8), nullable=False, default="en")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"User(id={self.id!r}, username={self.username!r}, role={self.role!r})"


class DeviceStatus(str, Enum):
    OFFLINE = "offline"
    ONLINE = "online"
    ERROR = "error"


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    unit: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    sampling_interval: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    thresholds: Mapped[str] = mapped_column(
        String, nullable=False, default='{"warning": null, "critical": null}'
    )
    modbus_config: Mapped[str] = mapped_column(String, nullable=False, default='{}')
    status: Mapped[DeviceStatus] = mapped_column(
        SAEnum(DeviceStatus, name="devicestatus", values_callable=lambda e: [x.value for x in e]),
        nullable=False,
        default=DeviceStatus.OFFLINE,
    )
    last_reading_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class GroupDevice(Base):
    __tablename__ = "group_devices"

    group_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    device_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
