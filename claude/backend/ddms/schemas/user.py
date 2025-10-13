"""Pydantic schemas for user management."""

from datetime import datetime

from pydantic import BaseModel, Field

from ddms.db.models import UserRole


class UserBase(BaseModel):
    """Base user schema with common fields."""

    username: str = Field(..., min_length=1, max_length=100, description="Username")
    role: UserRole = Field(default=UserRole.VIEWER, description="User role")
    language_preference: str = Field(
        default="en-US", min_length=2, max_length=10, description="Language preference"
    )


class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: str = Field(..., min_length=5, description="User password (min 5 characters)")


class UserUpdate(BaseModel):
    """Schema for updating an existing user.

    All fields are optional to allow partial updates.
    """

    username: str | None = Field(None, min_length=1, max_length=100, description="Username")
    password: str | None = Field(None, min_length=5, description="New password (min 5 characters)")
    role: UserRole | None = Field(None, description="User role")
    language_preference: str | None = Field(
        None, min_length=2, max_length=10, description="Language preference"
    )


class UserResponse(UserBase):
    """Schema for user response (excludes password_hash)."""

    id: int = Field(..., description="User ID")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic config."""

        from_attributes = True  # Enable ORM mode for SQLAlchemy models


class UserListResponse(BaseModel):
    """Schema for list of users response."""

    users: list[UserResponse] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")
