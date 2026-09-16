from __future__ import annotations

import uuid
from typing import Any

from app.db.supabase_client import supabase
from app.services.fusion_result_service import (
    get_latest_fusion_result,
)
from app.services.kpi_service import (
    get_patient_kpis,
)
from app.services.patient_service import (
    get_patient_by_id,
)
from app.services.vital_service import (
    get_latest_vital,
)


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


def get_recent_processing_jobs(
    patient_id: str,
    limit: int = 10,
) -> list[dict[str, Any]]:
    resolved_id = resolve_patient_uuid(patient_id)
    response = (
        supabase
        .table("processing_jobs")
        .select("*")
        .eq("patient_id", resolved_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )

    return response.data or []


def get_patient_baseline_deviations(
    patient_id: str,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """
    Retrieve stored baseline records.

    Actual current-value comparison can be connected
    later to the latest extracted feature records.
    """
    resolved_id = resolve_patient_uuid(patient_id)
    response = (
        supabase
        .table("patient_baselines")
        .select("*")
        .eq("patient_id", resolved_id)
        .eq("is_active", True)
        .order("updated_at", desc=True)
        .limit(limit)
        .execute()
    )

    return response.data or []


def calculate_data_availability(
    latest_fusion_result: dict[str, Any] | None,
    recent_jobs: list[dict[str, Any]],
) -> dict[str, Any]:
    if latest_fusion_result is None:
        return {
            "status": "no_fusion_result",
            "active_modalities": [],
            "missing_modalities": [
                "facial",
                "physiological",
                "behavioral",
                "voice",
            ],
            "processing_jobs_count": len(
                recent_jobs
            ),
        }

    active_modalities = (
        latest_fusion_result.get(
            "active_modalities",
            [],
        )
    )

    missing_modalities = (
        latest_fusion_result.get(
            "missing_modalities",
            [],
        )
    )

    if not active_modalities:
        status = "insufficient_data"
    elif missing_modalities:
        status = "partial_data"
    else:
        status = "complete_data"

    return {
        "status": status,
        "active_modalities": active_modalities,
        "missing_modalities": missing_modalities,
        "processing_jobs_count": len(
            recent_jobs
        ),
    }


def generate_monitoring_message(
    latest_fusion_result: dict[str, Any] | None,
) -> str:
    if latest_fusion_result is None:
        return (
            "No multimodal assessment is available "
            "for this patient yet."
        )

    level = latest_fusion_result.get(
        "pain_related_activity_level"
    )

    confidence = latest_fusion_result.get(
        "confidence",
        0.0,
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
            "observed. Compare with the patient's "
            "baseline and clinical findings."
        )
    else:
        message = (
            "Low pain-related activity was observed. "
            "This does not exclude pain."
        )

    if confidence < 0.60:
        message += (
            " Confidence is limited."
        )

    return message


def get_patient_monitoring(
    patient_id: str,
) -> dict[str, Any]:
    try:
        patient = get_patient_by_id(
            patient_id
        )
    except Exception:
        patient = None

    if patient is None:
        raise ValueError(
            "Patient was not found."
        )

    try:
        latest_vitals = get_latest_vital(
            patient_id
        )
    except Exception:
        latest_vitals = None

    try:
        active_kpis = get_patient_kpis(
            patient_id_or_code=patient_id,
            active_only=True,
        )
    except Exception:
        active_kpis = []

    latest_fusion_result = (
        get_latest_fusion_result(
            patient_id
        )
    )

    baseline_deviations = (
        get_patient_baseline_deviations(
            patient_id
        )
    )

    recent_jobs = get_recent_processing_jobs(
        patient_id
    )

    data_availability = (
        calculate_data_availability(
            latest_fusion_result=(
                latest_fusion_result
            ),
            recent_jobs=recent_jobs,
        )
    )

    clinical_message = (
        generate_monitoring_message(
            latest_fusion_result
        )
    )

    return {
        "patient": patient,
        "latest_vitals": latest_vitals,
        "active_kpis": active_kpis,
        "latest_fusion_result": (
            latest_fusion_result
        ),
        "baseline_deviations": (
            baseline_deviations
        ),
        "recent_processing_jobs": recent_jobs,
        "data_availability": (
            data_availability
        ),
        "clinical_message": clinical_message,
    }
