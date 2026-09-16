from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import torch

from app.ml.facial_model import (
    create_facial_model,
)


PROJECT_ROOT = (
    Path(__file__).resolve().parents[2]
)

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "facial_cnn_lstm_best.pt"
)

SCALER_PATH = (
    PROJECT_ROOT
    / "datasets"
    / "processed"
    / "facial"
    / "real_facial_scaler.npz"
)

DEVICE = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)

CLASS_NAMES = {
    0: "no_pain_related_activity",
    1: "low",
    2: "moderate",
    3: "high",
}


def load_scaler() -> tuple[np.ndarray, np.ndarray]:
    if not SCALER_PATH.exists():
        raise FileNotFoundError(
            f"Scaler not found: {SCALER_PATH}"
        )

    scaler_data = np.load(
        SCALER_PATH
    )

    mean = scaler_data["mean"]
    scale = scaler_data["scale"]

    return mean, scale


def normalize_sequence(
    sequence: np.ndarray,
) -> np.ndarray:
    mean, scale = load_scaler()

    scale = np.where(
        scale == 0,
        1.0,
        scale,
    )

    return (
        (sequence - mean)
        / scale
    ).astype(np.float32)


def load_facial_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Trained model not found: {MODEL_PATH}"
        )

    checkpoint = torch.load(
        MODEL_PATH,
        map_location=DEVICE,
    )

    model = create_facial_model(
        feature_count=checkpoint[
            "feature_count"
        ],
        num_classes=checkpoint[
            "num_classes"
        ],
    )

    model.load_state_dict(
        checkpoint[
            "model_state_dict"
        ]
    )

    model.to(DEVICE)
    model.eval()

    return model, checkpoint


def predict_facial_sequence(
    sequence: np.ndarray,
) -> dict[str, Any]:
    if sequence.ndim != 2:
        raise ValueError(
            "Expected sequence shape "
            "[time_steps, feature_count]"
        )

    if len(sequence) == 0:
        raise ValueError(
            "The facial sequence is empty"
        )

    model, checkpoint = (
        load_facial_model()
    )

    expected_feature_count = (
        checkpoint["feature_count"]
    )

    actual_feature_count = (
        sequence.shape[1]
    )

    if (
        actual_feature_count
        != expected_feature_count
    ):
        raise ValueError(
            "Feature count mismatch. "
            f"Expected {expected_feature_count}, "
            f"received {actual_feature_count}."
        )

    normalized_sequence = (
        normalize_sequence(sequence)
    )

    input_tensor = torch.tensor(
        normalized_sequence,
        dtype=torch.float32,
    ).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        logits = model(
            input_tensor
        )

        probabilities = torch.softmax(
            logits,
            dim=1,
        )

        predicted_class = int(
            torch.argmax(
                probabilities,
                dim=1,
            ).item()
        )

        confidence = float(
            probabilities[
                0,
                predicted_class,
            ].item()
        )

    return {
        "predicted_class": predicted_class,
        "predicted_label": CLASS_NAMES[
            predicted_class
        ],
        "confidence": round(
            confidence,
            4,
        ),
        "probabilities": {
            CLASS_NAMES[index]: round(
                float(
                    probabilities[
                        0,
                        index,
                    ].item()
                ),
                4,
            )
            for index in range(
                probabilities.shape[1]
            )
        },
        "time_steps": int(
            sequence.shape[0]
        ),
        "feature_count": int(
            sequence.shape[1]
        ),
        "model_version": (
            "facial-cnn-lstm-v1"
        ),
    }


def predict_facial_video(
    video_path: str | Path,
    window_size: int = 16,
) -> dict[str, Any]:
    from app.ml.facial_sequence_extractor import (
        extract_facial_sequence,
    )

    extraction = extract_facial_sequence(
        video_path=video_path
    )

    sequence = extraction[
        "features"
    ]

    if len(sequence) < window_size:
        raise ValueError(
            "Video does not contain enough "
            "detected facial frames"
        )

    latest_window = sequence[
        -window_size:
    ]

    result = predict_facial_sequence(
        latest_window
    )

    result["video_metadata"] = {
        "fps": extraction["fps"],
        "frame_count": extraction[
            "frame_count"
        ],
        "processed_frames": extraction[
            "processed_frames"
        ],
        "detected_faces": extraction[
            "detected_faces"
        ],
        "face_detection_rate": extraction[
            "face_detection_rate"
        ],
        "duration_seconds": extraction[
            "duration_seconds"
        ],
    }

    return result
