from app.services.fusion_service import fuse_multimodal_results
from fastapi.testclient import TestClient
from app.main import app

def test_fusion_service():
    # Test standard verbal patient with all 4 modalities
    patient_profile = {
        "communication_ability": "Fully verbal",
        "mobility_status": "Mobile",
        "facial_movement_limitation": False,
        "speech_limitation": False
    }

    modality_results = {
        "facial": {
            "pain_related_score": 0.72,
            "confidence": 0.85,
            "quality_score": 0.92
        },
        "physiological": {
            "pain_related_score": 0.64,
            "confidence": 0.80,
            "quality_score": 0.95
        },
        "behavioral": {
            "pain_related_score": 0.58,
            "confidence": 0.78,
            "quality_score": 0.88
        },
        "voice": {
            "pain_related_score": 0.70,
            "confidence": 0.82,
            "quality_score": 0.90
        }
    }

    result = fuse_multimodal_results(patient_profile, modality_results)
    print("Standard patient fusion result:")
    print("Score:", result["pain_related_activity_score"])
    print("Level:", result["pain_related_activity_level"])
    print("Confidence:", result["confidence"])
    print("Active modalities:", result["active_modalities"])

    assert result["fusion_status"] == "completed"
    assert result["pain_related_activity_level"] == "high"
    assert len(result["active_modalities"]) == 4

    # Test non-verbal patient with missing voice modality
    non_verbal_profile = {
        "communication_ability": "Non-verbal",
        "mobility_status": "Restricted",
        "facial_movement_limitation": False,
        "speech_limitation": True
    }

    non_verbal_modalities = {
        "facial": {
            "pain_related_score": 0.75,
            "confidence": 0.88,
            "quality_score": 0.90
        },
        "physiological": {
            "pain_related_score": 0.68,
            "confidence": 0.84,
            "quality_score": 0.94
        },
        "behavioral": {
            "pain_related_score": 0.61,
            "confidence": 0.75,
            "quality_score": 0.80
        }
    }

    result_nv = fuse_multimodal_results(non_verbal_profile, non_verbal_modalities)
    print("\nNon-verbal patient fusion result:")
    print("Score:", result_nv["pain_related_activity_score"])
    print("Level:", result_nv["pain_related_activity_level"])
    print("Confidence:", result_nv["confidence"])
    print("Active modalities:", result_nv["active_modalities"])
    print("Missing modalities:", result_nv["missing_modalities"])

    assert result_nv["fusion_status"] == "completed"
    assert "voice" in result_nv["missing_modalities"]

    # Test API endpoint
    client = TestClient(app)
    response = client.post("/fusion/calculate", json={
        "patient_id": "test-patient-id",
        "patient_profile": patient_profile,
        "modality_results": modality_results
    })
    print("\nAPI Response status code:", response.status_code)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["fusion_status"] == "completed"
    print("Multimodal Fusion test passed successfully!")

if __name__ == "__main__":
    test_fusion_service()
