"""Pydantic schemas for group management."""

from datetime import datetime

from pydantic import BaseModel, Field


class GroupBase(BaseModel):
    """Base group schema with common fields."""

    name: str = Field(..., min_length=1, max_length=100, description="Group name")
    description: str | None = Field(None, description="Group description")


class GroupCreate(GroupBase):
    """Schema for creating a new group."""

    pass


class GroupUpdate(BaseModel):
    """Schema for updating an existing group."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None


class GroupResponse(GroupBase):
    """Schema for group response."""

    id: int = Field(..., description="Group ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    device_count: int | None = Field(None, description="Number of devices in group")

    class Config:
        """Pydantic config."""

        from_attributes = True


class GroupListResponse(BaseModel):
    """Schema for list of groups response."""

    groups: list[GroupResponse] = Field(..., description="List of groups")
    total: int = Field(..., description="Total number of groups")


class DeviceAssignmentRequest(BaseModel):
    """Schema for assigning device to group."""

    device_id: int = Field(..., description="Device ID to assign")


class DeviceAssignmentResponse(BaseModel):
    """Schema for device assignment response."""

    message: str = Field(..., description="Success message")
    group_id: int = Field(..., description="Group ID")
    device_id: int = Field(..., description="Device ID")
