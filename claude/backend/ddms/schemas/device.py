"""Pydantic schemas for device management."""

from datetime import datetime

from pydantic import BaseModel, Field


class ThresholdConfig(BaseModel):
    """Threshold configuration for device readings."""

    warning: float | None = Field(None, description="Warning threshold value")
    critical: float | None = Field(None, description="Critical threshold value")


class ModbusConfig(BaseModel):
    """Modbus connection configuration."""

    model_config = {"protected_namespaces": ()}

    type: str = Field(..., description="Modbus type: 'tcp' or 'rtu'")
    host: str | None = Field(None, description="Modbus TCP host address")
    port: int | None = Field(None, description="Modbus TCP port")
    serial_port: str | None = Field(None, description="Serial port for RTU")
    baudrate: int | None = Field(None, description="Baudrate for RTU")
    register: int = Field(..., description="Modbus register address")
    data_type: str = Field(..., description="Data type: 'int16', 'uint16', 'float32', etc.")


class DeviceBase(BaseModel):
    """Base device schema with common fields."""

    name: str = Field(..., min_length=1, max_length=100, description="Device name")
    description: str | None = Field(None, description="Device description")
    unit: str = Field(
        ..., min_length=1, max_length=20, description="Reading unit (e.g., °C, bar, RPM)"
    )
    sampling_interval: int = Field(..., gt=0, description="Sampling interval in seconds")
    thresholds: ThresholdConfig | None = Field(None, description="Threshold configuration")
    modbus_config: ModbusConfig = Field(..., description="Modbus connection configuration")


class DeviceCreate(DeviceBase):
    """Schema for creating a new device."""

    pass


class DeviceUpdate(BaseModel):
    """Schema for updating an existing device."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    unit: str | None = Field(None, min_length=1, max_length=20)
    sampling_interval: int | None = Field(None, gt=0)
    thresholds: ThresholdConfig | None = None
    modbus_config: ModbusConfig | None = None


class DeviceResponse(DeviceBase):
    """Schema for device response."""

    id: int = Field(..., description="Device ID")
    status: str = Field(..., description="Connection status: online/offline/error")
    last_reading_at: datetime | None = Field(None, description="Last successful reading timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic config."""

        from_attributes = True


class DeviceListResponse(BaseModel):
    """Schema for list of devices response."""

    devices: list[DeviceResponse] = Field(..., description="List of devices")
    total: int = Field(..., description="Total number of devices")


class ConnectionTestResult(BaseModel):
    """Schema for connection test result."""

    success: bool = Field(..., description="Whether connection test succeeded")
    message: str = Field(..., description="Result message")
    error: str | None = Field(None, description="Error details if failed")
