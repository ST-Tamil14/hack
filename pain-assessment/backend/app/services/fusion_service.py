from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import torch

from app.ml.fusion_model import FUSION_FEATURE_NAMES, create_fusion_model


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FUSION_MODEL_PATH = PROJECT_ROOT / "models" / "multimodal_fusion_best.pt"
FUSION_SCALER_PATH = PROJECT_ROOT / "datasets" / "processed" / "fusion" / "fusion_scaler.npz"

DEFAULT_WEIGHTS = {
    "facial": 0.25,
    "physiological": 0.25,
    "behavioral": 0.25,
    "voice": 0.25,
}

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


def clamp(
    value: float,
    minimum: float = 0.0,
    maximum: float = 1.0,
) -> float:
    return max(minimum, min(maximum, value))


def normalize_score(value: Any) -> float | None:
    if value is None:
        return None

    if isinstance(value, str):
        mapping = {
            "low": 0.25,
            "mild": 0.25,
            "moderate": 0.60,
            "medium": 0.60,
            "high": 0.90,
            "marked": 0.90,
        }
        return mapping.get(value.lower())

    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return None

    if numeric_value > 1:
        numeric_value = numeric_value / 100.0

    return clamp(numeric_value)


def get_modality_score(modality_data: dict[str, Any]) -> float | None:
    possible_score_keys = [
        "pain_related_score",
        "pain_score",
        "activity_score",
        "score",
    ]

    for key in possible_score_keys:
        if key in modality_data:
            score = normalize_score(modality_data.get(key))
            if score is not None:
                return score

    return None


def get_modality_quality(modality_data: dict[str, Any]) -> float:
    quality = normalize_score(modality_data.get("quality_score", 1.0))
    return 0.0 if quality is None else quality


def get_modality_confidence(modality_data: dict[str, Any]) -> float:
    confidence = normalize_score(modality_data.get("confidence"))
    if confidence is None:
        confidence = get_modality_quality(modality_data)
    return confidence


def adjust_behavioral_weight(
    base_weight: float,
    mobility_status: str | None,
) -> float:
    restricted_statuses = {
        "immobile",
        "bedridden",
        "restricted",
        "paralyzed",
        "sedated",
    }

    if mobility_status:
        normalized_status = mobility_status.lower()
        if any(status in normalized_status for status in restricted_statuses):
            return 0.15 * base_weight

    return base_weight


def calculate_profile_weights(
    patient_profile: dict[str, Any],
) -> dict[str, float]:
    weights = DEFAULT_WEIGHTS.copy()

    communication_ability = str(patient_profile.get("communication_ability", "")).lower()
    mobility_status = str(patient_profile.get("mobility_status", "")).lower()
    speech_limitation = bool(patient_profile.get("speech_limitation", False))
    facial_limitation = bool(patient_profile.get("facial_movement_limitation", False))

    if (
        "non-verbal" in communication_ability
        or "intubated" in communication_ability
        or speech_limitation
    ):
        weights["voice"] = 0.05
        weights["facial"] = 0.35
        weights["physiological"] = 0.35
        weights["behavioral"] = 0.25

    if facial_limitation:
        weights["facial"] = 0.05
        weights["physiological"] = 0.40
        weights["behavioral"] = 0.40
        weights["voice"] = 0.15

    weights["behavioral"] = adjust_behavioral_weight(
        weights["behavioral"],
        mobility_status,
    )

    total = sum(weights.values())
    if total == 0:
        return DEFAULT_WEIGHTS.copy()

    return {m: w / total for m, w in weights.items()}


def classify_fusion_score(score: float | None) -> str:
    if score is None:
        return "insufficient_data"
    if score < 0.30:
        return "low"
    if score < 0.65:
        return "moderate"
    return "high"


def load_fusion_model_and_scaler() -> tuple[nn.Module | None, dict[str, np.ndarray] | None]:
    if not FUSION_MODEL_PATH.exists() or not FUSION_SCALER_PATH.exists():
        return None, None

    try:
        checkpoint = torch.load(FUSION_MODEL_PATH, map_location="cpu")
        model = create_fusion_model(
            input_size=checkpoint.get("feature_count", 22),
            num_classes=checkpoint.get("num_classes", 4),
        )
        model.load_state_dict(checkpoint["model_state_dict"])
        model.eval()

        scaler_data = np.load(FUSION_SCALER_PATH)
        scaler = {"mean": scaler_data["mean"], "scale": scaler_data["scale"]}
        return model, scaler
    except Exception:
        return None, None


