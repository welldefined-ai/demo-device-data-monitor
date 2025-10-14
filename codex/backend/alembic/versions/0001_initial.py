"""Initial empty schema

Revision ID: 0001_initial
Revises:
Create Date: 2025-10-12 12:45:00
"""
from __future__ import annotations

from alembic import op  # noqa: F401
import sqlalchemy as sa  # noqa: F401


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Initial upgrade has no-op to establish baseline."""
    pass


def downgrade() -> None:
    """Downgrade reverts initial baseline (no-op)."""
    pass
