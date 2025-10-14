from __future__ import annotations

from http import HTTPStatus

from fastapi.testclient import TestClient


def login_owner(client: TestClient) -> None:
    res = client.post("/api/auth/login", json={"username": "owner", "password": "owner"})
    assert res.status_code == HTTPStatus.OK


def test_devices_crud_and_groups(client: TestClient) -> None:
    login_owner(client)

    # Create device
    d1 = client.post(
        "/api/devices/",
        json={
            "name": "devA",
            "description": "",
            "unit": "°C",
            "sampling_interval": 30,
            "thresholds": {"warning": 70, "critical": 90},
            "modbus_config": {"type": "tcp", "host": "127.0.0.1", "port": 1502},
        },
    )
    assert d1.status_code == HTTPStatus.CREATED, d1.text
    dev_id = d1.json()["id"]

    # Get
    g = client.get(f"/api/devices/{dev_id}")
    assert g.status_code == HTTPStatus.OK

    # Update
    u = client.patch(f"/api/devices/{dev_id}", json={"unit": "C"})
    assert u.status_code == HTTPStatus.OK
    assert u.json()["unit"] == "C"

    # List
    lst = client.get("/api/devices/")
    assert lst.status_code == HTTPStatus.OK
    assert any(d["name"] == "devA" for d in lst.json())

    # Create group
    grp = client.post("/api/groups/", json={"name": "Grp1", "description": ""})
    assert grp.status_code == HTTPStatus.CREATED, grp.text
    gid = grp.json()["id"]

    # Assign device to group
    asg = client.post(f"/api/groups/{gid}/devices/{dev_id}")
    assert asg.status_code == HTTPStatus.OK

    # Reassign device to another group enforces single-group (by replacing mapping)
    grp2 = client.post("/api/groups/", json={"name": "Grp2", "description": ""})
    assert grp2.status_code == HTTPStatus.CREATED
    gid2 = grp2.json()["id"]
    asg2 = client.post(f"/api/groups/{gid2}/devices/{dev_id}")
    assert asg2.status_code == HTTPStatus.OK

    # Unassign
    un = client.delete(f"/api/groups/{gid2}/devices/{dev_id}")
    assert un.status_code == HTTPStatus.OK

    # Delete device
    dd = client.delete(f"/api/devices/{dev_id}")
    assert dd.status_code == HTTPStatus.OK


def test_device_name_conflict(client: TestClient) -> None:
    login_owner(client)
    d1 = client.post(
        "/api/devices/",
        json={
            "name": "devDup",
            "description": "",
            "unit": "bar",
            "sampling_interval": 10,
            "thresholds": {},
            "modbus_config": {},
        },
    )
    assert d1.status_code == HTTPStatus.CREATED, d1.text
    d2 = client.post(
        "/api/devices/",
        json={
            "name": "devDup",
            "description": "",
            "unit": "bar",
            "sampling_interval": 10,
            "thresholds": {},
            "modbus_config": {},
        },
    )
    assert d2.status_code == HTTPStatus.CONFLICT


def test_devices_404s(client: TestClient) -> None:
    login_owner(client)
    missing = 999999
    g = client.get(f"/api/devices/{missing}")
    assert g.status_code == HTTPStatus.NOT_FOUND
    p = client.patch(f"/api/devices/{missing}", json={"unit": "X"})
    assert p.status_code == HTTPStatus.NOT_FOUND
    d = client.delete(f"/api/devices/{missing}")
    assert d.status_code == HTTPStatus.NOT_FOUND


def test_groups_404s(client: TestClient) -> None:
    login_owner(client)
    # Missing group delete
    mg = client.delete("/api/groups/999999")
    assert mg.status_code == HTTPStatus.NOT_FOUND
    # Create valid device and group, then test missing counterpart
    dev = client.post(
        "/api/devices/",
        json={
            "name": "devX",
            "description": "",
            "unit": "rpm",
            "sampling_interval": 5,
            "thresholds": {},
            "modbus_config": {},
        },
    )
    assert dev.status_code == HTTPStatus.CREATED
    dev_id = dev.json()["id"]
    grp = client.post("/api/groups/", json={"name": "GrpX", "description": ""})
    assert grp.status_code == HTTPStatus.CREATED
    grp_id = grp.json()["id"]
    # Missing device for assign
    asg_missing_device = client.post(f"/api/groups/{grp_id}/devices/999999")
    assert asg_missing_device.status_code == HTTPStatus.NOT_FOUND
    # Missing group for assign
    asg_missing_group = client.post(f"/api/groups/999999/devices/{dev_id}")
    assert asg_missing_group.status_code == HTTPStatus.NOT_FOUND
