from typing import Any

from pydantic import BaseModel, Field


class AssessmentHistoryResponse(BaseModel):
    id: str
    patient_id: str

    pain_related_activity_score: float | None = None
    pain_related_activity_level: str | None = None

    confidence: float | None = None

    active_modalities: list[str] = Field(
        default_factory=list
    )

    missing_modalities: list[str] = Field(
        default_factory=list
    )

    modality_contributions: dict[str, Any] = Field(
        default_factory=dict
    )

    baseline_comparisons: list[dict[str, Any]] = Field(
        default_factory=list
    )

    trend_direction: str = "unknown"
    previous_score: float | None = None
    score_change: float | None = None

    clinical_message: str | None = None

    assessment_source: str = "automated"
    recorded_at: str | None = None
