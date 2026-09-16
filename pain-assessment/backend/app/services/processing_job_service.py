import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException

from app.db.supabase_client import supabase


MODALITY_PROCESSOR_MAP = {
    "facial": "facial_processor",
    "behavioral": "behavioral_processor",
    "physiological": "physiological_processor",
    "voice": "voice_processor",
}


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
        raise HTTPException(
            status_code=404,
            detail=f"Patient '{patient_id_or_code}' not found",
        )

    return response.data["id"]


def get_processor_name(modality: str) -> str:
    processor_name = MODALITY_PROCESSOR_MAP.get(modality)

    if not processor_name:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported modality: {modality}",
        )

    return processor_name


def create_processing_job(file_id: str) -> dict[str, Any]:
    file_response = (
        supabase.table("multimodal_files")
        .select("*")
        .eq("id", file_id)
        .maybe_single()
        .execute()
    )

    file_data = file_response.data if file_response else None

    if not file_data:
        raise HTTPException(
            status_code=404,
            detail="Uploaded file not found",
        )

    modality = file_data["modality"]
    patient_id = file_data["patient_id"]
    processor_name = get_processor_name(modality)

    existing_job_response = (
        supabase.table("processing_jobs")
        .select("*")
        .eq("file_id", file_id)
        .in_("status", ["queued", "processing", "processed"])
        .execute()
    )

    if existing_job_response.data:
        raise HTTPException(
            status_code=409,
            detail="A processing job already exists for this file",
        )

    job_payload = {
        "patient_id": patient_id,
        "file_id": file_id,
        "modality": modality,
        "processor_name": processor_name,
        "status": "queued",
        "progress": 0,
    }

    response = (
        supabase.table("processing_jobs")
        .insert(job_payload)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=500,
            detail="Failed to create processing job",
        )

    return response.data[0]


def get_processing_job(job_id: str) -> dict[str, Any]:
    response = (
        supabase.table("processing_jobs")
        .select("*")
        .eq("id", job_id)
        .maybe_single()
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=404,
            detail="Processing job not found",
        )

    return response.data


def list_patient_processing_jobs(
    patient_id_or_code: str,
) -> list[dict[str, Any]]:
    patient_uuid = resolve_patient_uuid(patient_id_or_code)
    response = (
        supabase.table("processing_jobs")
        .select("*")
        .eq("patient_id", patient_uuid)
        .order("created_at", desc=True)
        .execute()
    )

    return response.data or []


def update_processing_job(
    job_id: str,
    status: str,
    progress: int = 0,
    error_message: str | None = None,
    result_path: str | None = None,
) -> dict[str, Any]:
    allowed_statuses = {
        "queued",
        "processing",
        "processed",
        "failed",
        "rejected",
    }

    if status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid processing status: {status}",
        )

    update_payload: dict[str, Any] = {
        "status": status,
        "progress": progress,
        "error_message": error_message,
        "result_path": result_path,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    if status == "processing":
        update_payload["started_at"] = (
            datetime.now(timezone.utc).isoformat()
        )

    if status in {"processed", "failed", "rejected"}:
        update_payload["completed_at"] = (
            datetime.now(timezone.utc).isoformat()
        )

    response = (
        supabase.table("processing_jobs")
        .update(update_payload)
        .eq("id", job_id)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=404,
            detail="Processing job not found",
        )

    return response.data[0]
