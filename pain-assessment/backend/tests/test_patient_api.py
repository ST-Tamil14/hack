import uuid
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
AUTH_HEADERS = {"Authorization": "Bearer mock-admin-token"}


def test_patient_crud():
    unique_code = f"TEST_{uuid.uuid4().hex[:6]}"

    payload = {
        "patient_code": unique_code,
        "age_group": "adult",
        "clinical_department": "postoperative",
        "diagnosis": "Postoperative recovery",
        "pain_location": "Abdomen",
        "pain_type": "Acute",
        "recent_procedure": "Abdominal surgery",
        "medical_conditions": "None reported",
        "medication_status": "Analgesic administered",
        "sedation_status": "Alert",
        "mobility_status": "Limited",
        "communication_ability": "Fully verbal",
        "preferred_language": "English",
        "facial_movement_limitation": False,
        "speech_limitation": False,
        "initial_pain_score": 4,
        "clinical_notes": "Automated test patient",
    }

    # 1. Create Patient
    response = client.post("/patients/", json=payload, headers=AUTH_HEADERS)
    assert response.status_code == 201
    patient_data = response.json()
    assert "id" in patient_data
    patient_id = patient_data["id"]
    assert patient_data["patient_code"] == unique_code

    # 2. Get Patient by ID
    response = client.get(f"/patients/{patient_id}", headers=AUTH_HEADERS)
    assert response.status_code == 200
    assert response.json()["id"] == patient_id

    # 3. Get Patient by Code
    response = client.get(f"/patients/{unique_code}", headers=AUTH_HEADERS)
    assert response.status_code == 200
    assert response.json()["id"] == patient_id

    # 4. Update Patient
    update_payload = {"clinical_notes": "Updated notes"}
    response = client.put(f"/patients/{patient_id}", json=update_payload, headers=AUTH_HEADERS)
    assert response.status_code == 200
    assert response.json()["clinical_notes"] == "Updated notes"

    # 5. Delete Patient
    response = client.delete(f"/patients/{patient_id}", headers=AUTH_HEADERS)
    assert response.status_code == 200

    # 6. Verify NotFound after deletion
    response = client.get(f"/patients/{patient_id}", headers=AUTH_HEADERS)
    assert response.status_code == 404
