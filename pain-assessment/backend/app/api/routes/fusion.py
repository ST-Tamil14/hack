from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import require_roles
from app.schemas.fusion import (
    FusionRequest,
    FusionResponse,
)
from app.schemas.fusion_result import (
    FusionResultResponse,
)
from app.services.fusion_result_service import (
    get_latest_fusion_result,
    get_patient_fusion_history,
    save_fusion_result,
)
from app.services.fusion_service import (
    fuse_multimodal_results,
)


router = APIRouter(
    prefix="/fusion",
    tags=["Multimodal Fusion"],
)


@router.post(
    "/calculate",
    response_model=FusionResponse,
)
def calculate_fusion(
    request: FusionRequest,
    current_user: dict = Depends(require_roles("admin", "doctor", "nurse", "researcher")),
):
    result = fuse_multimodal_results(
        patient_profile=request.patient_profile,
        modality_results=request.modality_results,
    )

    return result


@router.post(
    "/calculate-and-save/{patient_id}",
    response_model=FusionResultResponse,
)
def calculate_and_save_fusion(
    patient_id: str,
    request: FusionRequest,
    current_user: dict = Depends(require_roles("admin", "doctor", "nurse", "researcher")),
):
    result = fuse_multimodal_results(
        patient_profile=request.patient_profile,
        modality_results=request.modality_results,
    )

    saved_result = save_fusion_result(
        fusion_result=result,
        patient_id=patient_id,
    )

    return saved_result


@router.get(
    "/patient/{patient_id}/latest",
    response_model=FusionResultResponse,
)
def latest_fusion_result(
    patient_id: str,
    current_user: dict = Depends(require_roles("admin", "doctor", "nurse", "researcher", "viewer")),
):
    result = get_latest_fusion_result(
        patient_id
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "No fusion result found "
                "for this patient."
            ),
        )

    return result


@router.get(
    "/patient/{patient_id}/history",
    response_model=list[FusionResultResponse],
)
def fusion_history(
    patient_id: str,
    limit: int = Query(
        default=50,
        ge=1,
        le=200,
    ),
    current_user: dict = Depends(require_roles("admin", "doctor", "nurse", "researcher", "viewer")),
):
    return get_patient_fusion_history(
        patient_id=patient_id,
        limit=limit,
    )
