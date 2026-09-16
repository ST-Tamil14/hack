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


def generate_clinical_message(
    fusion_result: dict[str, Any],
) -> str:
    """
    Generate a cautious clinical-support message.
    """

    level = fusion_result.get(
        "pain_related_activity_level"
    )

    confidence = fusion_result.get(
        "confidence",
        0.0,
    )

    missing_modalities = fusion_result.get(
        "missing_modalities",
        [],
    )

    if level == "insufficient_data":
        return (
            "Insufficient reliable data for "
            "pain-related estimation."
        )

    if level == "high":
        message = (
            "Observed changes may indicate increased "
            "pain-related activity. Clinical "
            "reassessment is recommended."
        )
    elif level == "moderate":
        message = (
            "Moderate pain-related activity was "
            "observed. Consider clinical reassessment "
            "and comparison with the patient's baseline."
        )
    else:
        message = (
            "Low pain-related activity was observed. "
            "This does not exclude pain and should be "
            "interpreted with clinical findings."
        )

    if confidence < 0.60:
        message += (
            " Confidence is limited because the "
            "available evidence is uncertain."
        )

    if missing_modalities:
        message += (
            " Missing modalities: "
            + ", ".join(missing_modalities)
            + "."
        )

    return message


def save_fusion_result(
    fusion_result: dict[str, Any],
    patient_id: str,
) -> dict[str, Any]:
    """
    Save a fusion result to Supabase.
    """
    resolved_patient_id = resolve_patient_uuid(patient_id)

    clinical_message = generate_clinical_message(
        fusion_result
    )

    payload = {
        "patient_id": resolved_patient_id,
        "pain_related_activity_score": (
            fusion_result.get(
                "pain_related_activity_score"
            )
        ),
        "pain_related_activity_level": (
            fusion_result.get(
                "pain_related_activity_level"
            )
        ),
        "confidence": fusion_result.get(
            "confidence",
            0.0,
        ),
        "active_modalities": (
            fusion_result.get(
                "active_modalities",
                [],
            )
        ),
        "missing_modalities": (
            fusion_result.get(
                "missing_modalities",
                [],
            )
        ),
        "modality_contributions": (
            fusion_result.get(
                "modality_contributions",
                {},
            )
        ),
        "profile_weights": (
            fusion_result.get(
                "profile_weights",
                {},
            )
        ),
        "clinical_message": clinical_message,
    }

    response = (
        supabase
        .table("fusion_results")
        .insert(payload)
        .execute()
    )

    if not response.data:
        raise RuntimeError(
            "Fusion result could not be saved."
        )

    return response.data[0]


def get_latest_fusion_result(
    patient_id: str,
) -> dict[str, Any] | None:
    """
    Retrieve the latest fusion result for a patient.
    """
    resolved_patient_id = resolve_patient_uuid(patient_id)

    response = (
        supabase
        .table("fusion_results")
        .select("*")
        .eq("patient_id", resolved_patient_id)
        .order(
            "created_at",
            desc=True,
        )
        .limit(1)
        .execute()
    )

    if not response.data:
        return None

    return response.data[0]


def get_patient_fusion_history(
    patient_id: str,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """
    Retrieve recent fusion results for a patient.
    """
    resolved_patient_id = resolve_patient_uuid(patient_id)

    safe_limit = max(
        1,
        min(limit, 200),
    )

    response = (
        supabase
        .table("fusion_results")
        .select("*")
        .eq("patient_id", resolved_patient_id)
        .order(
            "created_at",
            desc=True,
        )
        .limit(safe_limit)
        .execute()
    )

    return response.data or []
