from fastapi.testclient import TestClient
from app.main import app


def test_health() -> None:
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_api_root() -> None:
    response = TestClient(app).get("/api/v1")
    assert response.status_code == 200
    assert response.json()["version"] == "v1"
