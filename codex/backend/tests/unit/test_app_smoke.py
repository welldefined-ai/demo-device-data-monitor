from http import HTTPStatus

from fastapi.testclient import TestClient

from ddms import __version__
from ddms.main import app


def test_api_health_endpoint() -> None:
    client = TestClient(app)
    res = client.get("/api/health")
    assert res.status_code == HTTPStatus.OK
    payload = res.json()
    assert payload["status"] == "ok"
    assert payload["env"]


def test_api_version_endpoint() -> None:
    client = TestClient(app)
    res = client.get("/api/version")
    assert res.status_code == HTTPStatus.OK
    assert res.json() == {"version": __version__}
