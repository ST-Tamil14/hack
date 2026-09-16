import uuid
from fastapi import HTTPException, status

from app.db.supabase_client import supabase
from app.schemas.patient import PatientCreate, PatientUpdate


def is_valid_uuid(val: str) -> bool:
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


def create_patient(patient: PatientCreate):
    patient_data = patient.model_dump(exclude_none=True)

    response = (
        supabase
        .table("patients")
        .insert(patient_data)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Patient could not be created",
        )

    return response.data[0]


def get_all_patients():
    response = (
        supabase
        .table("patients")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )

    return response.data


def get_patient_by_id(identifier: str):
    query = supabase.table("patients").select("*")
    if is_valid_uuid(identifier):
        query = query.eq("id", identifier)
    else:
        query = query.eq("patient_code", identifier)

    response = query.maybe_single().execute()

    if not response or not getattr(response, "data", None):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient '{identifier}' not found",
        )

    return response.data


def update_patient(identifier: str, patient: PatientUpdate):
    update_data = patient.model_dump(exclude_none=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No update fields were provided",
        )

    query = supabase.table("patients").update(update_data)
    if is_valid_uuid(identifier):
        query = query.eq("id", identifier)
    else:
        query = query.eq("patient_code", identifier)

    response = query.execute()

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient '{identifier}' not found or could not be updated",
        )

    return response.data[0]


def delete_patient(identifier: str):
    query = supabase.table("patients").delete()
    if is_valid_uuid(identifier):
        query = query.eq("id", identifier)
    else:
        query = query.eq("patient_code", identifier)

    response = query.execute()

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient '{identifier}' not found",
        )

    return {
        "message": "Patient deleted successfully",
        "patient_id": identifier,
    }
