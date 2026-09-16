from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import torch

from app.ml.physiological_model import create_physiological_model
from app.ml.physiological_sequence_extractor import (
    extract_physiological_sequence,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = PROJECT_ROOT / "models" / "physiological_cnn_lstm_best.pt"

SCALER_PATH = (
    PROJECT_ROOT
    / "datasets"
    / "processed"
    / "physiological"
    / "physiological_scaler.npz"
)

CLASS_NAMES = [
    "no_pain_related_activity",
    "low",
    "moderate",
    "high",
]


def load_scaler() -> dict[str, np.ndarray]:
    if not SCALER_PATH.exists():
        raise FileNotFoundError(
            f"Scaler not found: {SCALER_PATH}"
        )

    scaler = np.load(SCALER_PATH)

    return {
        "mean": scaler["mean"],
        "scale": scaler["scale"],
    }


def normalize_windows(
    windows: np.ndarray,
    scaler: dict[str, np.ndarray],
) -> np.ndarray:
    mean = scaler["mean"]
    scale = np.where(
        scaler["scale"] == 0,
        1.0,
        scaler["scale"],
    )

    return (
        (windows - mean.reshape(1, 1, -1))
        / scale.reshape(1, 1, -1)
    ).astype(np.float32)


def load_physiological_model() -> torch.nn.Module:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model not found: {MODEL_PATH}"
        )

    checkpoint = torch.load(
        MODEL_PATH,
        map_location="cpu",
    )

    model = create_physiological_model(
        feature_count=checkpoint["feature_count"],
        num_classes=checkpoint["num_classes"],
    )

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    model.eval()

    return model


def predict_physiological_file(
    file_path: str | Path,
    window_size: int = 32,
    stride: int = 8,
) -> dict[str, Any]:
    extracted = extract_physiological_sequence(
        file_path=file_path,
        window_size=window_size,
        stride=stride,
    )

    windows = extracted["windows"]

    if len(windows) == 0:
        raise ValueError(
            "The physiological file does not contain enough samples"
        )

    scaler = load_scaler()
    normalized_windows = normalize_windows(
        windows,
        scaler,
    )

    # Use the latest available window
    latest_window = normalized_windows[-1:]

    model = load_physiological_model()

    input_tensor = torch.tensor(
        latest_window,
        dtype=torch.float32,
    )

    with torch.no_grad():
        logits = model(input_tensor)
        probabilities = torch.softmax(
            logits,
            dim=1,
        )[0]

    predicted_class_index = int(
        torch.argmax(probabilities).item()
    )

    probabilities_list = probabilities.cpu().numpy()

    pain_related_score = float(
        probabilities_list[1] * 0.3
        + probabilities_list[2] * 0.7
        + probabilities_list[3] * 1.0
    )

    return {
        "predicted_class": CLASS_NAMES[predicted_class_index],
        "predicted_class_index": predicted_class_index,
        "probabilities": {
            CLASS_NAMES[index]: float(value)
            for index, value in enumerate(probabilities_list)
        },
        "pain_related_score": round(pain_related_score, 4),
        "confidence": round(float(
            probabilities_list[predicted_class_index]
        ), 4),
        "feature_names": extracted["feature_names"],
        "sample_count": extracted["sample_count"],
        "window_count": extracted["window_count"],
    }
