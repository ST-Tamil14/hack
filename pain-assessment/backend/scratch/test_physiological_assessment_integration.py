import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.assessment_service import (
    convert_physiological_prediction_to_modality_result,
    build_modality_results,
)
from app.services.fusion_service import fuse_multimodal_results

def test_physiological_assessment_helpers():
    print("Testing physiological prediction conversion...")
    dummy_pred = {
        "predicted_class": "moderate",
        "predicted_class_index": 2,
        "probabilities": {"no_pain_related_activity": 0.1, "low": 0.2, "moderate": 0.6, "high": 0.1},
        "pain_related_score": 0.58,
        "confidence": 0.60,
        "feature_names": ["heart_rate", "hrv"],
        "sample_count": 100,
        "window_count": 10,
    }

    res = convert_physiological_prediction_to_modality_result(dummy_pred)
    print("Converted result:", res)
    assert res["pain_related_score"] == 0.58
    assert res["confidence"] == 0.60
    assert res["quality_score"] == 1.0
    assert res["model_version"] == "physiological-cnn-lstm-v1"

def test_build_modality_results_with_physiological_file():
    print("\nTesting build_modality_results with physiological_file_path...")
    file_path = str(PROJECT_ROOT / "datasets" / "raw" / "physiological" / "sample.csv")
    latest_features = {
        "behavioral": {"features": {"movement_intensity_mean": 0.1}},
    }

    modality_results = build_modality_results(
        latest_features,
        physiological_file_path=file_path,
    )
    print("Modality results:", modality_results)
    assert "physiological" in modality_results
    assert modality_results["physiological"]["model_version"] == "physiological-cnn-lstm-v1"
    assert "pain_related_score" in modality_results["physiological"]

    patient_profile = {
        "communication_ability": "verbal",
        "mobility_status": "mobile",
    }

    fusion = fuse_multimodal_results(patient_profile, modality_results)
    print("Fusion output:", fusion)
    assert fusion["fusion_status"] == "completed"
    assert "physiological" in fusion["active_modalities"]

if __name__ == "__main__":
    test_physiological_assessment_helpers()
    test_build_modality_results_with_physiological_file()
    print("\nALL PHYSIOLOGICAL ASSESSMENT INTEGRATION TESTS PASSED!")
