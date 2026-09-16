import uuid
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
AUTH_HEADERS = {"Authorization": "Bearer mock-admin-token"}


def test_assessment_run():
    # 1. Create Patient
    unique_code = f"TEST_A_{uuid.uuid4().hex[:6]}"
    patient_resp = client.post(
        "/patients/",
        json={
            "patient_code": unique_code,
            "communication_ability": "Fully verbal",
            "mobility_status": "Mobile",
        },
        headers=AUTH_HEADERS,
    )
    assert patient_resp.status_code == 201
    patient_id = patient_resp.json()["id"]

    try:
        # 2. Run Assessment
        response = client.post(f"/assessment/run/{patient_id}", headers=AUTH_HEADERS)
        assert response.status_code == 200

        data = response.json()
        assert "patient_id" in data
        assert "modality_results" in data
        assert "fusion_result" in data
        assert "clinical_message" in data

    finally:
        client.delete(f"/patients/{patient_id}", headers=AUTH_HEADERS)
