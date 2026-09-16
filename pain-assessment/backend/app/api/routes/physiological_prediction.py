from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import require_roles
from app.ml.physiological_predictor import (
    predict_physiological_file,
)
from app.schemas.physiological_prediction import (
    PhysiologicalPredictionRequest,
    PhysiologicalPredictionResponse,
)
from app.services.audit_service import create_audit_log


router = APIRouter(
    prefix="/models/physiological",
    tags=["Physiological Model"],
)


@router.post(
    "/predict",
    response_model=PhysiologicalPredictionResponse,
)
def predict_physiological(
    request: PhysiologicalPredictionRequest,
    current_user: dict = Depends(require_roles("admin", "doctor", "nurse", "researcher")),
):
    try:
        result = predict_physiological_file(
            file_path=request.file_path,
            window_size=request.window_size,
            stride=request.stride,
        )

        create_audit_log(
            user_id=current_user["id"],
            action="MODEL_PREDICTION_EXECUTED",
            resource_type="physiological_model",
            details={"file_path": request.file_path},
        )

        return result

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Physiological prediction failed",
        ) from error
