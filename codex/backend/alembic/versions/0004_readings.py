"""Add readings table for time-series data

Revision ID: 0004_readings
Revises: 0003_devices_groups
Create Date: 2025-10-14 00:00:01
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0004_readings"
down_revision = "0003_devices_groups"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "readings",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
    )
    op.create_index("ix_readings_device_id", "readings", ["device_id"], unique=False)
    op.create_index(
        "ix_readings_device_ts",
        "readings",
        ["device_id", "timestamp"],
        unique=False,
    )
    # TimescaleDB hypertable creation is intentionally skipped here to avoid
    # failures with primary key uniqueness constraints in dev environments.
    # A follow-up migration can convert the table when production constraints
    # and permissions allow it.


def downgrade() -> None:
    op.drop_index("ix_readings_device_ts", table_name="readings")
    op.drop_index("ix_readings_device_id", table_name="readings")
    op.drop_table("readings")
