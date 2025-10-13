"""Pydantic schemas for authentication."""

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Request schema for user login."""

    username: str = Field(..., min_length=1, max_length=100, description="Username")
    password: str = Field(..., min_length=1, description="Password")


class TokenResponse(BaseModel):
    """Response schema for successful authentication.

    Note: JWT token is returned in HttpOnly cookie, not in response body.
    This schema confirms authentication success.
    """

    message: str = Field(default="Login successful", description="Success message")
    username: str = Field(..., description="Authenticated username")
    role: str = Field(..., description="User role")
