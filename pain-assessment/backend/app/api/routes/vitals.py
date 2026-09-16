from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.auth import require_roles
from app.schemas.vital import (
    VitalSignCreate,
    VitalSignResponse,
    VitalSignUpdate,
)
from app.services.audit_service import create_audit_log
from app.services.vital_service import (
    create_vital_sign,
    delete_vital_sign,
    get_latest_vital_sign,
    get_vital_sign_by_id,
    get_vital_signs_by_patient,
    update_vital_sign,
)


router = APIRouter(
    prefix="/vitals",
    tags=["Vital Signs"],
)


@router.post(
    "/",
    response_model=VitalSignResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_vital_endpoint(
    vital: VitalSignCreate,
    current_user: dict = Depends(require_roles("admin", "doctor", "nurse")),
):
    recorded = create_vital_sign(vital)
    v_id = recorded.get("id") if isinstance(recorded, dict) else str(getattr(recorded, "id", ""))
    p_id = recorded.get("patient_id") if isinstance(recorded, dict) else str(getattr(recorded, "patient_id", ""))

    create_audit_log(
        user_id=current_user["id"],
        action="VITAL_RECORDED",
        resource_type="vital",
        resource_id=str(v_id) if v_id else None,
        patient_id=str(p_id) if p_id else None,
    )

    return recorded


@router.get(
    "/patient/{patient_id}",
    response_model=List[VitalSignResponse],
    summary="Get all vital sign readings for a patient by UUID or patient code",
)
def get_patient_vitals_endpoint(
    patient_id: str,
    current_user: dict = Depends(require_roles("admin", "doctor", "nurse", "researcher", "viewer")),
):
    return get_vital_signs_by_patient(patient_id)


@router.get(
    "/patient/{patient_id}/latest",
    response_model=VitalSignResponse,
    summary="Get latest vital sign reading for a patient by UUID or patient code",
)
def get_latest_vital_endpoint(
    patient_id: str,
    current_user: dict = Depends(require_roles("admin", "doctor", "nurse", "researcher", "viewer")),
):
    return get_latest_vital_sign(patient_id)


@router.get(
    "/{vital_id}",
    response_model=VitalSignResponse,
)
def get_vital_endpoint(
    vital_id: UUID,
    current_user: dict = Depends(require_roles("admin", "doctor", "nurse", "researcher", "viewer")),
):
    return get_vital_sign_by_id(str(vital_id))


@router.put(
    "/{vital_id}",
    response_model=VitalSignResponse,
)
def update_vital_endpoint(
    vital_id: UUID,
    vital: VitalSignUpdate,
    current_user: dict = Depends(require_roles("admin", "doctor", "nurse")),
):
    return update_vital_sign(str(vital_id), vital)


@router.delete(
    "/{vital_id}",
)
def delete_vital_endpoint(
    vital_id: UUID,
    current_user: dict = Depends(require_roles("admin", "doctor")),
):
    return delete_vital_sign(str(vital_id))
