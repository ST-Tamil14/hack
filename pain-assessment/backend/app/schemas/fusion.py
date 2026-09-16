from typing import Any

from pydantic import BaseModel, Field


class ModalityResult(BaseModel):
    pain_related_score: float
    confidence: float
    quality_score: float
    predicted_label: str | None = None
    model_version: str | None = None
    raw_prediction: dict | None = None


class FusionRequest(BaseModel):
    patient_id: str

    patient_profile: dict[str, Any] = Field(
        default_factory=dict
    )

    modality_results: dict[
        str,
        dict[str, Any],
    ] = Field(
        default_factory=dict
    )


class FusionResponse(BaseModel):
    fusion_status: str
    pain_related_activity_score: float | None
    pain_related_activity_level: str
    confidence: float

    active_modalities: list[str]
    missing_modalities: list[str]

    modality_contributions: dict[str, Any]
    profile_weights: dict[str, float]
