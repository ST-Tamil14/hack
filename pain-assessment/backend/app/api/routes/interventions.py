from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import require_roles
from app.schemas.intervention import (
    InterventionCreate,
    InterventionUpdate,
)
from app.services.audit_service import create_audit_log
from app.services.intervention_service import (
    calculate_intervention_response,
    create_intervention,
    evaluate_intervention_response,
    get_intervention,
    get_patient_interventions,
    update_intervention,
)


router = APIRouter(
    prefix="/interventions",
    tags=["Interventions"],
)


@router.post(
    "/patient/{patient_id}",
)
def create_patient_intervention(
    patient_id: str,
    payload: InterventionCreate,
    current_user: dict = Depends(require_roles("admin", "doctor", "nurse")),
):
    try:
        created = create_intervention(
            patient_id=patient_id,
            intervention_data=payload.model_dump(
                exclude_none=True,
                mode="json",
            ),
        )
        i_id = created.get("id") if isinstance(created, dict) else str(getattr(created, "id", ""))

        create_audit_log(
            user_id=current_user["id"],
            action="INTERVENTION_CREATED",
            resource_type="intervention",
            resource_id=str(i_id) if i_id else None,
            patient_id=patient_id,
        )

        return created

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.get(
    "/patient/{patient_id}",
)
def list_patient_interventions(
    patient_id: str,
    limit: int = Query(
        default=50,
        ge=1,
        le=200,
    ),
    current_user: dict = Depends(require_roles("admin", "doctor", "nurse", "researcher", "viewer")),
):
    try:
        return {
            "patient_id": patient_id,
            "records": get_patient_interventions(
                patient_id=patient_id,
                limit=limit,
            ),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.get(
    "/{intervention_id}",
)
def get_single_intervention(
    intervention_id: str,
    current_user: dict = Depends(require_roles("admin", "doctor", "nurse", "researcher", "viewer")),
):
    try:
        record = get_intervention(
            intervention_id
        )

        if record is None:
            raise HTTPException(
                status_code=404,
                detail="Intervention not found",
            )

        return record

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.put(
    "/{intervention_id}",
)
def update_single_intervention(
    intervention_id: str,
    payload: InterventionUpdate,
    current_user: dict = Depends(require_roles("admin", "doctor", "nurse")),
):
    try:
        return update_intervention(
            intervention_id=intervention_id,
            update_data=payload.model_dump(
                exclude_none=True,
                mode="json",
            ),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.post(
    "/{intervention_id}/evaluate-response",
)
def evaluate_response(
    intervention_id: str,
    current_user: dict = Depends(require_roles("admin", "doctor", "nurse")),
):
    try:
        return evaluate_intervention_response(
            intervention_id
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )
