"""Integration tests for device management endpoints."""

from fastapi.testclient import TestClient


def test_list_devices_as_authenticated_user(client: TestClient, owner_token: str) -> None:
    """Test listing devices as authenticated user."""
    response = client.get(
        "/api/devices",
        cookies={"access_token": owner_token},
    )

    assert response.status_code == 200
    data = response.json()
    assert "devices" in data
    assert "total" in data


def test_create_device_as_owner(client: TestClient, owner_token: str) -> None:
    """Test creating a device as owner."""
    device_data = {
        "name": "Temperature Sensor",
        "description": "Tank temperature monitor",
        "unit": "°C",
        "sampling_interval": 60,
        "thresholds": {"warning": 75.0, "critical": 90.0},
        "modbus_config": {
            "type": "tcp",
            "host": "192.168.1.100",
            "port": 502,
            "register": 40001,
            "data_type": "float32",
        },
    }

    response = client.post(
        "/api/devices",
        json=device_data,
        cookies={"access_token": owner_token},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Temperature Sensor"
    assert data["unit"] == "°C"
    assert data["status"] == "offline"
    assert data["thresholds"]["warning"] == 75.0
    assert data["modbus_config"]["type"] == "tcp"
    assert "id" in data


def test_create_device_as_viewer_forbidden(
    client: TestClient, viewer_user, db_session
) -> None:
    """Test that viewers cannot create devices."""
    # Login as viewer
    response = client.post(
        "/api/auth/login",
        json={"username": "viewer_user", "password": "viewer123"},
    )
    token = response.cookies.get("access_token")

    # Try to create device
    device_data = {
        "name": "Test Device",
        "unit": "bar",
        "sampling_interval": 30,
        "modbus_config": {"type": "tcp", "host": "localhost", "port": 502, "register": 1, "data_type": "int16"},
    }

    response = client.post(
        "/api/devices",
        json=device_data,
        cookies={"access_token": token},
    )

    assert response.status_code == 403


def test_get_device_details(client: TestClient, owner_token: str) -> None:
    """Test getting device details."""
    # Create device first
    device_data = {
        "name": "Pressure Sensor",
        "unit": "bar",
        "sampling_interval": 30,
        "modbus_config": {"type": "tcp", "host": "192.168.1.101", "port": 502, "register": 40002, "data_type": "int16"},
    }
    create_response = client.post(
        "/api/devices",
        json=device_data,
        cookies={"access_token": owner_token},
    )
    device_id = create_response.json()["id"]

    # Get device details
    response = client.get(
        f"/api/devices/{device_id}",
        cookies={"access_token": owner_token},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Pressure Sensor"
    assert data["id"] == device_id


def test_update_device(client: TestClient, owner_token: str) -> None:
    """Test updating a device."""
    # Create device
    create_response = client.post(
        "/api/devices",
        json={
            "name": "Original Name",
            "unit": "RPM",
            "sampling_interval": 60,
            "modbus_config": {"type": "tcp", "host": "localhost", "port": 502, "register": 1, "data_type": "int16"},
        },
        cookies={"access_token": owner_token},
    )
    device_id = create_response.json()["id"]

    # Update device
    update_response = client.patch(
        f"/api/devices/{device_id}",
        json={"name": "Updated Name", "sampling_interval": 120},
        cookies={"access_token": owner_token},
    )

    assert update_response.status_code == 200
    data = update_response.json()
    assert data["name"] == "Updated Name"
    assert data["sampling_interval"] == 120


def test_delete_device(client: TestClient, owner_token: str) -> None:
    """Test deleting a device."""
    # Create device
    create_response = client.post(
        "/api/devices",
        json={
            "name": "To Delete",
            "unit": "%",
            "sampling_interval": 60,
            "modbus_config": {"type": "tcp", "host": "localhost", "port": 502, "register": 1, "data_type": "int16"},
        },
        cookies={"access_token": owner_token},
    )
    device_id = create_response.json()["id"]

    # Delete device
    response = client.delete(
        f"/api/devices/{device_id}",
        cookies={"access_token": owner_token},
    )

    assert response.status_code == 204

    # Verify device is deleted
    get_response = client.get(
        f"/api/devices/{device_id}",
        cookies={"access_token": owner_token},
    )
    assert get_response.status_code == 404


def test_test_connection_endpoint(client: TestClient, owner_token: str) -> None:
    """Test the connection test endpoint."""
    # Create device
    create_response = client.post(
        "/api/devices",
        json={
            "name": "Connection Test",
            "unit": "°C",
            "sampling_interval": 60,
            "modbus_config": {"type": "tcp", "host": "localhost", "port": 502, "register": 1, "data_type": "float32"},
        },
        cookies={"access_token": owner_token},
    )
    device_id = create_response.json()["id"]

    # Test connection
    response = client.post(
        f"/api/devices/{device_id}/test-connection",
        cookies={"access_token": owner_token},
    )

    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "message" in data


def test_get_nonexistent_device(client: TestClient, owner_token: str) -> None:
    """Test getting a non-existent device returns 404."""
    response = client.get(
        "/api/devices/9999",
        cookies={"access_token": owner_token},
    )

    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()
