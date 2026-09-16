from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_unauthenticated_request_fails():
    response = client.get("/health/")
    # HTTPBearer returns 403 Not Authenticated or 401
    assert response.status_code in (401, 403)


def test_authenticated_request_succeeds():
    headers = {"Authorization": "Bearer mock-admin-token"}
    response = client.get("/health/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["authenticated_user"] == "admin@example.com"
    assert data["role"] == "admin"


def test_role_restriction_denied():
    headers = {"Authorization": "Bearer mock-viewer-token"}
    response = client.delete("/patients/non-existent-id", headers=headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have permission to perform this action"


def test_role_restriction_allowed():
    headers = {"Authorization": "Bearer mock-admin-token"}
    response = client.delete("/patients/non-existent-id", headers=headers)
    # Role check passes, patient service will return 404 for non-existent patient or 200
    assert response.status_code in (200, 404)
