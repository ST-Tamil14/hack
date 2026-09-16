from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import torch

from app.ml.behavioral_model import (
    create_behavioral_model,
)
from app.ml.behavioral_sequence_extractor import (
    extract_behavioral_sequence,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = PROJECT_ROOT / "models" / "behavioral_cnn_lstm_best.pt"

SCALER_PATH = (
    PROJECT_ROOT
    / "datasets"
    / "processed"
    / "behavioral"
    / "behavioral_scaler.npz"
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


def normalize_sequence(
    sequence: np.ndarray,
    scaler: dict[str, np.ndarray],
) -> np.ndarray:
    scale = np.where(
        scaler["scale"] == 0,
        1.0,
        scaler["scale"],
    )

    return (
        (sequence - scaler["mean"])
        / scale
    ).astype(np.float32)


def load_behavioral_model() -> torch.nn.Module:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model not found: {MODEL_PATH}"
        )

    checkpoint = torch.load(
        MODEL_PATH,
        map_location="cpu",
    )

    model = create_behavioral_model(
        feature_count=checkpoint["feature_count"],
        num_classes=checkpoint["num_classes"],
    )

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    model.eval()

    return model


def predict_behavioral_video(
    video_path: str | Path,
    window_size: int = 32,
) -> dict[str, Any]:
    extracted = extract_behavioral_sequence(
        video_path=video_path,
    )

    sequence = extracted["features"]

    if len(sequence) < window_size:
        raise ValueError(
            "The video does not contain enough detected poses"
        )

    scaler = load_scaler()

    normalized = normalize_sequence(
        sequence,
        scaler,
    )

    latest_window = normalized[-window_size:]

    model = load_behavioral_model()

    input_tensor = torch.tensor(
        latest_window[None, ...],
        dtype=torch.float32,
    )

    with torch.no_grad():
        logits = model(input_tensor)
        probabilities = torch.softmax(
            logits,
            dim=1,
        )[0]

    probabilities_array = (
        probabilities.cpu().numpy()
    )

    predicted_index = int(
        np.argmax(probabilities_array)
    )

    score = float(
        probabilities_array[1] * 0.3
        + probabilities_array[2] * 0.7
        + probabilities_array[3] * 1.0
    )

    return {
        "predicted_class": CLASS_NAMES[predicted_index],
        "predicted_class_index": predicted_index,
        "probabilities": {
            CLASS_NAMES[index]: float(value)
            for index, value in enumerate(
                probabilities_array
            )
        },
        "pain_related_score": score,
        "confidence": float(
            probabilities_array[predicted_index]
        ),
        "feature_names": extracted["feature_names"],
        "processed_frames": extracted["processed_frames"],
        "detected_poses": extracted["detected_poses"],
        "pose_detection_rate": extracted[
            "pose_detection_rate"
        ],
        "duration_seconds": extracted[
            "duration_seconds"
        ],
    }
