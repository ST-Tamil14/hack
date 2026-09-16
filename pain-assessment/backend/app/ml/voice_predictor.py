from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import torch

from app.ml.speech_recognition import transcribe_audio
from app.ml.voice_feature_extractor import extract_voice_features
from app.ml.voice_model import create_voice_model
from app.ml.voice_sequence_extractor import extract_voice_sequence


PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = PROJECT_ROOT / "models" / "voice_cnn_lstm_best.pt"
SCALER_PATH = PROJECT_ROOT / "datasets" / "processed" / "voice" / "voice_scaler.npz"

CLASS_NAMES = [
    "no_pain_related_activity",
    "low",
    "moderate",
    "high",
]

CLASS_TO_SCORE = {
    "no_pain_related_activity": 0.0,
    "low": 0.3,
    "moderate": 0.7,
    "high": 1.0,
}


def load_scaler() -> dict[str, np.ndarray] | None:
    if not SCALER_PATH.exists():
        return None
    try:
        scaler = np.load(SCALER_PATH)
        return {
            "mean": scaler["mean"],
            "scale": scaler["scale"],
        }
    except Exception:
        return None


def normalize_sequence(
    sequence: np.ndarray,
    scaler: dict[str, np.ndarray],
) -> np.ndarray:
    scale = np.where(scaler["scale"] == 0, 1.0, scaler["scale"])
    return ((sequence - scaler["mean"]) / scale).astype(np.float32)


def load_voice_model() -> torch.nn.Module | None:
    if not MODEL_PATH.exists():
        return None

    try:
        checkpoint = torch.load(MODEL_PATH, map_location="cpu")
        model = create_voice_model(
            feature_count=checkpoint.get("feature_count", 16),
            num_classes=checkpoint.get("num_classes", 4),
        )
        model.load_state_dict(checkpoint["model_state_dict"])
        model.eval()
        return model
    except Exception:
        return None


def predict_voice_file(
    audio_path: str | Path,
    window_size: int = 32,
) -> dict[str, Any]:
    audio_path = Path(audio_path)
    acoustic_features = extract_voice_features(audio_path)
    sequence_data = extract_voice_sequence(audio_path)
    sequence = sequence_data["features"]

    transcription = transcribe_audio(audio_path)
    detected_language = transcription.get("language")

    scaler = load_scaler()
    model = load_voice_model()

    if model is not None and scaler is not None and len(sequence) >= window_size:
        normalized = normalize_sequence(sequence, scaler)
        latest_window = normalized[-window_size:]
        input_tensor = torch.tensor(latest_window[None, ...], dtype=torch.float32)

        with torch.no_grad():
            logits = model(input_tensor)
            probabilities = torch.softmax(logits, dim=1)[0].numpy()

        predicted_index = int(np.argmax(probabilities))
        predicted_class = CLASS_NAMES[predicted_index]
        confidence = float(probabilities[predicted_index])
        score = float(CLASS_TO_SCORE[predicted_class])
        model_type = "voice_cnn_lstm"
    else:
        # Fallback acoustic score
        f0_mean = acoustic_features.get("f0_mean_hz") or 180.0
        pause_ratio = acoustic_features.get("pause_ratio") or 0.3
        vocal_events = acoustic_features.get("vocal_events", {})
        event_rate = vocal_events.get("estimated_vocal_event_rate") or 0.0

        pitch_score = min(max((f0_mean - 160.0) / 150.0, 0.0), 1.0)
        pause_score = min(max(pause_ratio, 0.0), 1.0)
        vocal_score = min(max(event_rate / 3.0, 0.0), 1.0)

        score = float(0.4 * pitch_score + 0.3 * pause_score + 0.3 * vocal_score)
        score = max(0.0, min(1.0, score))

        if score < 0.25:
            predicted_index = 0
        elif score < 0.55:
            predicted_index = 1
        elif score < 0.80:
            predicted_index = 2
        else:
            predicted_index = 3

        predicted_class = CLASS_NAMES[predicted_index]
        probabilities = [0.25, 0.25, 0.25, 0.25]
        probabilities[predicted_index] = 0.55
        total_p = sum(probabilities)
        probabilities = [p / total_p for p in probabilities]

        confidence = float(acoustic_features.get("quality_score") or 0.75)
        model_type = "preliminary_rule_based"

    return {
        "predicted_class": predicted_class,
        "predicted_class_index": predicted_index,
        "probabilities": {
            CLASS_NAMES[i]: float(p) for i, p in enumerate(probabilities)
        },
        "pain_related_score": round(score, 4),
        "confidence": round(confidence, 4),
        "language": detected_language,
        "quality_score": acoustic_features.get("quality_score", 0.75),
        "acoustic_features": acoustic_features,
        "model_type": model_type,
    }