def construct_fusion_feature_vector(
    patient_profile: dict[str, Any],
    modality_results: dict[str, dict[str, Any]],
) -> tuple[np.ndarray, list[str], list[str]]:
    active_modalities = []
    missing_modalities = []

    # Read modality scores & metrics
    f_data = modality_results.get("facial", {})
    p_data = modality_results.get("physiological", {})
    b_data = modality_results.get("behavioral", {})
    v_data = modality_results.get("voice", {})

    f_score = get_modality_score(f_data)
    p_score = get_modality_score(p_data)
    b_score = get_modality_score(b_data)
    v_score = get_modality_score(v_data)

    f_conf = get_modality_confidence(f_data)
    p_conf = get_modality_confidence(p_data)
    b_conf = get_modality_confidence(b_data)
    v_conf = get_modality_confidence(v_data)

    f_qual = get_modality_quality(f_data)
    p_qual = get_modality_quality(p_data)
    b_qual = get_modality_quality(b_data)
    v_qual = get_modality_quality(v_data)

    # Availability flags
    f_avail = 1.0 if (f_score is not None and f_data.get("status") != "missing") else 0.0
    p_avail = 1.0 if (p_score is not None and p_data.get("status") != "missing") else 0.0
    b_avail = 1.0 if (b_score is not None and b_data.get("status") != "missing") else 0.0
    v_avail = 1.0 if (v_score is not None and v_data.get("status") != "missing") else 0.0

    # Profile flags & Masking
    comm_ability = str(patient_profile.get("communication_ability", "")).lower()
    mobility = str(patient_profile.get("mobility_status", "")).lower()

    nonverbal = 1.0 if "non-verbal" in comm_ability else 0.0
    intubated = 1.0 if "intubated" in comm_ability else 0.0
    restricted = 1.0 if any(s in mobility for s in ["immobile", "restricted", "bedridden", "paralyzed", "sedated"]) else 0.0
    f_limitation = 1.0 if patient_profile.get("facial_movement_limitation") else 0.0
    s_limitation = 1.0 if patient_profile.get("speech_limitation") else 0.0
    sedated = 1.0 if "sedated" in str(patient_profile.get("sedation_status", "")).lower() else 0.0

    # Apply profile masks
    if nonverbal or intubated or s_limitation:
        v_avail = 0.0
        v_score = 0.0

    if f_limitation:
        f_avail = 0.0

    if restricted:
        b_avail = 0.0

    if f_avail: active_modalities.append("facial")
    else: missing_modalities.append("facial")

    if p_avail: active_modalities.append("physiological")
    else: missing_modalities.append("physiological")

    if b_avail: active_modalities.append("behavioral")
    else: missing_modalities.append("behavioral")

    if v_avail: active_modalities.append("voice")
    else: missing_modalities.append("voice")

    feature_vector = np.array([
        f_score or 0.0, p_score or 0.0, b_score or 0.0, v_score or 0.0,
        f_conf, p_conf, b_conf, v_conf,
        f_qual, p_qual, b_qual, v_qual,
        f_avail, p_avail, b_avail, v_avail,
        nonverbal, intubated, restricted, f_limitation, s_limitation, sedated,
    ], dtype=np.float32)

    return feature_vector, active_modalities, missing_modalities


