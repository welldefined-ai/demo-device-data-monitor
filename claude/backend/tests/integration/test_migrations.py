"""Tests for Alembic database migrations."""

import pytest
from alembic.config import Config
from sqlalchemy import create_engine, text

from alembic import command


@pytest.fixture
def alembic_config() -> Config:
    """Create Alembic configuration."""
    config = Config("alembic.ini")
    return config


def test_migrations_upgrade_head(alembic_config: Config) -> None:
    """Test that migrations can be applied to an empty database."""
    # This test verifies that `alembic upgrade head` runs without errors
    # For Iteration 0, we have an empty migration which should succeed
    try:
        command.upgrade(alembic_config, "head")
    except Exception as e:
        pytest.fail(f"Migration upgrade failed: {e}")


def test_migrations_downgrade_base(alembic_config: Config) -> None:
    """Test that migrations can be rolled back."""
    try:
        # First upgrade to head
        command.upgrade(alembic_config, "head")
        # Then downgrade to base
        command.downgrade(alembic_config, "base")
    except Exception as e:
        pytest.fail(f"Migration downgrade failed: {e}")


def test_database_connection() -> None:
    """Test database connection with migrations applied."""
    from ddms.core.config import settings

    # Create a synchronous engine for testing
    sync_url = str(settings.database_url).replace("postgresql+asyncpg://", "postgresql://")
    engine = create_engine(sync_url)

    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.scalar() == 1
    except Exception as e:
        pytest.fail(f"Database connection test failed: {e}")
    finally:
        engine.dispose()
