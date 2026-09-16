from __future__ import annotations

import uuid
from typing import Any

from app.db.supabase_client import supabase


def is_valid_uuid(val: str) -> bool:
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


def resolve_patient_uuid(patient_id_or_code: str) -> str:
    if is_valid_uuid(patient_id_or_code):
        return str(patient_id_or_code)

    response = (
        supabase
        .table("patients")
        .select("id")
        .eq("patient_code", patient_id_or_code)
        .maybe_single()
        .execute()
    )

    if not response or not response.data:
        return patient_id_or_code

    return response.data["id"]


def get_previous_assessment(
    patient_id: str,
) -> dict[str, Any] | None:
    resolved_id = resolve_patient_uuid(patient_id)
    response = (
        supabase.table("assessment_history")
        .select("*")
        .eq("patient_id", resolved_id)
        .order("recorded_at", desc=True)
        .limit(1)
        .execute()
    )

    records = response.data or []

    if not records:
        return None

    return records[0]


def calculate_trend(
    current_score: float | None,
    previous_score: float | None,
) -> tuple[str, float | None]:
    if current_score is None or previous_score is None:
        return "unknown", None

    score_change = round(
        current_score - previous_score,
        4,
    )

    threshold = 0.05

    if score_change >= threshold:
        return "increasing", score_change

    if score_change <= -threshold:
        return "decreasing", score_change

    return "stable", score_change


def save_assessment_history(
    patient_id: str,
    assessment_result: dict[str, Any],
    fusion_result_id: str | None = None,
) -> dict[str, Any]:
    resolved_id = resolve_patient_uuid(patient_id)

    current_score = assessment_result.get(
        "fusion_result",
        {},
    ).get(
        "pain_related_activity_score"
    )

    previous_assessment = get_previous_assessment(
        resolved_id
    )

    previous_score = None

    if previous_assessment:
        previous_score = previous_assessment.get(
            "pain_related_activity_score"
        )

    trend_direction, score_change = calculate_trend(
        current_score=current_score,
        previous_score=previous_score,
    )

    fusion_result = assessment_result.get(
        "fusion_result",
        {},
    )

    history_record = {
        "patient_id": resolved_id,
        "fusion_result_id": fusion_result_id,
        "pain_related_activity_score": current_score,
        "pain_related_activity_level": fusion_result.get(
            "pain_related_activity_level"
        ),
        "confidence": fusion_result.get(
            "confidence"
        ),
        "active_modalities": fusion_result.get(
            "active_modalities",
            [],
        ),
        "missing_modalities": fusion_result.get(
            "missing_modalities",
            [],
        ),
        "modality_contributions": fusion_result.get(
            "modality_contributions",
            {},
        ),
        "baseline_comparisons": assessment_result.get(
            "baseline_comparisons",
            [],
        ),
        "trend_direction": trend_direction,
        "previous_score": previous_score,
        "score_change": score_change,
        "clinical_message": assessment_result.get(
            "clinical_message"
        ),
        "assessment_source": "automated",
    }

    response = (
        supabase.table("assessment_history")
        .insert(history_record)
        .execute()
    )

    if not response.data:
        raise RuntimeError("Failed to save assessment history")

    return response.data[0]


def get_patient_assessment_history(
    patient_id: str,
    limit: int = 50,
) -> list[dict[str, Any]]:
    resolved_id = resolve_patient_uuid(patient_id)
    safe_limit = max(1, min(limit, 200))

    response = (
        supabase.table("assessment_history")
        .select("*")
        .eq("patient_id", resolved_id)
        .order("recorded_at", desc=True)
        .limit(safe_limit)
        .execute()
    )

    return response.data or []


def get_latest_assessment_history(
    patient_id: str,
) -> dict[str, Any] | None:
    records = get_patient_assessment_history(
        patient_id=patient_id,
        limit=1,
    )

    if not records:
        return None

    return records[0]
