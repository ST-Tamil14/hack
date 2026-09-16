from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import require_roles
from app.services.dataset_service import (
    prepare_facial_dataset,
)


router = APIRouter(
    prefix="/datasets",
    tags=["Datasets"],
)


@router.post(
    "/facial/prepare",
)
def prepare_facial_dataset_route(
    annotation_filename: str,
    current_user: dict = Depends(require_roles("admin", "researcher")),
):
    try:
        return prepare_facial_dataset(
            annotation_filename
        )

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
