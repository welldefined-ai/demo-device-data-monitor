"""add devices and groups tables

Revision ID: 8004d8f514e1
Revises: 86f0fdb17023
Create Date: 2025-10-14 09:34:22.175169

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8004d8f514e1'
down_revision: Union[str, None] = '86f0fdb17023'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create devices, groups, and group_devices tables."""
    # Create device groups table
    op.create_table(
        "groups",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )
    op.create_index("ix_groups_name", "groups", ["name"])

    # Create devices table
    op.create_table(
        "devices",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("unit", sa.String(length=20), nullable=False),
        sa.Column("sampling_interval", sa.Integer(), nullable=False),
        sa.Column("thresholds", sa.JSON(), nullable=True),
        sa.Column("modbus_config", sa.JSON(), nullable=False),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="offline",
        ),
        sa.Column("last_reading_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )
    op.create_index("ix_devices_name", "devices", ["name"])
    op.create_index("ix_devices_status", "devices", ["status"])

    # Create group_devices junction table
    op.create_table(
        "group_devices",
        sa.Column("group_id", sa.Integer(), sa.ForeignKey("groups.id", ondelete="CASCADE"), nullable=False),
        sa.Column("device_id", sa.Integer(), sa.ForeignKey("devices.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("group_id", "device_id"),
    )
    # Unique constraint on device_id to enforce single-group assignment
    op.create_index("ix_group_devices_device_id", "group_devices", ["device_id"], unique=True)


def downgrade() -> None:
    """Drop devices, groups, and group_devices tables."""
    op.drop_table("group_devices")
    op.drop_index("ix_devices_status", table_name="devices")
    op.drop_index("ix_devices_name", table_name="devices")
    op.drop_table("devices")
    op.drop_index("ix_groups_name", table_name="groups")
    op.drop_table("groups")
