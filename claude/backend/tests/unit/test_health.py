"""Tests for health check endpoints."""

import pytest
from fastapi.testclient import TestClient

from ddms.main import app


@pytest.fixture
def client() -> TestClient:
    """Create a test client."""
    return TestClient(app)


def test_system_health(client: TestClient) -> None:
    """Test GET /health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"
    assert "env" in data
    assert data["env"] in ["development", "production", "test"]


def test_api_health(client: TestClient) -> None:
    """Test GET /api/health endpoint matches root health."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"
    assert "env" in data
    assert data["env"] in ["development", "production", "test"]


def test_api_version(client: TestClient) -> None:
    """Test GET /api/version endpoint."""
    response = client.get("/api/version")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert isinstance(data["version"], str)
    assert data == {"version": data["version"]}
