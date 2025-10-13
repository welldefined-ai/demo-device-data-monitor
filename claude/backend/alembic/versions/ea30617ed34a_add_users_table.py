"""add users table

Revision ID: ea30617ed34a
Revises: 40646a8b5999
Create Date: 2025-10-13 19:09:25.037106

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ea30617ed34a'
down_revision: Union[str, None] = '40646a8b5999'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create users table with role-based access control."""
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("username", sa.String(length=100), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "role",
            sa.Enum("owner", "admin", "viewer", name="user_role"),
            nullable=False,
            server_default="viewer",
        ),
        sa.Column(
            "language_preference",
            sa.String(length=10),
            nullable=False,
            server_default="en-US",
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )

    # Create index on username for faster lookups
    op.create_index("ix_users_username", "users", ["username"], unique=True)


def downgrade() -> None:
    """Drop users table."""
    op.drop_index("ix_users_username", table_name="users")
    op.drop_table("users")
    op.execute("DROP TYPE user_role")
