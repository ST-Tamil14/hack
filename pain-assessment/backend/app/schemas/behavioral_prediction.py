from typing import Any

from pydantic import BaseModel, Field


class BehavioralPredictionResponse(BaseModel):
    predicted_class: str
    predicted_class_index: int
    probabilities: dict[str, float]
    pain_related_score: float
    confidence: float
    feature_names: list[str]
    processed_frames: int
    detected_poses: int
    pose_detection_rate: float
    duration_seconds: float
