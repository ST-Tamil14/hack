from fastapi.testclient import TestClient

from app.main import app
from app.services.fusion_service import (
    construct_fusion_feature_vector,
    fuse_multimodal_results,
)

client = TestClient(app)


def test_multimodal_fusion_feature_vector_construction():
    profile = {
        "communication_ability": "intubated",
        "mobility_status": "bedridden",
        "facial_movement_limitation": True,
        "speech_limitation": True,
    }
    modality_results = {
        "facial": {"pain_related_score": 0.75, "confidence": 0.85, "quality_score": 0.90},
        "physiological": {"pain_related_score": 0.60, "confidence": 0.80, "quality_score": 0.95},
        "behavioral": {"pain_related_score": 0.50, "confidence": 0.70, "quality_score": 0.80},
        "voice": {"pain_related_score": 0.65, "confidence": 0.75, "quality_score": 0.85},
    }

    vector, active_mods, missing_mods = construct_fusion_feature_vector(
        patient_profile=profile,
        modality_results=modality_results,
    )

    assert len(vector) == 22
    # Voice, Facial, Behavioral are masked due to profile limitations
    assert "physiological" in active_mods
    assert "voice" in missing_mods


def test_multimodal_fusion_mlp_prediction():
    profile = {
        "communication_ability": "Fully verbal",
        "mobility_status": "Mobile",
        "facial_movement_limitation": False,
        "speech_limitation": False,
    }
    modality_results = {
        "facial": {"pain_related_score": 0.72, "confidence": 0.85, "quality_score": 0.92},
        "physiological": {"pain_related_score": 0.64, "confidence": 0.80, "quality_score": 0.95},
        "behavioral": {"pain_related_score": 0.58, "confidence": 0.78, "quality_score": 0.88},
        "voice": {"pain_related_score": 0.70, "confidence": 0.82, "quality_score": 0.90},
    }

    result = fuse_multimodal_results(
        patient_profile=profile,
        modality_results=modality_results,
    )

    assert result["fusion_status"] == "completed"
    assert result["fusion_model"] == "multimodal_fusion_mlp"
    assert result["calibration_status"] == "calibrated"
    assert "ablation_scores" in result
    assert "without_facial" in result["ablation_scores"]


def test_all_models_status_ready():
    response = client.get("/models/status")
    assert response.status_code == 200
    data = response.json()

    models = data["models"]
    assert models["facial"]["status"] == "ready"
    assert models["physiological"]["status"] == "ready"
    assert models["behavioral"]["status"] == "ready"
    assert models["voice"]["status"] == "ready"
    assert models["fusion"]["status"] == "ready"
