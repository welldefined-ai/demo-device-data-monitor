"""Pydantic schemas for device readings."""

from datetime import datetime

from pydantic import BaseModel, Field


class ReadingResponse(BaseModel):
    """Schema for a single reading."""

    device_id: int = Field(..., description="Device ID")
    timestamp: datetime = Field(..., description="Reading timestamp")
    value: float = Field(..., description="Reading value")

    class Config:
        """Pydantic config."""

        from_attributes = True


class ReadingsListResponse(BaseModel):
    """Schema for list of readings."""

    readings: list[ReadingResponse] = Field(..., description="List of readings")
    total: int = Field(..., description="Total number of readings")
