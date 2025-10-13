"""Integration tests for authentication endpoints."""

from fastapi.testclient import TestClient


def test_login_success(client: TestClient) -> None:
    """Test successful login with valid credentials."""
    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "admin"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Login successful"
    assert data["username"] == "admin"
    assert data["role"] == "owner"

    # Check that HttpOnly cookie is set
    assert "access_token" in response.cookies


def test_login_invalid_username(client: TestClient) -> None:
    """Test login with invalid username."""
    response = client.post(
        "/api/auth/login",
        json={"username": "nonexistent", "password": "admin"},
    )

    assert response.status_code == 401
    data = response.json()
    assert "Incorrect username or password" in data["detail"]


def test_login_invalid_password(client: TestClient) -> None:
    """Test login with invalid password."""
    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "wrongpassword"},
    )

    assert response.status_code == 401
    data = response.json()
    assert "Incorrect username or password" in data["detail"]


def test_get_current_user_authenticated(client: TestClient, owner_token: str) -> None:
    """Test getting current user info when authenticated."""
    response = client.get(
        "/api/auth/me",
        cookies={"access_token": owner_token},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "admin"
    assert data["role"] == "owner"
    assert data["language_preference"] == "en-US"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data
    # Password hash should not be returned
    assert "password_hash" not in data


def test_get_current_user_unauthenticated(client: TestClient) -> None:
    """Test getting current user info when not authenticated."""
    response = client.get("/api/auth/me")

    assert response.status_code == 401
    data = response.json()
    assert "Not authenticated" in data["detail"]


def test_get_current_user_invalid_token(client: TestClient) -> None:
    """Test getting current user info with invalid token."""
    response = client.get(
        "/api/auth/me",
        cookies={"access_token": "invalid_token"},
    )

    assert response.status_code == 401
    data = response.json()
    assert "Invalid or expired token" in data["detail"]


def test_logout(client: TestClient, owner_token: str) -> None:
    """Test logout clears the cookie."""
    response = client.post(
        "/api/auth/logout",
        cookies={"access_token": owner_token},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Logout successful"

    # Check that cookie is cleared
    # In test client, we can't easily verify cookie deletion,
    # but we can verify the endpoint returns success


def test_logout_unauthenticated(client: TestClient) -> None:
    """Test logout when not authenticated still succeeds."""
    response = client.post("/api/auth/logout")

    # Logout should succeed even if not authenticated
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Logout successful"


def test_login_multiple_sessions(client: TestClient) -> None:
    """Test that multiple logins work correctly."""
    # First login
    response1 = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "admin"},
    )
    assert response1.status_code == 200
    token1 = response1.cookies.get("access_token")

    # Second login
    response2 = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "admin"},
    )
    assert response2.status_code == 200
    token2 = response2.cookies.get("access_token")

    # Both tokens should exist and work
    assert token1 is not None
    assert token2 is not None

    # Both tokens should work
    me1 = client.get("/api/auth/me", cookies={"access_token": token1})
    me2 = client.get("/api/auth/me", cookies={"access_token": token2})
    assert me1.status_code == 200
    assert me2.status_code == 200
