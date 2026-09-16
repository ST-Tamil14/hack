import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import cv2
import numpy as np
import tempfile
from fastapi.testclient import TestClient
from app.main import app
from app.services.assessment_service import (
    predict_from_facial_file,
    convert_facial_prediction_to_modality_result,
)

client = TestClient(app)

def test_model_status_endpoint():
    print("Testing GET /models/status...")
    response = client.get("/models/status")
    print("Status code:", response.status_code)
    print("Status body:", response.json())
    assert response.status_code == 200
    data = response.json()
    assert "facial_model" in data
    assert data["facial_model"]["available"] is True
    assert data["facial_model"]["status"] == "ready"

def test_facial_file_prediction_integration():
    print("\nTesting predict_from_facial_file with synthetic video...")
    
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        tmp_path = tmp.name

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(tmp_path, fourcc, 10.0, (100, 100))
    for _ in range(20):
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.rectangle(frame, (20, 20), (80, 80), (255, 255, 255), -1)
        out.write(frame)
    out.release()

    res = predict_from_facial_file(tmp_path)
    print("Modality result from video file:", res)

    Path(tmp_path).unlink()

    assert "pain_related_score" in res
    assert "confidence" in res
    assert "quality_score" in res
    assert "predicted_label" in res
    assert res["model_version"] == "facial-cnn-lstm-v1"

if __name__ == "__main__":
    test_model_status_endpoint()
    test_facial_file_prediction_integration()
    print("\nALL FACIAL ASSESSMENT INTEGRATION TESTS PASSED!")
