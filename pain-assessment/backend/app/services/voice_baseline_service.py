from __future__ import annotations

from typing import Any

from app.db.supabase_client import supabase


VOICE_NUMERIC_FEATURES = [
    "rms_mean",
    "rms_stddev",
    "f0_mean_hz",
    "f0_stddev_hz",
    "pause_ratio",
    "voiced_ratio",
    "spectral_centroid_mean",
    "estimated_vocal_event_count",
    "estimated_vocal_event_rate",
]


def get_nested_value(
    data: dict[str, Any],
    path: str,
) -> Any:
    current: Any = data

    for part in path.split("."):
        if not isinstance(current, dict):
            return None

        current = current.get(part)

    return current


def voice_is_usable(
    communication_ability: str | None,
    speech_limitation: bool,
    quality_score: float | None,
) -> bool:
    """
    Evaluate whether voice modality audio and patient profile permit reliable voice usage.
    """
    unavailable_abilities = {
        "non-verbal",
        "intubated",
        "unable_to_speak",
    }

    if communication_ability:
        normalized_ability = communication_ability.lower()

        if any(ability in normalized_ability for ability in unavailable_abilities):
            return False

    if speech_limitation:
        return False

    if quality_score is not None and quality_score < 0.40:
        return False

    return True


def get_patient_baseline_record(
    patient_id: str,
    modality: str = "voice",
    feature_name: str = "f0_mean_hz",
) -> dict[str, Any] | None:
    try:
        response = (
            supabase.table("patient_baselines")
            .select("*")
            .eq("patient_id", patient_id)
            .eq("modality", modality)
            .eq("feature_name", feature_name)
            .maybe_single()
            .execute()
        )

        return response.data if response else None
    except Exception:
        return None


def calculate_voice_feature_deviation(
    feature_name: str,
    current_value: float | None,
    baseline_mean: float | None,
    baseline_stddev: float | None,
) -> dict[str, Any]:
    if current_value is None or baseline_mean is None:
        return {
            "feature_name": feature_name,
            "current_value": current_value,
            "baseline_mean": baseline_mean,
            "baseline_stddev": baseline_stddev,
            "absolute_deviation": None,
            "percentage_deviation": None,
            "z_score": None,
            "category": "unavailable",
        }

    abs_deviation = abs(current_value - baseline_mean)

    pct_deviation = (
        (abs_deviation / abs(baseline_mean) * 100.0)
        if baseline_mean != 0
        else 0.0
    )

    stddev_effective = baseline_stddev if (baseline_stddev and baseline_stddev > 0) else 1.0
    z_score = abs(current_value - baseline_mean) / stddev_effective

    if z_score < 1.0:
        category = "normal_range"
    elif z_score < 2.0:
        category = "mild_deviation"
    else:
        category = "marked_deviation"

    return {
        "feature_name": feature_name,
        "current_value": round(float(current_value), 4),
        "baseline_mean": round(float(baseline_mean), 4),
        "baseline_stddev": round(float(baseline_stddev), 4) if baseline_stddev is not None else None,
        "absolute_deviation": round(float(abs_deviation), 4),
        "percentage_deviation": round(float(pct_deviation), 2),
        "z_score": round(float(z_score), 2),
        "category": category,
    }


def compare_voice_with_baseline(
    patient_id: str,
    current_features: dict[str, Any],
) -> dict[str, Any]:
    comparisons: list[dict[str, Any]] = []
    z_scores: list[float] = []

    for feature_name in VOICE_NUMERIC_FEATURES:
        current_val = get_nested_value(current_features, feature_name)

        if current_val is None and feature_name == "estimated_vocal_event_count":
            current_val = get_nested_value(
                current_features,
                "non_speech_vocalizations.estimated_vocal_event_count",
            )

        if current_val is None and feature_name == "estimated_vocal_event_rate":
            current_val = get_nested_value(
                current_features,
                "non_speech_vocalizations.estimated_vocal_event_rate",
            )

        if current_val is None:
            continue

        try:
            current_val_float = float(current_val)
        except (ValueError, TypeError):
            continue

        baseline_record = get_patient_baseline_record(
            patient_id=patient_id,
            modality="voice",
            feature_name=feature_name,
        )

        b_mean = baseline_record.get("baseline_mean") if baseline_record else None
        b_std = baseline_record.get("baseline_stddev") if baseline_record else None

        dev = calculate_voice_feature_deviation(
            feature_name=feature_name,
            current_value=current_val_float,
            baseline_mean=float(b_mean) if b_mean is not None else None,
            baseline_stddev=float(b_std) if b_std is not None else None,
        )

        comparisons.append(dev)

        if dev.get("z_score") is not None:
            z_scores.append(dev["z_score"])

    if not z_scores:
        overall_deviation = 0.0
        interpretation = "Voice baseline comparisons unavailable for patient."
    else:
        max_z = max(z_scores)
        mean_z = sum(z_scores) / len(z_scores)
        overall_deviation = round(min(max((mean_z * 0.5 + max_z * 0.5) / 3.0, 0.0), 1.0), 4)

        if overall_deviation > 0.60:
            interpretation = "Voice features show marked deviation from the personal baseline."
        elif overall_deviation > 0.30:
            interpretation = "Voice features show mild deviation from the personal baseline."
        else:
            interpretation = "Voice features are within normal range relative to the personal baseline."

    return {
        "patient_id": patient_id,
        "comparisons": comparisons,
        "overall_voice_deviation": overall_deviation,
        "interpretation": interpretation,
    }
