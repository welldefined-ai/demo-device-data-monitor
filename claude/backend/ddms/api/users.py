"""User management endpoints."""

import logging

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from ddms.api.deps import AdminUser, CurrentUser, DbSession
from ddms.core.security import hash_password
from ddms.db.models import User
from ddms.schemas.user import UserCreate, UserListResponse, UserResponse, UserUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("", response_model=UserListResponse)
async def list_users(
    session: DbSession,
    current_user: AdminUser,  # Only admin or owner can list users
) -> UserListResponse:
    """
    List all users in the system.

    Args:
        session: Database session
        current_user: Current authenticated user (must be admin or owner)

    Returns:
        List of all users
    """
    result = await session.execute(select(User))
    users = result.scalars().all()

    logger.info(f"User {current_user.username} listed all users ({len(users)} total)")

    return UserListResponse(
        users=[UserResponse.model_validate(user) for user in users],
        total=len(users),
    )


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    session: DbSession,
    current_user: AdminUser,  # Only admin or owner can create users
) -> UserResponse:
    """
    Create a new user.

    Args:
        user_data: User creation data
        session: Database session
        current_user: Current authenticated user (must be admin or owner)

    Returns:
        Created user information

    Raises:
        HTTPException: If username already exists or validation fails
    """
    # Hash the password
    password_hash = hash_password(user_data.password)

    # Create new user
    new_user = User(
        username=user_data.username,
        password_hash=password_hash,
        role=user_data.role,
        language_preference=user_data.language_preference,
    )

    try:
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        logger.info(
            f"User {current_user.username} created new user: {new_user.username} "
            f"(role: {new_user.role})"
        )

        return UserResponse.model_validate(new_user)

    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{user_data.username}' already exists",
        ) from None


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    session: DbSession,
    current_user: CurrentUser,
) -> UserResponse:
    """
    Update an existing user.

    Users can update their own information.
    Admins and owners can update any user.

    Args:
        user_id: ID of user to update
        user_data: Update data
        session: Database session
        current_user: Current authenticated user

    Returns:
        Updated user information

    Raises:
        HTTPException: If user not found or permission denied
    """
    # Fetch user to update
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check permissions: users can update themselves, admins can update anyone
    if user.id != current_user.id and not current_user.can_manage_users():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own information",
        )

    # Apply updates
    if user_data.username is not None:
        user.username = user_data.username

    if user_data.password is not None:
        user.password_hash = hash_password(user_data.password)

    if user_data.role is not None:
        # Only admins can change roles
        if not current_user.can_manage_users():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins and owners can change user roles",
            )
        user.role = user_data.role

    if user_data.language_preference is not None:
        user.language_preference = user_data.language_preference

    try:
        await session.commit()
        await session.refresh(user)

        logger.info(f"User {current_user.username} updated user {user.username} (id: {user.id})")

        return UserResponse.model_validate(user)

    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{user_data.username}' already exists",
        ) from None


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    session: DbSession,
    current_user: AdminUser,  # Only admin or owner can delete users
) -> None:
    """
    Delete a user.

    Prevents deletion of the current user (to avoid locking out).
    Prevents deletion of owner users.

    Args:
        user_id: ID of user to delete
        session: Database session
        current_user: Current authenticated user (must be admin or owner)

    Raises:
        HTTPException: If user not found, trying to delete self, or trying to delete owner
    """
    # Fetch user to delete
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Prevent self-deletion
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account",
        )

    # Prevent deletion of owner users (requirement DDMS-AUTH-021)
    if user.is_owner():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Owner accounts cannot be deleted",
        )

    await session.delete(user)
    await session.commit()

    logger.info(f"User {current_user.username} deleted user {user.username} (id: {user.id})")
