"""SQLAlchemy database models."""

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

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
