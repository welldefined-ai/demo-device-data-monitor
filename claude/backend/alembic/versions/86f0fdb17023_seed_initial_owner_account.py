"""seed initial owner account

Revision ID: 86f0fdb17023
Revises: ea30617ed34a
Create Date: 2025-10-13 19:10:25.451695

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '86f0fdb17023'
down_revision: Union[str, None] = 'ea30617ed34a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Seed the database with an initial owner account.

    Default credentials:
        Username: admin
        Password: admin
    """
    # Only seed if users table is empty
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT COUNT(*) FROM users"))
    count = result.scalar()

    if count == 0:
        # Insert initial owner account
        # Password hash for 'admin' using argon2
        op.execute(
            sa.text(
                """
                INSERT INTO users (username, password_hash, role, language_preference)
                VALUES (
                    'admin',
                    '$argon2id$v=19$m=65536,t=3,p=4$/Tz/58OUk58vaCUcnlY+Aw$ua1M61E6e9GkTI/Nv4JfDi6bBLwZehcxfWDNb/yvuxY',
                    'owner',
                    'en-US'
                )
                """
            )
        )


def downgrade() -> None:
    """Remove the seeded owner account."""
    # Delete the default admin user if it exists
    op.execute(
        sa.text("DELETE FROM users WHERE username = 'admin' AND role = 'owner'")
    )
