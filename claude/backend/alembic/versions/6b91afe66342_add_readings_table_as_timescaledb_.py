"""add readings table as timescaledb hypertable

Revision ID: 6b91afe66342
Revises: 8004d8f514e1
Create Date: 2025-10-14 12:36:28.224603

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6b91afe66342'
down_revision: Union[str, None] = '8004d8f514e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create readings table and convert to TimescaleDB hypertable."""
    # Create readings table with composite primary key
    op.create_table(
        "readings",
        sa.Column("device_id", sa.Integer(), sa.ForeignKey("devices.id", ondelete="CASCADE"), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("device_id", "timestamp"),
    )

    # Create index on (device_id, timestamp) for efficient queries
    op.create_index("ix_readings_device_timestamp", "readings", ["device_id", "timestamp"])

    # Convert to TimescaleDB hypertable
    # Note: This requires TimescaleDB extension to be enabled in PostgreSQL
    op.execute(
        """
        SELECT create_hypertable('readings', 'timestamp', if_not_exists => TRUE);
        """
    )


def downgrade() -> None:
    """Drop readings table."""
    op.drop_index("ix_readings_device_timestamp", table_name="readings")
    op.drop_table("readings")
