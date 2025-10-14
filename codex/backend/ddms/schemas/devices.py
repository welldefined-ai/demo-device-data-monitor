from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from ddms.db.models import DeviceStatus


class DeviceBase(BaseModel):
    name: str
    description: str = ""
    unit: str = ""
    sampling_interval: int = 60
    thresholds: dict[str, Any] = Field(default_factory=dict)
    modbus_config: dict[str, Any] = Field(default_factory=dict)


class DeviceCreate(DeviceBase):
    pass


class DeviceUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    unit: str | None = None
    sampling_interval: int | None = None
    thresholds: dict[str, Any] | None = None
    modbus_config: dict[str, Any] | None = None


class DeviceOut(DeviceBase):
    id: int
    status: DeviceStatus
    last_reading_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TestConnectionResponse(BaseModel):
    ok: bool
    error: str | None = None

