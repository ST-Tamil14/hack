from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)

from app.core.auth import require_roles
from app.ml.behavioral_predictor import (
    predict_behavioral_video,
)
from app.services.audit_service import create_audit_log


router = APIRouter(
    prefix="/models/behavioral",
    tags=["Behavioral Model"],
)


@router.post("/predict-video")
async def predict_behavioral(
    file: UploadFile = File(...),
    current_user: dict = Depends(require_roles("admin", "doctor", "nurse", "researcher")),
):
    allowed_types = {
        "video/mp4",
        "video/webm",
        "video/quicktime",
        "application/octet-stream",
    }

    if file.content_type and file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Unsupported video type",
        )

    file_bytes = await file.read()

    if len(file_bytes) > 100 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="Video exceeds 100 MB limit",
        )

    temporary_path = None

    try:
        with NamedTemporaryFile(
            suffix=Path(
                file.filename or "video.mp4"
            ).suffix,
            delete=False,
        ) as temporary_file:
            temporary_file.write(file_bytes)
            temporary_path = temporary_file.name

        result = predict_behavioral_video(
            video_path=temporary_path,
        )

        create_audit_log(
            user_id=current_user["id"],
            action="MODEL_PREDICTION_EXECUTED",
            resource_type="behavioral_model",
            details={"filename": file.filename},
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
            detail=f"Behavioral prediction failed: {error}",
        ) from error

    finally:
        if temporary_path:
            temporary_file_path = Path(
                temporary_path
            )

            if temporary_file_path.exists():
                temporary_file_path.unlink()
