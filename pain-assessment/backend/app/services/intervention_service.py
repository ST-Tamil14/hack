from __future__ import annotations

import uuid
from datetime import datetime, timedelta
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


def create_intervention(
    patient_id: str,
    intervention_data: dict[str, Any],
) -> dict[str, Any]:
    resolved_id = resolve_patient_uuid(patient_id)
    record = {
        "patient_id": resolved_id,
        **intervention_data,
        "response_status": "pending",
    }

    response = (
        supabase.table("interventions")
        .insert(record)
        .execute()
    )

    if not response.data:
        raise RuntimeError("Intervention could not be created")

    return response.data[0]


def get_intervention(
    intervention_id: str,
) -> dict[str, Any] | None:
    response = (
        supabase.table("interventions")
        .select("*")
        .eq("id", intervention_id)
        .maybe_single()
        .execute()
    )

    return response.data


def get_patient_interventions(
    patient_id: str,
    limit: int = 50,
) -> list[dict[str, Any]]:
    resolved_id = resolve_patient_uuid(patient_id)
    safe_limit = max(1, min(limit, 200))

    response = (
        supabase.table("interventions")
        .select("*")
        .eq("patient_id", resolved_id)
        .order("started_at", desc=True)
        .limit(safe_limit)
        .execute()
    )

    return response.data or []


def update_intervention(
    intervention_id: str,
    update_data: dict[str, Any],
) -> dict[str, Any]:
    response = (
        supabase.table("interventions")
        .update(update_data)
        .eq("id", intervention_id)
        .execute()
    )

    if not response.data:
        raise ValueError(
            "Intervention not found"
        )

    return response.data[0]


def get_nearest_pre_assessment(
    patient_id: str,
    started_at: datetime,
    window_minutes: int = 30,
) -> dict[str, Any] | None:
    resolved_id = resolve_patient_uuid(patient_id)
    start_time = started_at - timedelta(
        minutes=window_minutes
    )

    response = (
        supabase.table("assessment_history")
        .select("*")
        .eq("patient_id", resolved_id)
        .gte("recorded_at", start_time.isoformat())
        .lte("recorded_at", started_at.isoformat())
        .order("recorded_at", desc=True)
        .limit(1)
        .execute()
    )

    records = response.data or []

    if not records:
        return None

    return records[0]


def get_nearest_post_assessment(
    patient_id: str,
    reference_time: datetime,
    window_minutes: int = 60,
) -> dict[str, Any] | None:
    resolved_id = resolve_patient_uuid(patient_id)
    end_time = reference_time + timedelta(
        minutes=window_minutes
    )

    response = (
        supabase.table("assessment_history")
        .select("*")
        .eq("patient_id", resolved_id)
        .gte("recorded_at", reference_time.isoformat())
        .lte("recorded_at", end_time.isoformat())
        .order("recorded_at", desc=False)
        .limit(1)
        .execute()
    )

    records = response.data or []

    if not records:
        return None

    return records[0]


def calculate_intervention_response(
    pre_score: float | None,
    post_score: float | None,
) -> tuple[str, float | None]:
    if pre_score is None or post_score is None:
        return "insufficient_data", None

    score_change = round(
        post_score - pre_score,
        4,
    )

    threshold = 0.05

    if score_change <= -threshold:
        return "improved", score_change

    if score_change >= threshold:
        return "increased", score_change

    return "unchanged", score_change


def evaluate_intervention_response(
    intervention_id: str,
) -> dict[str, Any]:
    intervention = get_intervention(
        intervention_id
    )

    if intervention is None:
        raise ValueError(
            "Intervention not found"
        )

    patient_id = intervention["patient_id"]

    started_at = datetime.fromisoformat(
        intervention["started_at"].replace(
            "Z",
            "+00:00",
        )
    )

    completed_at_value = intervention.get(
        "completed_at"
    )

    if completed_at_value:
        reference_time = datetime.fromisoformat(
            completed_at_value.replace(
                "Z",
                "+00:00",
            )
        )
    else:
        reference_time = started_at

    pre_assessment = get_nearest_pre_assessment(
        patient_id=patient_id,
        started_at=started_at,
    )

    post_assessment = get_nearest_post_assessment(
        patient_id=patient_id,
        reference_time=reference_time,
    )

    pre_score = None
    post_score = None
    pre_assessment_id = None
    post_assessment_id = None

    if pre_assessment:
        pre_score = pre_assessment.get(
            "pain_related_activity_score"
        )
        pre_assessment_id = pre_assessment.get(
            "id"
        )

    if post_assessment:
        post_score = post_assessment.get(
            "pain_related_activity_score"
        )
        post_assessment_id = post_assessment.get(
            "id"
        )

    response_status, score_change = (
        calculate_intervention_response(
            pre_score=pre_score,
            post_score=post_score,
        )
    )

    updated_record = {
        "pre_assessment_id": pre_assessment_id,
        "post_assessment_id": post_assessment_id,
        "pre_score": pre_score,
        "post_score": post_score,
        "score_change": score_change,
        "response_status": response_status,
    }

    return update_intervention(
        intervention_id=intervention_id,
        update_data=updated_record,
    )
