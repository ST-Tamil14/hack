import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient
from app.main import app
from app.ml.behavioral_sequence_extractor import extract_behavioral_sequence
from app.ml.behavioral_predictor import predict_behavioral_video


def test_pipeline():
    video_path = PROJECT_ROOT / "datasets" / "raw" / "behavioral" / "video_001.mp4"
    print(f"Testing video path: {video_path}")

    # Test feature extraction
    extracted = extract_behavioral_sequence(video_path)
    print("Sequence Extraction Output:")
    print(f"  Processed frames: {extracted['processed_frames']}")
    print(f"  Detected poses: {extracted['detected_poses']}")
    print(f"  Feature shape: {extracted['features'].shape}")
    assert extracted["features"].shape[1] == 11

    # Test direct prediction
    prediction = predict_behavioral_video(video_path)
    print("\nPredictor Output:")
    print(f"  Predicted class: {prediction['predicted_class']}")
    print(f"  Score: {prediction['pain_related_score']}")
    print(f"  Confidence: {prediction['confidence']}")
    print(f"  Probabilities: {prediction['probabilities']}")

    # Test FastAPI endpoints
    client = TestClient(app)

    # 1. Model status
    response = client.get("/models/status")
    assert response.status_code == 200
    status_data = response.json()
    print("\nModel Status Output:")
    print(f"  Behavioral status: {status_data['models']['behavioral']['status']}")
    assert status_data["models"]["behavioral"]["status"] == "ready"

    # 2. Predict video endpoint
    with open(video_path, "rb") as f:
        response = client.post(
            "/models/behavioral/predict-video",
            files={"file": ("video_001.mp4", f, "video/mp4")},
        )
    print("\nAPI Prediction Endpoint Response:")
    print(f"  Status code: {response.status_code}")
    print(f"  Body: {response.json()}")
    assert response.status_code == 200

    print("\nALL VERIFICATION TESTS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    test_pipeline()
