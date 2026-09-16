import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import torch
from app.ml.facial_model import create_facial_model, FacialCNNLSTM
from app.ml.facial_predictor import predict_facial_sequence, load_facial_model

def test_facial_model():
    print("Testing FacialCNNLSTM instantiating...")
    model = create_facial_model(feature_count=8, num_classes=4)
    dummy_input = torch.randn(32, 16, 8)
    output = model(dummy_input)
    assert output.shape == (32, 4), f"Unexpected output shape: {output.shape}"
    print(f"Model forward output shape: {output.shape}")

def test_facial_predictor():
    print("Testing facial predictor...")
    model = load_facial_model()
    dummy_sequence = np.random.randn(16, 8).astype(np.float32)
    res = predict_facial_sequence(dummy_sequence)
    print("Prediction result:", res)
    assert "predicted_class" in res
    assert "predicted_label" in res
    assert "confidence" in res
    assert "probabilities" in res
    assert len(res["probabilities"]) == 4

if __name__ == "__main__":
    test_facial_model()
    test_facial_predictor()
    print("ALL FACIAL MODEL & PREDICTOR TESTS PASSED!")
