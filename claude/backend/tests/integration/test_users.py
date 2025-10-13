"""Integration tests for user management endpoints."""

from fastapi.testclient import TestClient


def test_list_users_as_owner(client: TestClient, owner_token: str) -> None:
    """Test listing users as owner."""
    response = client.get(
        "/api/users",
        cookies={"access_token": owner_token},
    )

    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    assert "total" in data
    assert data["total"] == 1
    assert data["users"][0]["username"] == "admin"
    assert data["users"][0]["role"] == "owner"


def test_list_users_as_admin(client: TestClient, admin_user, db_session) -> None:
    """Test listing users as admin."""
    # Login as admin
    response = client.post(
        "/api/auth/login",
        json={"username": "admin_user", "password": "admin123"},
    )
    token = response.cookies.get("access_token")

    # List users
    response = client.get(
        "/api/users",
        cookies={"access_token": token},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2  # At least owner and admin


def test_list_users_as_viewer_forbidden(client: TestClient, viewer_user, db_session) -> None:
    """Test that viewers cannot list users."""
    # Login as viewer
    response = client.post(
        "/api/auth/login",
        json={"username": "viewer_user", "password": "viewer123"},
    )
    token = response.cookies.get("access_token")

    # Try to list users
    response = client.get(
        "/api/users",
        cookies={"access_token": token},
    )

    assert response.status_code == 403
    data = response.json()
    assert "Only owners and admins" in data["detail"]


def test_list_users_unauthenticated(client: TestClient) -> None:
    """Test that unauthenticated users cannot list users."""
    response = client.get("/api/users")

    assert response.status_code == 401


def test_create_user_as_owner(client: TestClient, owner_token: str) -> None:
    """Test creating a user as owner."""
    response = client.post(
        "/api/users",
        json={
            "username": "newuser",
            "password": "password123",
            "role": "viewer",
        },
        cookies={"access_token": owner_token},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["role"] == "viewer"
    assert data["language_preference"] == "en-US"
    assert "id" in data
    assert "password_hash" not in data


def test_create_admin_user(client: TestClient, owner_token: str) -> None:
    """Test creating an admin user."""
    response = client.post(
        "/api/users",
        json={
            "username": "new_admin",
            "password": "admin123",
            "role": "admin",
        },
        cookies={"access_token": owner_token},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["role"] == "admin"


def test_create_user_duplicate_username(client: TestClient, owner_token: str) -> None:
    """Test that duplicate usernames are rejected."""
    response = client.post(
        "/api/users",
        json={
            "username": "admin",  # Already exists
            "password": "password123",
            "role": "viewer",
        },
        cookies={"access_token": owner_token},
    )

    assert response.status_code == 400
    data = response.json()
    assert "already exists" in data["detail"]


def test_create_user_as_viewer_forbidden(client: TestClient, viewer_user, db_session) -> None:
    """Test that viewers cannot create users."""
    # Login as viewer
    response = client.post(
        "/api/auth/login",
        json={"username": "viewer_user", "password": "viewer123"},
    )
    token = response.cookies.get("access_token")

    # Try to create user
    response = client.post(
        "/api/users",
        json={
            "username": "newuser",
            "password": "password123",
            "role": "viewer",
        },
        cookies={"access_token": token},
    )

    assert response.status_code == 403


def test_update_own_password(client: TestClient, owner_token: str, db_session) -> None:
    """Test user can update their own password."""
    response = client.patch(
        "/api/users/1",  # Owner user ID
        json={"password": "newpassword123"},
        cookies={"access_token": owner_token},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "admin"

    # Verify new password works
    login_response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "newpassword123"},
    )
    assert login_response.status_code == 200


def test_update_own_language_preference(client: TestClient, owner_token: str) -> None:
    """Test user can update their own language preference."""
    response = client.patch(
        "/api/users/1",
        json={"language_preference": "zh-CN"},
        cookies={"access_token": owner_token},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["language_preference"] == "zh-CN"


def test_update_other_user_as_admin(
    client: TestClient, owner_token: str, viewer_user, db_session
) -> None:
    """Test admin can update other users."""
    response = client.patch(
        f"/api/users/{viewer_user.id}",
        json={"username": "updated_viewer"},
        cookies={"access_token": owner_token},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "updated_viewer"


def test_viewer_cannot_update_others(
    client: TestClient, viewer_user, admin_user, db_session
) -> None:
    """Test viewer cannot update other users."""
    # Login as viewer
    response = client.post(
        "/api/auth/login",
        json={"username": "viewer_user", "password": "viewer123"},
    )
    token = response.cookies.get("access_token")

    # Try to update admin user
    response = client.patch(
        f"/api/users/{admin_user.id}",
        json={"username": "hacked"},
        cookies={"access_token": token},
    )

    assert response.status_code == 403
    data = response.json()
    assert "You can only update your own information" in data["detail"]


def test_viewer_cannot_change_own_role(client: TestClient, viewer_user, db_session) -> None:
    """Test viewer cannot change their own role."""
    # Login as viewer
    response = client.post(
        "/api/auth/login",
        json={"username": "viewer_user", "password": "viewer123"},
    )
    token = response.cookies.get("access_token")

    # Try to change own role
    response = client.patch(
        f"/api/users/{viewer_user.id}",
        json={"role": "admin"},
        cookies={"access_token": token},
    )

    assert response.status_code == 403
    data = response.json()
    assert "Only admins and owners can change user roles" in data["detail"]


def test_admin_can_change_user_roles(
    client: TestClient, owner_token: str, viewer_user, db_session
) -> None:
    """Test admin can change user roles."""
    response = client.patch(
        f"/api/users/{viewer_user.id}",
        json={"role": "admin"},
        cookies={"access_token": owner_token},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "admin"


def test_delete_user_as_owner(
    client: TestClient, owner_token: str, viewer_user, db_session
) -> None:
    """Test deleting a user as owner."""
    response = client.delete(
        f"/api/users/{viewer_user.id}",
        cookies={"access_token": owner_token},
    )

    assert response.status_code == 204

    # Verify user is deleted
    list_response = client.get(
        "/api/users",
        cookies={"access_token": owner_token},
    )
    users = list_response.json()["users"]
    assert not any(u["username"] == "viewer_user" for u in users)


def test_cannot_delete_self(client: TestClient, owner_token: str) -> None:
    """Test user cannot delete their own account."""
    response = client.delete(
        "/api/users/1",  # Owner user ID
        cookies={"access_token": owner_token},
    )

    assert response.status_code == 400
    data = response.json()
    assert "You cannot delete your own account" in data["detail"]


def test_cannot_delete_owner(client: TestClient, admin_user, db_session) -> None:
    """Test that owner accounts cannot be deleted."""
    # Login as admin
    response = client.post(
        "/api/auth/login",
        json={"username": "admin_user", "password": "admin123"},
    )
    token = response.cookies.get("access_token")

    # Try to delete owner
    response = client.delete(
        "/api/users/1",  # Owner user ID
        cookies={"access_token": token},
    )

    assert response.status_code == 400
    data = response.json()
    assert "Owner accounts cannot be deleted" in data["detail"]


def test_viewer_cannot_delete_users(
    client: TestClient, viewer_user, admin_user, db_session
) -> None:
    """Test viewer cannot delete users."""
    # Login as viewer
    response = client.post(
        "/api/auth/login",
        json={"username": "viewer_user", "password": "viewer123"},
    )
    token = response.cookies.get("access_token")

    # Try to delete admin
    response = client.delete(
        f"/api/users/{admin_user.id}",
        cookies={"access_token": token},
    )

    assert response.status_code == 403


def test_update_nonexistent_user(client: TestClient, owner_token: str) -> None:
    """Test updating a non-existent user returns 404."""
    response = client.patch(
        "/api/users/9999",
        json={"username": "newname"},
        cookies={"access_token": owner_token},
    )

    assert response.status_code == 404
    data = response.json()
    assert "User not found" in data["detail"]


def test_delete_nonexistent_user(client: TestClient, owner_token: str) -> None:
    """Test deleting a non-existent user returns 404."""
    response = client.delete(
        "/api/users/9999",
        cookies={"access_token": owner_token},
    )

    assert response.status_code == 404
    data = response.json()
    assert "User not found" in data["detail"]
