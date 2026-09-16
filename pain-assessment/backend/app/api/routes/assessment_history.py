from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import require_roles
from app.services.assessment_history_service import (
    get_latest_assessment_history,
    get_patient_assessment_history,
)
from app.services.audit_service import create_audit_log


router = APIRouter(
    prefix="/assessment-history",
    tags=["Assessment History"],
)


@router.get(
    "/patient/{patient_id}",
)
def get_assessment_history(
    patient_id: str,
    limit: int = Query(
        default=50,
        ge=1,
        le=200,
    ),
    current_user: dict = Depends(require_roles("admin", "doctor", "nurse", "researcher", "viewer")),
):
    try:
        records = get_patient_assessment_history(
            patient_id=patient_id,
            limit=limit,
        )

        create_audit_log(
            user_id=current_user["id"],
            action="ASSESSMENT_VIEWED",
            resource_type="assessment_history",
            patient_id=patient_id,
        )

        return {
            "patient_id": patient_id,
            "records": records,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.get(
    "/patient/{patient_id}/latest",
)
def get_latest_assessment(
    patient_id: str,
    current_user: dict = Depends(require_roles("admin", "doctor", "nurse", "researcher", "viewer")),
):
    try:
        record = get_latest_assessment_history(
            patient_id
        )

        if record is None:
            raise HTTPException(
                status_code=404,
                detail="No assessment history found",
            )

        create_audit_log(
            user_id=current_user["id"],
            action="ASSESSMENT_VIEWED",
            resource_type="assessment_history_latest",
            patient_id=patient_id,
        )

        return record

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )
