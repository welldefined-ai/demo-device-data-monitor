"""SQLAlchemy database models."""

import enum
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ddms.db.base import Base


class UserRole(str, enum.Enum):
    """User role enumeration for role-based access control."""

    OWNER = "owner"
    ADMIN = "admin"
    VIEWER = "viewer"


class User(Base):
    """User model for authentication and authorization."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(
            UserRole,
            name="user_role",
            native_enum=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=UserRole.VIEWER,
    )
    language_preference: Mapped[str] = mapped_column(String(10), nullable=False, default="en-US")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"

    def is_owner(self) -> bool:
        """Check if user has owner role."""
        return self.role == UserRole.OWNER

    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.role == UserRole.ADMIN

    def is_viewer(self) -> bool:
        """Check if user has viewer role."""
        return self.role == UserRole.VIEWER

    def can_manage_users(self) -> bool:
        """Check if user can manage other users."""
        return self.role in (UserRole.OWNER, UserRole.ADMIN)

    def can_modify_data(self) -> bool:
        """Check if user can create, edit, or delete data."""
        return self.role in (UserRole.OWNER, UserRole.ADMIN)


class Group(Base):
    """Device group model for organizing monitoring devices."""

    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    devices: Mapped[list["Device"]] = relationship(
        "Device", secondary="group_devices", back_populates="groups"
    )

    def __repr__(self) -> str:
        """String representation of Group."""
        return f"<Group(id={self.id}, name='{self.name}')>"


class Device(Base):
    """Device model for monitoring devices."""

    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    sampling_interval: Mapped[int] = mapped_column(Integer, nullable=False)
    thresholds: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    modbus_config: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="offline", index=True
    )
    last_reading_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    groups: Mapped[list[Group]] = relationship(
        "Group", secondary="group_devices", back_populates="devices"
    )

    def __repr__(self) -> str:
        """String representation of Device."""
        return f"<Device(id={self.id}, name='{self.name}', status='{self.status}')>"


class GroupDevice(Base):
    """Association table for group-device many-to-many relationship."""

    __tablename__ = "group_devices"

    group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True
    )
    device_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("devices.id", ondelete="CASCADE"), primary_key=True, unique=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    def __repr__(self) -> str:
        """String representation of GroupDevice."""
        return f"<GroupDevice(group_id={self.group_id}, device_id={self.device_id})>"
