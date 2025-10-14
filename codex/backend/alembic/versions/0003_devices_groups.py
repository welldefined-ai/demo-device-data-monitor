"""Add devices, groups, and group_devices tables

Revision ID: 0003_devices_groups
Revises: 0002_users
Create Date: 2025-10-14 00:00:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0003_devices_groups"
down_revision = "0002_users"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "devices",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=128), nullable=False, unique=True),
        sa.Column("description", sa.String(length=512), nullable=False, server_default=""),
        sa.Column("unit", sa.String(length=32), nullable=False, server_default=""),
        sa.Column("sampling_interval", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("thresholds", sa.String(), nullable=False, server_default='{"warning": null, "critical": null}'),
        sa.Column("modbus_config", sa.String(), nullable=False, server_default='{}'),
        sa.Column("status", sa.Enum("offline", "online", "error", name="devicestatus"), nullable=False, server_default="offline"),
        sa.Column("last_reading_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_devices_name", "devices", ["name"], unique=True)

    op.create_table(
        "groups",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=128), nullable=False, unique=True),
        sa.Column("description", sa.String(length=512), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_groups_name", "groups", ["name"], unique=True)

    op.create_table(
        "group_devices",
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("device_id", sa.Integer(), primary_key=True, autoincrement=False),
    )
    op.create_index("ix_group_devices_group_id", "group_devices", ["group_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_group_devices_group_id", table_name="group_devices")
    op.drop_table("group_devices")
    op.drop_index("ix_groups_name", table_name="groups")
    op.drop_table("groups")
    op.drop_index("ix_devices_name", table_name="devices")
    op.drop_table("devices")
    try:
        sa.Enum(name="devicestatus").drop(op.get_bind(), checkfirst=True)
    except Exception:  # pragma: no cover
        pass

