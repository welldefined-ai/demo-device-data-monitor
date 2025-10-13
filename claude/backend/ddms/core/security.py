"""Security utilities for authentication and authorization."""

from datetime import UTC, datetime, timedelta
from typing import Any, cast

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from ddms.core.config import settings

# Initialize Argon2 password hasher
ph = PasswordHasher()

# JWT Configuration
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours


def hash_password(password: str) -> str:
    """
    Hash a password using Argon2.

    Args:
        password: Plain text password to hash

    Returns:
        Hashed password string
    """
    return ph.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        password: Plain text password to verify
        password_hash: Hashed password to compare against

    Returns:
        True if password matches, False otherwise
    """
    try:
        ph.verify(password_hash, password)
        return True
    except VerifyMismatchError:
        return False


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Dictionary of claims to include in the token
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any] | None:
    """
    Decode and verify a JWT access token.

    Args:
        token: JWT token string to decode

    Returns:
        Dictionary of token claims if valid, None if invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        return cast(dict[str, Any], payload)
    except jwt.ExpiredSignatureError:
        # Token has expired
        return None
    except jwt.InvalidTokenError:
        # Token is invalid
        return None
