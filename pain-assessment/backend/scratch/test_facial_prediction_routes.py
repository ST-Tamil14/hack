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

client = TestClient(app)

def test_facial_predict_endpoint():
    print("Testing POST /models/facial/predict...")
    sequence = [[0.12, 0.08, 0.15, 0.42, 0.55, 1.31, 0.01, 0.48] for _ in range(16)]
    payload = {"sequence": sequence}

    response = client.post("/models/facial/predict", json=payload)
    print("Response status:", response.status_code)
    print("Response body:", response.json())
    assert response.status_code == 200
    data = response.json()
    assert "predicted_class" in data
    assert "predicted_label" in data
    assert "confidence" in data
    assert data["time_steps"] == 16
    assert data["feature_count"] == 8

def test_facial_predict_video_endpoint():
    print("\nTesting POST /models/facial/predict-video...")
    
    # Create a small synthetic MP4 video in temp file
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        tmp_path = tmp.name

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(tmp_path, fourcc, 10.0, (100, 100))
    for _ in range(20):
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        # Draw a synthetic face rectangle
        cv2.rectangle(frame, (20, 20), (80, 80), (255, 255, 255), -1)
        out.write(frame)
    out.release()

    with open(tmp_path, "rb") as f:
        video_bytes = f.read()

    Path(tmp_path).unlink()

    files = {
        "file": ("test_video.mp4", video_bytes, "video/mp4")
    }

    response = client.post("/models/facial/predict-video", files=files)
    print("Video prediction status:", response.status_code)
    print("Video prediction response:", response.json())
    assert response.status_code == 200
    data = response.json()
    assert "predicted_class" in data
    assert "video_metadata" in data

if __name__ == "__main__":
    test_facial_predict_endpoint()
    test_facial_predict_video_endpoint()
    print("\nALL FACIAL PREDICTION ROUTE TESTS PASSED!")
