from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ddms.core.config import Settings
from ddms.core.security import hash_password
from ddms.db.models import Role, User

logger = logging.getLogger(__name__)


def ensure_owner_account(session: Session, settings: Settings) -> None:
    """Ensure a single owner account exists on an empty database.

    Uses configured default credentials when creating the owner.
    Safe to run multiple times (no-op if owner exists).
    """
    try:
        exists = session.scalar(select(User.id).where(User.role == Role.OWNER).limit(1))
        if exists:
            return
        owner = User(
            username=settings.owner_default_username,
            password_hash=hash_password(settings.owner_default_password),
            role=Role.OWNER,
            language_preference="en",
        )
        session.add(owner)
        session.commit()
        logger.info("Bootstrap: created default owner user '%s'", settings.owner_default_username)
    except SQLAlchemyError:
        # Likely the users table does not exist yet; ignore and continue.
        session.rollback()
        logger.debug("Bootstrap skipped: users table missing or DB unavailable")

