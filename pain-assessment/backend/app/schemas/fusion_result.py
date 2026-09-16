from typing import Any

from pydantic import BaseModel, Field


class FusionResultCreate(BaseModel):
    patient_id: str

    pain_related_activity_score: float | None = None
    pain_related_activity_level: str

    confidence: float

    active_modalities: list[str] = Field(
        default_factory=list
    )

    missing_modalities: list[str] = Field(
        default_factory=list
    )

    modality_contributions: dict[str, Any] = Field(
        default_factory=dict
    )

    profile_weights: dict[str, float] = Field(
        default_factory=dict
    )

    clinical_message: str | None = None


class FusionResultResponse(FusionResultCreate):
    id: str
    created_at: str | None = None
