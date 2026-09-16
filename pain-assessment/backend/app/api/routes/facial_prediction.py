from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)
import numpy as np

from app.core.auth import require_roles
from app.ml.facial_predictor import (
    predict_facial_sequence,
    predict_facial_video,
)
from app.schemas.facial_prediction import (
    FacialPredictionRequest,
    FacialPredictionResponse,
    FacialVideoPredictionResponse,
)
from app.services.audit_service import create_audit_log


router = APIRouter(
    prefix="/models/facial",
    tags=["Facial Model"],
)


@router.post(
    "/predict",
    response_model=FacialPredictionResponse,
)
def predict_facial_pain(
    request: FacialPredictionRequest,
    current_user: dict = Depends(require_roles("admin", "doctor", "nurse", "researcher")),
):
    try:
        sequence = np.asarray(
            request.sequence,
            dtype=np.float32,
        )

        result = predict_facial_sequence(
            sequence
        )

        create_audit_log(
            user_id=current_user["id"],
            action="MODEL_PREDICTION_EXECUTED",
            resource_type="facial_model",
            details={"type": "sequence"},
        )

        return result

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.post(
    "/predict-video",
    response_model=FacialVideoPredictionResponse,
)
async def predict_from_facial_video(
    file: UploadFile = File(...),
    current_user: dict = Depends(require_roles("admin", "doctor", "nurse", "researcher")),
):
    allowed_types = {
        "video/mp4",
        "video/webm",
        "video/quicktime",
    }

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=(
                "Only MP4, WebM, and QuickTime "
                "video files are supported."
            ),
        )

    temporary_path = None

    try:
        file_bytes = await file.read()

        if not file_bytes:
            raise HTTPException(
                status_code=400,
                detail="Uploaded video is empty.",
            )

        if len(file_bytes) > 100 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail=(
                    "Video exceeds the 100 MB "
                    "upload limit."
                ),
            )

        suffix = Path(
            file.filename or "video.mp4"
        ).suffix

        with NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as temporary_file:
            temporary_file.write(
                file_bytes
            )
            temporary_path = (
                temporary_file.name
            )

        result = predict_facial_video(
            video_path=temporary_path,
            window_size=16,
        )

        create_audit_log(
            user_id=current_user["id"],
            action="MODEL_PREDICTION_EXECUTED",
            resource_type="facial_model",
            details={"type": "video", "filename": file.filename},
        )

        return result

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    finally:
        if temporary_path:
            temporary_file_path = Path(
                temporary_path
            )

            if temporary_file_path.exists():
                temporary_file_path.unlink()
