"""Unit tests for security utilities."""

from datetime import timedelta

from ddms.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_password() -> None:
    """Test password hashing."""
    password = "testpassword123"
    hashed = hash_password(password)

    # Hash should be different from original password
    assert hashed != password
    # Hash should be a string
    assert isinstance(hashed, str)
    # Hash should contain argon2 identifier
    assert "$argon2id$" in hashed


def test_verify_password_correct() -> None:
    """Test password verification with correct password."""
    password = "testpassword123"
    hashed = hash_password(password)

    # Should return True for correct password
    assert verify_password(password, hashed) is True


def test_verify_password_incorrect() -> None:
    """Test password verification with incorrect password."""
    password = "testpassword123"
    wrong_password = "wrongpassword"
    hashed = hash_password(password)

    # Should return False for incorrect password
    assert verify_password(wrong_password, hashed) is False


def test_create_access_token() -> None:
    """Test JWT token creation."""
    data = {"user_id": 1, "username": "testuser"}
    token = create_access_token(data)

    # Token should be a string
    assert isinstance(token, str)
    # Token should have 3 parts (header.payload.signature)
    assert len(token.split(".")) == 3


def test_create_access_token_with_expiry() -> None:
    """Test JWT token creation with custom expiry."""
    data = {"user_id": 1, "username": "testuser"}
    expires = timedelta(minutes=30)
    token = create_access_token(data, expires_delta=expires)

    # Token should be created successfully
    assert isinstance(token, str)
    assert len(token.split(".")) == 3


def test_decode_access_token_valid() -> None:
    """Test JWT token decoding with valid token."""
    data = {"user_id": 1, "username": "testuser"}
    token = create_access_token(data)

    # Should decode successfully
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["user_id"] == 1
    assert decoded["username"] == "testuser"
    # Should contain exp claim
    assert "exp" in decoded


def test_decode_access_token_invalid() -> None:
    """Test JWT token decoding with invalid token."""
    invalid_token = "invalid.token.here"

    # Should return None for invalid token
    decoded = decode_access_token(invalid_token)
    assert decoded is None


def test_decode_access_token_expired() -> None:
    """Test JWT token decoding with expired token."""
    data = {"user_id": 1, "username": "testuser"}
    # Create token that expires immediately
    token = create_access_token(data, expires_delta=timedelta(seconds=-1))

    # Should return None for expired token
    decoded = decode_access_token(token)
    assert decoded is None
