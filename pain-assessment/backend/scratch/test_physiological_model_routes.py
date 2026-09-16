import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient
from app.main import app
from app.ml.physiological_predictor import predict_physiological_file

client = TestClient(app)

def test_physiological_predictor():
    print("Testing predict_physiological_file on sample.csv...")
    file_path = PROJECT_ROOT / "datasets" / "raw" / "physiological" / "sample.csv"
    result = predict_physiological_file(file_path, window_size=32, stride=8)
    print("Predictor result:", result)
    assert "predicted_class" in result
    assert "probabilities" in result
    assert "pain_related_score" in result
    assert "confidence" in result

def test_physiological_predict_route():
    print("\nTesting POST /models/physiological/predict...")
    file_path = str(PROJECT_ROOT / "datasets" / "raw" / "physiological" / "sample.csv")
    payload = {
        "file_path": file_path,
        "window_size": 32,
        "stride": 8
    }

    response = client.post("/models/physiological/predict", json=payload)
    print("Status:", response.status_code)
    print("Response body:", response.json())
    assert response.status_code == 200
    data = response.json()
    assert "predicted_class" in data
    assert "pain_related_score" in data
    assert "confidence" in data

def test_model_status_both_models():
    print("\nTesting GET /models/status for facial and physiological models...")
    response = client.get("/models/status")
    print("Status body:", response.json())
    assert response.status_code == 200
    data = response.json()
    assert data["facial_model"]["status"] == "ready"
    assert data["physiological_model"]["status"] == "ready"

if __name__ == "__main__":
    test_physiological_predictor()
    test_physiological_predict_route()
    test_model_status_both_models()
    print("\nALL PHYSIOLOGICAL MODEL & ROUTE TESTS PASSED!")
