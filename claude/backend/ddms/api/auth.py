"""Authentication endpoints."""

import logging

from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import select

from ddms.api.deps import CurrentUser, DbSession
from ddms.core.security import create_access_token, verify_password
from ddms.db.models import User
from ddms.schemas.auth import LoginRequest, TokenResponse
from ddms.schemas.user import UserResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest,
    response: Response,
    session: DbSession,
) -> TokenResponse:
    """
    Authenticate user and return JWT token in HttpOnly cookie.

    Args:
        credentials: Login credentials (username and password)
        response: FastAPI response object for setting cookies
        session: Database session

    Returns:
        Token response with user info

    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by username
    result = await session.execute(select(User).where(User.username == credentials.username))
    user = result.scalar_one_or_none()

    # Verify user exists and password is correct
    if user is None or not verify_password(credentials.password, user.password_hash):
        logger.warning(f"Failed login attempt for username: {credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    # Create JWT token
    token = create_access_token(data={"user_id": user.id, "username": user.username})

    # Set HttpOnly cookie with the token
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,  # Prevent JavaScript access
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",  # CSRF protection
        max_age=60 * 60 * 24,  # 24 hours
    )

    logger.info(f"User logged in: {user.username} (role: {user.role})")

    return TokenResponse(
        message="Login successful",
        username=user.username,
        role=user.role.value,
    )


@router.post("/logout")
async def logout(response: Response) -> dict[str, str]:
    """
    Log out user by clearing the authentication cookie.

    Args:
        response: FastAPI response object for clearing cookies

    Returns:
        Success message
    """
    response.delete_cookie(key="access_token")
    logger.info("User logged out")
    return {"message": "Logout successful"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: CurrentUser) -> UserResponse:
    """
    Get current authenticated user information.

    Args:
        current_user: Current authenticated user from dependency

    Returns:
        User information (excluding password hash)
    """
    return UserResponse.model_validate(current_user)
