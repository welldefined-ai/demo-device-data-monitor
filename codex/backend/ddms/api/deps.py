from __future__ import annotations

from collections.abc import Callable
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from jose import JWTError
from sqlalchemy.orm import Session

from ddms.core.security import AUTH_COOKIE_NAME, decode_jwt
from ddms.db.models import Role, User
from ddms.db.session import get_session

SessionDep = Annotated[Session, Depends(get_session)]


def get_current_user(
    session: SessionDep, token: str | None = Cookie(default=None, alias=AUTH_COOKIE_NAME)
) -> User:
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = decode_jwt(token)
    except JWTError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        ) from err

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
        )

    user = session.get(User, int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_roles(*allowed: Role) -> Callable[[User], User]:
    def _dep(user: Annotated[User, Depends(get_current_user)]) -> User:
        if user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )
        return user

    return _dep

# Convenience alias for routes
UserDep = Annotated[User, Depends(get_current_user)]
