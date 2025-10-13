from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient


def login(client: TestClient, username: str, password: str) -> dict[str, Any]:
    res = client.post("/api/auth/login", json={"username": username, "password": password})
    return {"status": res.status_code, "json": (res.json() if res.status_code < 500 else None)}


def test_login_me_logout_flow(client: TestClient) -> None:
    # Invalid credentials
    bad = client.post("/api/auth/login", json={"username": "owner", "password": "wrong"})
    assert bad.status_code == 401

    # Default owner (bootstrapped on startup)
    res = client.post("/api/auth/login", json={"username": "owner", "password": "owner"})
    assert res.status_code == 200
    assert "ddms_auth" in res.cookies

    me = client.get("/api/auth/me")
    assert me.status_code == 200
    me_json = me.json()
    assert me_json["username"] == "owner"
    assert me_json["role"] == "owner"

    out = client.post("/api/auth/logout")
    assert out.status_code == 200
    me2 = client.get("/api/auth/me")
    assert me2.status_code == 401


def test_user_rbac_owner_admin_viewer(client: TestClient) -> None:
    # Login as owner
    res = client.post("/api/auth/login", json={"username": "owner", "password": "owner"})
    assert res.status_code == 200

    # Create admin and viewer
    admin = client.post("/api/users/", json={"username": "admin", "password": "secret", "role": "admin"})
    assert admin.status_code == 201, admin.text
    admin_id = admin.json()["id"]

    viewer = client.post("/api/users/", json={"username": "viewer", "password": "secret", "role": "viewer"})
    assert viewer.status_code == 201, viewer.text
    viewer_id = viewer.json()["id"]

    # List users (owner allowed)
    users = client.get("/api/users/")
    assert users.status_code == 200
    names = [u["username"] for u in users.json()]
    assert {"owner", "admin", "viewer"}.issubset(set(names))

    # Logout owner
    client.post("/api/auth/logout")

    # Login as viewer
    res = client.post("/api/auth/login", json={"username": "viewer", "password": "secret"})
    assert res.status_code == 200

    # Viewer cannot list users
    users_forbidden = client.get("/api/users/")
    assert users_forbidden.status_code == 403

    # Viewer can update self
    upd_self = client.patch(f"/api/users/{viewer_id}", json={"password": "newpass"})
    assert upd_self.status_code == 200

    # Viewer cannot update others
    upd_other = client.patch(f"/api/users/{admin_id}", json={"password": "newpass"})
    assert upd_other.status_code == 403

    client.post("/api/auth/logout")

    # Login as admin
    res = client.post("/api/auth/login", json={"username": "admin", "password": "secret"})
    assert res.status_code == 200

    # Admin can list users
    users_ok = client.get("/api/users/")
    assert users_ok.status_code == 200

    # Admin can delete viewer
    del_viewer = client.delete(f"/api/users/{viewer_id}")
    assert del_viewer.status_code == 204

    # Admin cannot delete owner (route forbids any owner deletion)
    del_owner = client.delete("/api/users/1")
    assert del_owner.status_code == 400

