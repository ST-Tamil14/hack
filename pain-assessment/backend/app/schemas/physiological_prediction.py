from typing import Any

from pydantic import BaseModel, Field


class PhysiologicalPredictionRequest(BaseModel):
    file_path: str
    window_size: int = Field(default=32, ge=4, le=1000)
    stride: int = Field(default=8, ge=1, le=1000)


class PhysiologicalPredictionResponse(BaseModel):
    predicted_class: str
    predicted_class_index: int
    probabilities: dict[str, float]
    pain_related_score: float
    confidence: float
    feature_names: list[str]
    sample_count: int
    window_count: int
