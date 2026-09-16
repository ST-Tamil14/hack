from typing import Any

from pydantic import BaseModel, Field


class VoiceBaselineComparisonRequest(BaseModel):
    patient_id: str
    current_features: dict[str, Any] = Field(
        default_factory=dict
    )


class VoiceFeatureDeviation(BaseModel):
    feature_name: str
    current_value: float | None = None
    baseline_mean: float | None = None
    baseline_stddev: float | None = None
    absolute_deviation: float | None = None
    percentage_deviation: float | None = None
    z_score: float | None = None
    category: str


class VoiceBaselineComparisonResponse(BaseModel):
    patient_id: str
    comparisons: list[VoiceFeatureDeviation]
    overall_voice_deviation: float | None = None
    interpretation: str
