from fastapi import APIRouter, Depends, Query

from app.core.auth import require_roles
from app.schemas.evaluation import ModelEvaluationCreate
from app.services.evaluation_service import (
    get_model_evaluations,
    save_model_evaluation,
)

router = APIRouter(
    prefix="/evaluations",
    tags=["Model Evaluations"],
)


@router.post("/")
def create_evaluation(
    evaluation: ModelEvaluationCreate,
    current_user: dict = Depends(
        require_roles("admin", "researcher")
    ),
):
    return save_model_evaluation(
        evaluation.model_dump(),
        evaluated_by=current_user.get("id"),
    )


@router.get("/")
def list_evaluations(
    model_name: str | None = Query(default=None),
    modality: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    current_user: dict = Depends(
        require_roles("admin", "doctor", "researcher")
    ),
):
    return get_model_evaluations(
        model_name=model_name,
        modality=modality,
        limit=limit,
    )