def fuse_multimodal_results(
    patient_profile: dict[str, Any],
    modality_results: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    model, scaler = load_fusion_model_and_scaler()
    profile_weights = calculate_profile_weights(patient_profile)

    vector, active_modalities, missing_modalities = construct_fusion_feature_vector(
        patient_profile=patient_profile,
        modality_results=modality_results,
    )

    if not active_modalities:
        return {
            "fusion_status": "insufficient_data",
            "pain_related_activity_score": None,
            "pain_related_activity_level": "insufficient_data",
            "confidence": 0.0,
            "active_modalities": [],
            "missing_modalities": list(profile_weights.keys()),
            "modality_contributions": {},
            "profile_weights": profile_weights,
            "fusion_model": "none",
            "calibration_status": "not_calibrated",
            "clinical_validation_status": "not_validated",
        }

    # If trained fusion MLP model exists, run inference
    if model is not None and scaler is not None:
        scale = np.where(scaler["scale"] == 0, 1.0, scaler["scale"])
        scaled_vector = (vector - scaler["mean"]) / scale

        input_tensor = torch.tensor(scaled_vector[None, ...], dtype=torch.float32)

        with torch.no_grad():
            logits = model(input_tensor)
            probs = torch.softmax(logits, dim=1)[0].numpy()

        pred_idx = int(np.argmax(probs))
        pred_class = CLASS_NAMES[pred_idx]
        final_score = float(probs[1] * 0.3 + probs[2] * 0.7 + probs[3] * 1.0)
        final_confidence = float(probs[pred_idx])

        # Ablation for explainability
        ablation_scores = {}
        for idx, mod in enumerate(["facial", "physiological", "behavioral", "voice"]):
            vec_ablated = scaled_vector.copy()
            vec_ablated[idx] = 0.0  # Zero out score
            vec_ablated[idx + 12] = 0.0  # Zero out availability
            with torch.no_grad():
                l_ablated = model(torch.tensor(vec_ablated[None, ...], dtype=torch.float32))
                p_ablated = torch.softmax(l_ablated, dim=1)[0].numpy()
                score_ablated = float(p_ablated[1] * 0.3 + p_ablated[2] * 0.7 + p_ablated[3] * 1.0)
                ablation_scores[f"without_{mod}"] = round(score_ablated, 4)

        modality_contributions = {}
        for mod in active_modalities:
            modality_contributions[mod] = {
                "score": round(get_modality_score(modality_results.get(mod, {})) or 0.0, 4),
                "confidence": round(get_modality_confidence(modality_results.get(mod, {})), 4),
                "quality_score": round(get_modality_quality(modality_results.get(mod, {})), 4),
            }

        return {
            "fusion_status": "completed",
            "pain_related_activity_score": round(final_score, 4),
            "pain_related_activity_level": classify_fusion_score(final_score),
            "confidence": round(final_confidence, 4),
            "active_modalities": active_modalities,
            "missing_modalities": missing_modalities,
            "modality_contributions": modality_contributions,
            "profile_weights": profile_weights,
            "ablation_scores": ablation_scores,
            "fusion_model": "multimodal_fusion_mlp",
            "calibration_status": "calibrated",
            "clinical_validation_status": "prototype_evaluation_pending",
        }

    # Fallback to quality-adjusted weighted fusion
    weighted_scores, weighted_confidences = [], []
    modality_contributions = {}

    for modality, configured_weight in profile_weights.items():
        mod_data = modality_results.get(modality)
        if not mod_data:
            continue
        score = get_modality_score(mod_data)
        quality = get_modality_quality(mod_data)
        confidence = get_modality_confidence(mod_data)

        if score is None or mod_data.get("status") == "missing":
            continue

        effective_weight = configured_weight * quality
        weighted_scores.append(score * effective_weight)
        weighted_confidences.append(confidence * effective_weight)

        modality_contributions[modality] = {
            "score": round(score, 4),
            "configured_weight": round(configured_weight, 4),
            "quality_score": round(quality, 4),
            "effective_weight": round(effective_weight, 4),
            "confidence": round(confidence, 4),
            "weighted_contribution": round(score * effective_weight, 4),
            "model_version": mod_data.get("model_version"),
        }

    total_effective_weight = sum(item["effective_weight"] for item in modality_contributions.values())

    if not weighted_scores or total_effective_weight <= 0:
        return {
            "fusion_status": "insufficient_data",
            "pain_related_activity_score": None,
            "pain_related_activity_level": "insufficient_data",
            "confidence": 0.0,
            "active_modalities": [],
            "missing_modalities": list(profile_weights.keys()),
            "modality_contributions": {},
            "profile_weights": profile_weights,
            "fusion_model": "quality_adjusted_weighted_fusion",
            "calibration_status": "not_calibrated",
            "clinical_validation_status": "prototype_evaluation_pending",
        }

    final_score = sum(weighted_scores) / total_effective_weight
    final_confidence = sum(weighted_confidences) / total_effective_weight
    data_completeness = len(active_modalities) / len(profile_weights)
    final_confidence *= (0.5 + (0.5 * data_completeness))

    final_score = clamp(final_score)
    final_confidence = clamp(final_confidence)

    return {
        "fusion_status": "completed",
        "pain_related_activity_score": round(final_score, 4),
        "pain_related_activity_level": classify_fusion_score(final_score),
        "confidence": round(final_confidence, 4),
        "active_modalities": active_modalities,
        "missing_modalities": missing_modalities,
        "modality_contributions": modality_contributions,
        "profile_weights": profile_weights,
        "fusion_model": "quality_adjusted_weighted_fusion",
        "calibration_status": "not_calibrated",
        "clinical_validation_status": "prototype_evaluation_pending",
    }
