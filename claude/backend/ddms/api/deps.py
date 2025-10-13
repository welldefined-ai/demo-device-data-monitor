"""FastAPI dependencies for database sessions and authentication."""

from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ddms.core.security import decode_access_token
from ddms.db.base import get_async_session
from ddms.db.models import User

# Type alias for database session dependency
DbSession = Annotated[AsyncSession, Depends(get_async_session)]


async def get_current_user(
    session: DbSession,
    access_token: str | None = Cookie(default=None),
) -> User:
    """
    Get the currently authenticated user from JWT token in cookie.

    Args:
        session: Database session
        access_token: JWT token from HttpOnly cookie

    Returns:
        Current authenticated user

    Raises:
        HTTPException: If token is missing, invalid, or user not found
    """
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    # Decode and verify JWT token
    payload = decode_access_token(access_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    # Extract user ID from token
    user_id: int | None = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    # Fetch user from database
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


# Type alias for current user dependency
CurrentUser = Annotated[User, Depends(get_current_user)]


async def require_owner(current_user: CurrentUser) -> User:
    """
    Require that the current user has owner role.

    Args:
        current_user: Currently authenticated user

    Returns:
        Current user if they have owner role

    Raises:
        HTTPException: If user does not have owner role
    """
    if not current_user.is_owner():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners can perform this action",
        )
    return current_user


async def require_admin(current_user: CurrentUser) -> User:
    """
    Require that the current user has owner or admin role.

    Args:
        current_user: Currently authenticated user

    Returns:
        Current user if they have owner or admin role

    Raises:
        HTTPException: If user does not have sufficient permissions
    """
    if not current_user.can_manage_users():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners and admins can perform this action",
        )
    return current_user


async def require_modify_permissions(current_user: CurrentUser) -> User:
    """
    Require that the current user has permissions to modify data.

    Args:
        current_user: Currently authenticated user

    Returns:
        Current user if they have modify permissions

    Raises:
        HTTPException: If user does not have sufficient permissions
    """
    if not current_user.can_modify_data():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify data",
        )
    return current_user


# Type aliases for role-based dependencies
OwnerUser = Annotated[User, Depends(require_owner)]
AdminUser = Annotated[User, Depends(require_admin)]
ModifyUser = Annotated[User, Depends(require_modify_permissions)]
