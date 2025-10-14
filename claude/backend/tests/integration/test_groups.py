"""Integration tests for group management endpoints."""

from fastapi.testclient import TestClient


def test_list_groups(client: TestClient, owner_token: str) -> None:
    """Test listing groups."""
    response = client.get(
        "/api/groups",
        cookies={"access_token": owner_token},
    )

    assert response.status_code == 200
    data = response.json()
    assert "groups" in data
    assert "total" in data


def test_create_group_as_owner(client: TestClient, owner_token: str) -> None:
    """Test creating a group as owner."""
    group_data = {
        "name": "Tank Sensors",
        "description": "All tank monitoring sensors",
    }

    response = client.post(
        "/api/groups",
        json=group_data,
        cookies={"access_token": owner_token},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Tank Sensors"
    assert data["description"] == "All tank monitoring sensors"
    assert "id" in data


def test_create_group_as_viewer_forbidden(client: TestClient, viewer_user, db_session) -> None:
    """Test that viewers cannot create groups."""
    # Login as viewer
    response = client.post(
        "/api/auth/login",
        json={"username": "viewer_user", "password": "viewer123"},
    )
    token = response.cookies.get("access_token")

    # Try to create group
    response = client.post(
        "/api/groups",
        json={"name": "Test Group"},
        cookies={"access_token": token},
    )

    assert response.status_code == 403


def test_update_group(client: TestClient, owner_token: str) -> None:
    """Test updating a group."""
    # Create group
    create_response = client.post(
        "/api/groups",
        json={"name": "Original Name"},
        cookies={"access_token": owner_token},
    )
    group_id = create_response.json()["id"]

    # Update group
    response = client.patch(
        f"/api/groups/{group_id}",
        json={"name": "Updated Name", "description": "New description"},
        cookies={"access_token": owner_token},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["description"] == "New description"


def test_delete_group(client: TestClient, owner_token: str) -> None:
    """Test deleting a group."""
    # Create group
    create_response = client.post(
        "/api/groups",
        json={"name": "To Delete"},
        cookies={"access_token": owner_token},
    )
    group_id = create_response.json()["id"]

    # Delete group
    response = client.delete(
        f"/api/groups/{group_id}",
        cookies={"access_token": owner_token},
    )

    assert response.status_code == 204


def test_assign_device_to_group(client: TestClient, owner_token: str) -> None:
    """Test assigning a device to a group."""
    # Create device
    device_response = client.post(
        "/api/devices",
        json={
            "name": "Test Device",
            "unit": "°C",
            "sampling_interval": 60,
            "modbus_config": {
                "type": "tcp",
                "host": "localhost",
                "port": 502,
                "register": 1,
                "data_type": "int16",
            },
        },
        cookies={"access_token": owner_token},
    )
    device_id = device_response.json()["id"]

    # Create group
    group_response = client.post(
        "/api/groups",
        json={"name": "Test Group"},
        cookies={"access_token": owner_token},
    )
    group_id = group_response.json()["id"]

    # Assign device to group
    response = client.post(
        f"/api/groups/{group_id}/devices/{device_id}",
        cookies={"access_token": owner_token},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Device assigned to group successfully"
    assert data["group_id"] == group_id
    assert data["device_id"] == device_id


def test_single_group_constraint(client: TestClient, owner_token: str) -> None:
    """Test that a device can only be assigned to one group."""
    # Create device
    device_response = client.post(
        "/api/devices",
        json={
            "name": "Single Group Device",
            "unit": "bar",
            "sampling_interval": 30,
            "modbus_config": {
                "type": "tcp",
                "host": "localhost",
                "port": 502,
                "register": 1,
                "data_type": "int16",
            },
        },
        cookies={"access_token": owner_token},
    )
    device_id = device_response.json()["id"]

    # Create first group and assign
    group1_response = client.post(
        "/api/groups",
        json={"name": "Group 1"},
        cookies={"access_token": owner_token},
    )
    group1_id = group1_response.json()["id"]

    assign1_response = client.post(
        f"/api/groups/{group1_id}/devices/{device_id}",
        cookies={"access_token": owner_token},
    )
    assert assign1_response.status_code == 200

    # Create second group and try to assign (should fail)
    group2_response = client.post(
        "/api/groups",
        json={"name": "Group 2"},
        cookies={"access_token": owner_token},
    )
    group2_id = group2_response.json()["id"]

    assign2_response = client.post(
        f"/api/groups/{group2_id}/devices/{device_id}",
        cookies={"access_token": owner_token},
    )

    assert assign2_response.status_code == 400
    data = assign2_response.json()
    assert "already assigned" in data["detail"].lower()


def test_remove_device_from_group(client: TestClient, owner_token: str) -> None:
    """Test removing a device from a group."""
    # Create device and group
    device_response = client.post(
        "/api/devices",
        json={
            "name": "Remove Test Device",
            "unit": "RPM",
            "sampling_interval": 60,
            "modbus_config": {
                "type": "tcp",
                "host": "localhost",
                "port": 502,
                "register": 1,
                "data_type": "int16",
            },
        },
        cookies={"access_token": owner_token},
    )
    device_id = device_response.json()["id"]

    group_response = client.post(
        "/api/groups",
        json={"name": "Remove Test Group"},
        cookies={"access_token": owner_token},
    )
    group_id = group_response.json()["id"]

    # Assign device
    client.post(
        f"/api/groups/{group_id}/devices/{device_id}",
        cookies={"access_token": owner_token},
    )

    # Remove device from group
    response = client.delete(
        f"/api/groups/{group_id}/devices/{device_id}",
        cookies={"access_token": owner_token},
    )

    assert response.status_code == 204


def test_delete_group_cascades_assignments(client: TestClient, owner_token: str) -> None:
    """Test that deleting a group removes device assignments."""
    # Create device and group
    device_response = client.post(
        "/api/devices",
        json={
            "name": "Cascade Test Device",
            "unit": "°C",
            "sampling_interval": 60,
            "modbus_config": {
                "type": "tcp",
                "host": "localhost",
                "port": 502,
                "register": 1,
                "data_type": "int16",
            },
        },
        cookies={"access_token": owner_token},
    )
    device_id = device_response.json()["id"]

    group_response = client.post(
        "/api/groups",
        json={"name": "Cascade Test Group"},
        cookies={"access_token": owner_token},
    )
    group_id = group_response.json()["id"]

    # Assign device to group
    client.post(
        f"/api/groups/{group_id}/devices/{device_id}",
        cookies={"access_token": owner_token},
    )

    # Delete group
    delete_response = client.delete(
        f"/api/groups/{group_id}",
        cookies={"access_token": owner_token},
    )
    assert delete_response.status_code == 204

    # Verify device still exists
    device_get_response = client.get(
        f"/api/devices/{device_id}",
        cookies={"access_token": owner_token},
    )
    assert device_get_response.status_code == 200

    # Device should now be assignable to a new group (constraint removed)
    new_group_response = client.post(
        "/api/groups",
        json={"name": "New Group"},
        cookies={"access_token": owner_token},
    )
    new_group_id = new_group_response.json()["id"]

    assign_response = client.post(
        f"/api/groups/{new_group_id}/devices/{device_id}",
        cookies={"access_token": owner_token},
    )
    assert assign_response.status_code == 200


def test_device_count_in_groups_list(client: TestClient, owner_token: str) -> None:
    """Test that groups list includes device count."""
    # Create group with devices
    group_response = client.post(
        "/api/groups",
        json={"name": "Count Test Group"},
        cookies={"access_token": owner_token},
    )
    group_id = group_response.json()["id"]

    # Create and assign 2 devices
    for i in range(2):
        device_response = client.post(
            "/api/devices",
            json={
                "name": f"Device {i + 1}",
                "unit": "°C",
                "sampling_interval": 60,
                "modbus_config": {
                    "type": "tcp",
                    "host": "localhost",
                    "port": 502,
                    "register": i + 1,
                    "data_type": "int16",
                },
            },
            cookies={"access_token": owner_token},
        )
        device_id = device_response.json()["id"]
        client.post(
            f"/api/groups/{group_id}/devices/{device_id}",
            cookies={"access_token": owner_token},
        )

    # List groups and check device count
    list_response = client.get(
        "/api/groups",
        cookies={"access_token": owner_token},
    )

    assert list_response.status_code == 200
    groups = list_response.json()["groups"]
    test_group = next(g for g in groups if g["id"] == group_id)
    assert test_group["device_count"] == 2
