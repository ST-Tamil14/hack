from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class EpisodeObservationCreate(BaseModel):
    patient_id: str
    pain_related_activity_score: float = Field(
        ge=0,
        le=1,
    )
    confidence: float = Field(
        ge=0,
        le=1,
    )
    active_modalities: list[str] = []
    missing_modalities: list[str] = []
    modality_contributions: dict[str, Any] = {}
    data_quality: float | None = Field(
        default=None,
        ge=0,
        le=1,
    )
    observed_at: datetime | None = None


class EpisodeResponse(BaseModel):
    id: str
    patient_id: str
    started_at: datetime | str
    ended_at: datetime | str | None = None
    duration_seconds: float | None = None
    peak_score: float | None = None
    average_score: float | None = None
    episode_level: str
    confidence: float | None = None
    status: str
    clinician_reviewed: bool | None = False
    clinician_comment: str | None = None


class ClinicianReviewCreate(BaseModel):
    clinician_comment: str
    clinician_reviewed: bool = True
