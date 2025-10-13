"""Create users table

Revision ID: 0002_users
Revises: 0001_initial
Create Date: 2025-10-13 00:00:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0002_users"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("password_hash", sa.String(length=256), nullable=False),
        sa.Column("role", sa.Enum("owner", "admin", "viewer", name="userrole"), nullable=False),
        sa.Column("language_preference", sa.String(length=8), nullable=False, server_default="en"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("username", name="uq_users_username"),
    )
    op.create_index("ix_users_username", "users", ["username"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_users_username", table_name="users")
    op.drop_table("users")
    # Note: Enum type is dropped automatically by PostgreSQL if unused; if needed:
    try:
        sa.Enum(name="userrole").drop(op.get_bind(), checkfirst=True)  # type: ignore[arg-type]
    except Exception:
        pass

