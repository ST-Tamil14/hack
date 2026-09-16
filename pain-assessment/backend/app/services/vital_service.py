import uuid
from fastapi import HTTPException, status

from app.db.supabase_client import supabase
from app.schemas.vital import (
    VitalSignCreate,
    VitalSignUpdate,
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient '{patient_id_or_code}' not found",
        )

    return response.data["id"]


def create_vital_sign(vital: VitalSignCreate):
    vital_data = vital.model_dump(
        exclude_none=True,
        mode="json",
    )
    vital_data["patient_id"] = resolve_patient_uuid(str(vital.patient_id))

    response = (
        supabase
        .table("vital_signs")
        .insert(vital_data)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Vital sign could not be created",
        )

    return response.data[0]


def get_vital_signs_by_patient(patient_id_or_code: str):
    patient_uuid = resolve_patient_uuid(patient_id_or_code)
    response = (
        supabase
        .table("vital_signs")
        .select("*")
        .eq("patient_id", patient_uuid)
        .order("recorded_at", desc=True)
        .execute()
    )

    return response.data


def get_latest_vital_sign(patient_id_or_code: str):
    patient_uuid = resolve_patient_uuid(patient_id_or_code)
    response = (
        supabase
        .table("vital_signs")
        .select("*")
        .eq("patient_id", patient_uuid)
        .order("recorded_at", desc=True)
        .limit(1)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No vital-sign readings found for this patient",
        )

    return response.data[0]


def get_latest_vital(patient_id_or_code: str):
    patient_uuid = resolve_patient_uuid(patient_id_or_code)
    response = (
        supabase
        .table("vital_signs")
        .select("*")
        .eq("patient_id", patient_uuid)
        .order("recorded_at", desc=True)
        .limit(1)
        .execute()
    )

    if not response.data:
        return None

    return response.data[0]



def get_vital_sign_by_id(vital_id: str):
    response = (
        supabase
        .table("vital_signs")
        .select("*")
        .eq("id", vital_id)
        .maybe_single()
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vital-sign reading not found",
        )

    return response.data


def update_vital_sign(
    vital_id: str,
    vital: VitalSignUpdate,
):
    update_data = vital.model_dump(
        exclude_none=True,
        mode="json",
    )

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No update fields were provided",
        )

    response = (
        supabase
        .table("vital_signs")
        .update(update_data)
        .eq("id", vital_id)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vital-sign reading not found",
        )

    return response.data[0]


def delete_vital_sign(vital_id: str):
    response = (
        supabase
        .table("vital_signs")
        .delete()
        .eq("id", vital_id)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vital-sign reading not found",
        )

    return {
        "message": "Vital-sign reading deleted successfully",
        "vital_id": vital_id,
    }
