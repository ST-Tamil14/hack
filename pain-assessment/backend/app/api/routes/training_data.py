from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import require_roles
from app.ml.facial_sequence_builder import (
    prepare_facial_sequences,
)


router = APIRouter(
    prefix="/training-data",
    tags=["Training Data"],
)


@router.post(
    "/facial/prepare-sequences",
)
def prepare_facial_training_sequences(
    window_size: int = Query(
        default=16,
        ge=4,
        le=128,
    ),
    stride: int = Query(
        default=8,
        ge=1,
        le=128,
    ),
    current_user: dict = Depends(require_roles("admin", "researcher")),
):
    try:
        return prepare_facial_sequences(
            window_size=window_size,
            stride=stride,
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
