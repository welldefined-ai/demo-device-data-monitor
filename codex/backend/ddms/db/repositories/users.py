from __future__ import annotations

from typing import Iterable, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from ddms.db.models import Role, User


def get_by_username(session: Session, username: str) -> Optional[User]:
    stmt = select(User).where(User.username == username)
    return session.scalar(stmt)


def list_users(session: Session) -> Iterable[User]:
    stmt = select(User).order_by(User.id.asc())
    return session.scalars(stmt).all()


def create_user(session: Session, *, username: str, password_hash: str, role: Role, language_preference: str = "en") -> User:
    user = User(username=username, password_hash=password_hash, role=role, language_preference=language_preference)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def update_user(
    session: Session,
    user: User,
    *,
    username: Optional[str] = None,
    password_hash: Optional[str] = None,
    language_preference: Optional[str] = None,
) -> User:
    if username is not None:
        user.username = username
    if password_hash is not None:
        user.password_hash = password_hash
    if language_preference is not None:
        user.language_preference = language_preference
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def delete_user(session: Session, user: User) -> None:
    session.delete(user)
    session.commit()

