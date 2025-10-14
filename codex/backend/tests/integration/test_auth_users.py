from __future__ import annotations

from http import HTTPStatus
from typing import Any

from fastapi.testclient import TestClient


def login(client: TestClient, username: str, password: str) -> dict[str, Any]:
    res = client.post("/api/auth/login", json={"username": username, "password": password})
    return {
        "status": res.status_code,
        "json": (res.json() if res.status_code < HTTPStatus.INTERNAL_SERVER_ERROR else None),
    }


def test_login_me_logout_flow(client: TestClient) -> None:
    # Invalid credentials
    bad = client.post("/api/auth/login", json={"username": "owner", "password": "wrong"})
    assert bad.status_code == HTTPStatus.UNAUTHORIZED

    # Default owner (bootstrapped on startup)
    res = client.post("/api/auth/login", json={"username": "owner", "password": "owner"})
    assert res.status_code == HTTPStatus.OK
    assert "ddms_auth" in res.cookies

    me = client.get("/api/auth/me")
    assert me.status_code == HTTPStatus.OK
    me_json = me.json()
    assert me_json["username"] == "owner"
    assert me_json["role"] == "owner"

    out = client.post("/api/auth/logout")
    assert out.status_code == HTTPStatus.OK
    me2 = client.get("/api/auth/me")
    assert me2.status_code == HTTPStatus.UNAUTHORIZED


def test_user_rbac_owner_admin_viewer(client: TestClient) -> None:
    # Login as owner
    res = client.post("/api/auth/login", json={"username": "owner", "password": "owner"})
    assert res.status_code == HTTPStatus.OK

    # Create admin and viewer
    admin = client.post(
        "/api/users/",
        json={"username": "adminA", "password": "secret", "role": "admin"},
    )
    assert admin.status_code == HTTPStatus.CREATED, admin.text
    admin_id = admin.json()["id"]

    viewer = client.post(
        "/api/users/",
        json={"username": "viewer1", "password": "secret", "role": "viewer"},
    )
    assert viewer.status_code == HTTPStatus.CREATED, viewer.text
    viewer_id = viewer.json()["id"]

    # List users (owner allowed)
    users = client.get("/api/users/")
    assert users.status_code == HTTPStatus.OK
    names = [u["username"] for u in users.json()]
    assert {"owner", "adminA", "viewer1"}.issubset(set(names))

    # Logout owner
    client.post("/api/auth/logout")

    # Login as viewer
    res = client.post("/api/auth/login", json={"username": "viewer1", "password": "secret"})
    assert res.status_code == HTTPStatus.OK

    # Viewer cannot list users
    users_forbidden = client.get("/api/users/")
    assert users_forbidden.status_code == HTTPStatus.FORBIDDEN

    # Viewer can update self
    upd_self = client.patch(f"/api/users/{viewer_id}", json={"password": "newpass"})
    assert upd_self.status_code == HTTPStatus.OK

    # Viewer cannot update others
    upd_other = client.patch(f"/api/users/{admin_id}", json={"password": "newpass"})
    assert upd_other.status_code == HTTPStatus.FORBIDDEN

    client.post("/api/auth/logout")

    # Login as admin
    res = client.post("/api/auth/login", json={"username": "adminA", "password": "secret"})
    assert res.status_code == HTTPStatus.OK

    # Admin can list users
    users_ok = client.get("/api/users/")
    assert users_ok.status_code == HTTPStatus.OK

    # Admin can delete viewer
    del_viewer = client.delete(f"/api/users/{viewer_id}")
    assert del_viewer.status_code == HTTPStatus.OK

    # Admin cannot delete owner (route forbids any owner deletion)
    del_owner = client.delete("/api/users/1")
    assert del_owner.status_code == HTTPStatus.BAD_REQUEST


def test_admin_create_user_and_uniqueness_and_update(client: TestClient) -> None:
    # Owner creates an admin
    res = client.post("/api/auth/login", json={"username": "owner", "password": "owner"})
    assert res.status_code == HTTPStatus.OK

    admin2 = client.post(
        "/api/users/",
        json={"username": "adminB", "password": "secret", "role": "admin"},
    )
    assert admin2.status_code == HTTPStatus.CREATED, admin2.text

    # Switch to admin2
    client.post("/api/auth/logout")
    res = client.post("/api/auth/login", json={"username": "adminB", "password": "secret"})
    assert res.status_code == HTTPStatus.OK

    # Create two viewers
    view_a = client.post(
        "/api/users/",
        json={"username": "view_a1", "password": "pw", "role": "viewer"},
    )
    assert view_a.status_code == HTTPStatus.CREATED, view_a.text
    _view_a_id = view_a.json()["id"]

    view_b = client.post(
        "/api/users/",
        json={"username": "view_b1", "password": "pw", "role": "viewer"},
    )
    assert view_b.status_code == HTTPStatus.CREATED, view_b.text
    view_b_id = view_b.json()["id"]

    # Duplicate create should conflict
    dup = client.post(
        "/api/users/",
        json={"username": "view_b1", "password": "pw", "role": "viewer"},
    )
    assert dup.status_code == HTTPStatus.CONFLICT

    # Update to existing username should conflict
    upd_conflict = client.patch(
        f"/api/users/{view_b_id}", json={"username": "view_a1"}
    )
    assert upd_conflict.status_code == HTTPStatus.CONFLICT

    # Happy path: rename to a unique username
    upd_ok = client.patch(
        f"/api/users/{view_b_id}", json={"username": "view_b1_renamed"}
    )
    assert upd_ok.status_code == HTTPStatus.OK
    assert upd_ok.json()["username"] == "view_b1_renamed"


def test_viewer_cannot_create_and_admin_delete_missing_and_logout_cookie(
    client: TestClient,
) -> None:
    # Owner creates a viewer
    res = client.post("/api/auth/login", json={"username": "owner", "password": "owner"})
    assert res.status_code == HTTPStatus.OK
    viewer = client.post(
        "/api/users/",
        json={"username": "view_c1", "password": "pw", "role": "viewer"},
    )
    assert viewer.status_code == HTTPStatus.CREATED, viewer.text
    client.post("/api/auth/logout")

    # Viewer cannot create users
    res = client.post("/api/auth/login", json={"username": "view_c1", "password": "pw"})
    assert res.status_code == HTTPStatus.OK
    forbidden = client.post(
        "/api/users/", json={"username": "should_fail", "password": "pw", "role": "viewer"}
    )
    assert forbidden.status_code == HTTPStatus.FORBIDDEN

    # Logout clears cookie
    out = client.post("/api/auth/logout")
    assert out.status_code == HTTPStatus.OK
    set_cookie = out.headers.get("set-cookie", "")
    assert "ddms_auth=" in set_cookie and "Max-Age=0" in set_cookie
    me = client.get("/api/auth/me")
    assert me.status_code == HTTPStatus.UNAUTHORIZED

    # Admin delete missing user id returns 404
    client.post("/api/auth/logout")
    res = client.post("/api/auth/login", json={"username": "owner", "password": "owner"})
    assert res.status_code == HTTPStatus.OK
    admin3 = client.post(
        "/api/users/",
        json={"username": "adminC", "password": "secret", "role": "admin"},
    )
    assert admin3.status_code == HTTPStatus.CREATED
    client.post("/api/auth/logout")
    res = client.post("/api/auth/login", json={"username": "adminC", "password": "secret"})
    assert res.status_code == HTTPStatus.OK
    missing = client.delete("/api/users/999999")
    assert missing.status_code == HTTPStatus.NOT_FOUND
