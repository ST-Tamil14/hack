from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.auth import require_roles
from app.schemas.episode import ClinicianReviewCreate, EpisodeObservationCreate
from app.services.episode_service import (
    calculate_trend,
    get_episode_by_id,
    get_patient_episodes,
    process_observation,
    review_episode,
)

router = APIRouter(
    prefix="/episodes",
    tags=["Pain Episodes"],
)


@router.post("/observe")
def observe_episode(
    observation: EpisodeObservationCreate,
    current_user: dict = Depends(
        require_roles("admin", "doctor", "nurse", "researcher")
    ),
):
    return process_observation(
        observation.model_dump()
    )


@router.get("/patient/{patient_id}")
def list_patient_episodes(
    patient_id: str,
    limit: int = Query(default=50, ge=1, le=500),
    current_user: dict = Depends(
        require_roles("admin", "doctor", "nurse", "researcher", "viewer")
    ),
):
    return get_patient_episodes(
        patient_id=patient_id,
        limit=limit,
    )


@router.get("/{episode_id}")
def get_episode(
    episode_id: str,
    current_user: dict = Depends(
        require_roles("admin", "doctor", "nurse", "researcher", "viewer")
    ),
):
    ep = get_episode_by_id(episode_id)
    if not ep:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pain episode '{episode_id}' not found.",
        )
    return ep


@router.post("/{episode_id}/review")
def review_patient_episode(
    episode_id: str,
    review: ClinicianReviewCreate,
    current_user: dict = Depends(
        require_roles("admin", "doctor", "nurse")
    ),
):
    return review_episode(
        episode_id=episode_id,
        clinician_comment=review.clinician_comment,
    )


@router.get("/patient/{patient_id}/trend")
def get_episode_trend(
    patient_id: str,
    previous_score: float = Query(..., ge=0, le=1),
    current_score: float = Query(..., ge=0, le=1),
    current_user: dict = Depends(
        require_roles("admin", "doctor", "nurse", "researcher", "viewer")
    ),
):
    trend_result = calculate_trend(previous_score, current_score)
    return {
        "patient_id": patient_id,
        "previous_score": previous_score,
        "current_score": current_score,
        "trend": trend_result,
        "message": (
            "Observed score is increasing"
            if trend_result == "increasing"
            else "Observed score is decreasing"
            if trend_result == "decreasing"
            else "Observed score is stable"
        ),
    }
