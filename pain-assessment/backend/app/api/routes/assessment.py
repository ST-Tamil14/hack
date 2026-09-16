from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import require_roles
from app.schemas.assessment import (
    AssessmentRunResponse,
)
from app.services.assessment_service import (
    run_assessment,
)
from app.services.audit_service import create_audit_log


router = APIRouter(
    prefix="/assessment",
    tags=["Assessment"],
)


@router.post(
    "/run/{patient_id}",
    response_model=AssessmentRunResponse,
)
def run_patient_assessment(
    patient_id: str,
    current_user: dict = Depends(require_roles("admin", "doctor", "nurse", "researcher")),
):
    try:
        result = run_assessment(patient_id)

        create_audit_log(
            user_id=current_user["id"],
            action="ASSESSMENT_EXECUTED",
            resource_type="assessment",
            resource_id=patient_id,
            patient_id=patient_id,
        )

        return result

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )
