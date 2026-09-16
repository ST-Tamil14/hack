import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.fusion_service import calculate_profile_weights, fuse_multimodal_results
from app.services.assessment_service import (
    convert_behavioral_prediction_to_modality_result,
    build_modality_results,
)
from app.ml.behavioral_predictor import predict_behavioral_video


def test_behavioral_assessment():
    video_path = PROJECT_ROOT / "datasets" / "raw" / "behavioral" / "video_001.mp4"
    print(f"Testing video path: {video_path}")

    # 1. Test direct prediction and conversion
    prediction = predict_behavioral_video(video_path)
    modality_res = convert_behavioral_prediction_to_modality_result(prediction)

    print("\nModality Result Output:")
    print(f"  Model Name: {modality_res['model_name']}")
    print(f"  Pain Related Score: {modality_res['pain_related_score']}")
    print(f"  Confidence: {modality_res['confidence']}")
    print(f"  Quality Score: {modality_res['quality_score']}")
    assert modality_res["model_name"] == "behavioral_cnn_lstm"
    assert "pain_related_score" in modality_res

    # 2. Test profile weights with restricted mobility status (bedridden / immobile / paralyzed / sedated)
    mobile_profile = {"mobility_status": "mobile", "communication_ability": "verbal"}
    bedridden_profile = {"mobility_status": "bedridden", "communication_ability": "verbal"}

    mobile_weights = calculate_profile_weights(mobile_profile)
    bedridden_weights = calculate_profile_weights(bedridden_profile)

    print("\nProfile Weights Comparison:")
    print(f"  Mobile Profile Weights: {mobile_weights}")
    print(f"  Bedridden Profile Weights: {bedridden_weights}")

    # Verify behavioral weight is significantly lower for bedridden patient
    assert bedridden_weights["behavioral"] < mobile_weights["behavioral"]

    # 3. Test multimodal fusion with behavioral model result
    modality_results = {
        "facial": {
            "pain_related_score": 0.64,
            "confidence": 0.81,
            "quality_score": 0.90,
            "model_name": "facial_cnn_lstm",
        },
        "physiological": {
            "pain_related_score": 0.71,
            "confidence": 0.78,
            "quality_score": 0.94,
            "model_name": "physiological_cnn_lstm",
        },
        "behavioral": modality_res,
        "voice": {
            "pain_related_score": 0.0,
            "confidence": 0.0,
            "quality_score": 0.0,
            "status": "missing",
        },
    }

    fusion = fuse_multimodal_results(
        patient_profile=mobile_profile,
        modality_results=modality_results,
    )

    print("\nMultimodal Fusion Result:")
    print(f"  Fusion Status: {fusion['fusion_status']}")
    print(f"  Final Pain Score: {fusion['pain_related_activity_score']}")
    print(f"  Level: {fusion['pain_related_activity_level']}")
    print(f"  Confidence: {fusion['confidence']}")
    print(f"  Active Modalities: {fusion['active_modalities']}")

    assert fusion["fusion_status"] == "completed"
    assert "behavioral" in fusion["active_modalities"]

    # 4. Test build_modality_results with behavioral_file_path
    built_results = build_modality_results(
        latest_features={},
        behavioral_file_path=str(video_path),
    )
    print("\nBuilt Modality Results with Behavioral Video:")
    print(f"  Behavioral result: {built_results.get('behavioral')}")
    assert "behavioral" in built_results
    assert built_results["behavioral"]["model_name"] == "behavioral_cnn_lstm"

    print("\nALL BEHAVIORAL ASSESSMENT TESTS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    test_behavioral_assessment()
