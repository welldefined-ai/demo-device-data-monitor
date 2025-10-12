from fastapi.testclient import TestClient

from ddms import __version__
from ddms.main import app


def test_root_health_endpoint_exposes_env_and_version() -> None:
    client = TestClient(app)
    res = client.get("/health")
    assert res.status_code == 200
    payload = res.json()
    assert payload["status"] == "ok"
    assert payload["version"] == __version__
    assert payload["env"]


def test_api_health_endpoint_matches_root_health() -> None:
    client = TestClient(app)
    res = client.get("/api/health")
    assert res.status_code == 200
    payload = res.json()
    assert payload["status"] == "ok"
    assert payload["version"] == __version__
    assert payload["env"]


def test_api_version_endpoint() -> None:
    client = TestClient(app)
    res = client.get("/api/version")
    assert res.status_code == 200
    assert res.json() == {"version": __version__}
