import uuid
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
AUTH_HEADERS = {"Authorization": "Bearer mock-admin-token"}


def test_vitals_crud():
    # Create patient first
    unique_code = f"TEST_V_{uuid.uuid4().hex[:6]}"
    patient_resp = client.post(
        "/patients/",
        json={
            "patient_code": unique_code,
            "age_group": "adult",
        },
        headers=AUTH_HEADERS,
    )
    assert patient_resp.status_code == 201
    patient_id = patient_resp.json()["id"]

    try:
        vital_payload = {
            "patient_id": patient_id,
            "heart_rate": 96,
            "systolic_bp": 132,
            "diastolic_bp": 84,
            "respiratory_rate": 21,
            "spo2": 98,
            "temperature": 37.1,
            "hrv": 42,
            "eda_gsr": 3.2,
            "skin_temperature": 32.4,
            "perfusion_index": 2.1,
            "consciousness_status": "Alert",
            "sedation_status": "None",
            "clinical_pain_score": 4,
        }

        # 1. Post Vital Sign
        response = client.post("/vitals/", json=vital_payload, headers=AUTH_HEADERS)
        assert response.status_code == 201
        vital_data = response.json()
        assert vital_data["heart_rate"] == 96
        vital_id = vital_data["id"]

        # 2. Get Vitals for Patient
        response = client.get(f"/vitals/patient/{patient_id}", headers=AUTH_HEADERS)
        assert response.status_code == 200
        vitals_list = response.json()
        assert len(vitals_list) >= 1

        # 3. Get Latest Vital for Patient
        response = client.get(f"/vitals/patient/{patient_id}/latest", headers=AUTH_HEADERS)
        assert response.status_code == 200
        assert response.json()["id"] == vital_id

    finally:
        client.delete(f"/patients/{patient_id}", headers=AUTH_HEADERS)
