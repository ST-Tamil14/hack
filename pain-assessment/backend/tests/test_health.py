from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
AUTH_HEADERS = {"Authorization": "Bearer mock-admin-token"}


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Pain Assessment Backend is running"


def test_health_endpoint():
    response = client.get("/health/", headers=AUTH_HEADERS)
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_model_status_endpoint():
    response = client.get("/models/status", headers=AUTH_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert "facial" in data["models"]
    assert "physiological" in data["models"]
    assert "behavioral" in data["models"]
    assert "voice" in data["models"]
