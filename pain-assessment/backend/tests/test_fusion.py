from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
AUTH_HEADERS = {"Authorization": "Bearer mock-admin-token"}


def test_fusion_calculate_endpoint():
    payload = {
        "patient_id": "P001",
        "patient_profile": {
            "communication_ability": "Fully verbal",
            "mobility_status": "Mobile",
            "facial_movement_limitation": False,
            "speech_limitation": False,
        },
        "modality_results": {
            "facial": {
                "pain_related_score": 0.72,
                "confidence": 0.85,
                "quality_score": 0.92,
            },
            "physiological": {
                "pain_related_score": 0.64,
                "confidence": 0.80,
                "quality_score": 0.95,
            },
            "behavioral": {
                "pain_related_score": 0.58,
                "confidence": 0.78,
                "quality_score": 0.88,
            },
            "voice": {
                "pain_related_score": 0.70,
                "confidence": 0.82,
                "quality_score": 0.90,
            },
        },
    }

    response = client.post("/fusion/calculate", json=payload, headers=AUTH_HEADERS)
    assert response.status_code == 200

    data = response.json()
    assert "pain_related_activity_score" in data
    assert "pain_related_activity_level" in data
    assert "confidence" in data
    assert "active_modalities" in data
    assert "missing_modalities" in data
    assert "modality_contributions" in data
    assert "profile_weights" in data
    assert data["fusion_status"] == "completed"
