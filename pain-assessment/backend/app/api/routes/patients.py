from typing import List

from fastapi import APIRouter, Depends, status

from app.core.auth import get_current_user, require_roles
from app.schemas.patient import (
    PatientCreate,
    PatientResponse,
    PatientUpdate,
)
from app.services.audit_service import create_audit_log
from app.services.patient_service import (
    create_patient,
    delete_patient,
    get_all_patients,
    get_patient_by_id,
    update_patient,
)


router = APIRouter(
    prefix="/patients",
    tags=["Patients"],
)


@router.post(
    "/",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_patient_endpoint(
    patient: PatientCreate,
    current_user: dict = Depends(require_roles("admin", "doctor", "nurse")),
):
    created_patient = create_patient(patient)
    patient_id = created_patient.get("id") if isinstance(created_patient, dict) else getattr(created_patient, "id", None)

    create_audit_log(
        user_id=current_user["id"],
        action="PATIENT_CREATED",
        resource_type="patient",
        resource_id=str(patient_id) if patient_id else None,
        patient_id=str(patient_id) if patient_id else None,
    )

    return created_patient


@router.get(
    "/",
    response_model=List[PatientResponse],
)
def get_all_patients_endpoint(
    current_user: dict = Depends(require_roles("admin", "doctor", "nurse", "researcher", "viewer")),
):
    return get_all_patients()


@router.get(
    "/{patient_id}",
    response_model=PatientResponse,
    summary="Get patient by UUID or patient code",
)
def get_patient_endpoint(
    patient_id: str,
    current_user: dict = Depends(require_roles("admin", "doctor", "nurse", "researcher", "viewer")),
):
    """
    Retrieve a patient profile using either their database UUID 
    (e.g., 'c88df461-a713-4850-8cb6-fc5690cc72e0') or patient code (e.g., 'P001').
    """
    return get_patient_by_id(patient_id)


@router.put(
    "/{patient_id}",
    response_model=PatientResponse,
    summary="Update patient by UUID or patient code",
)
def update_patient_endpoint(
    patient_id: str,
    patient: PatientUpdate,
    current_user: dict = Depends(require_roles("admin", "doctor", "nurse")),
):
    """
    Update a patient profile using either their database UUID or patient code.
    """
    updated = update_patient(patient_id, patient)
    pid = updated.get("id") if isinstance(updated, dict) else str(patient_id)

    create_audit_log(
        user_id=current_user["id"],
        action="PATIENT_UPDATED",
        resource_type="patient",
        resource_id=str(pid),
        patient_id=str(pid),
    )

    return updated


@router.delete(
    "/{patient_id}",
    summary="Delete patient by UUID or patient code",
)
def delete_patient_endpoint(
    patient_id: str,
    current_user: dict = Depends(require_roles("admin", "doctor")),
):
    """
    Delete a patient profile using either their database UUID or patient code.
    """
    result = delete_patient(patient_id)

    create_audit_log(
        user_id=current_user["id"],
        action="PATIENT_DELETED",
        resource_type="patient",
        resource_id=str(patient_id),
        patient_id=str(patient_id),
    )

    return result