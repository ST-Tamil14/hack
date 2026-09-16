from typing import Any

from pydantic import BaseModel, Field


class FacialPredictionRequest(BaseModel):
    sequence: list[list[float]] = Field(
        ...,
        description=(
            "Facial feature sequence with shape "
            "[time_steps, feature_count]."
        ),
    )


class FacialPredictionResponse(BaseModel):
    predicted_class: int
    predicted_label: str
    confidence: float
    probabilities: dict[str, float]
    time_steps: int
    feature_count: int
    model_version: str = "facial-cnn-lstm-v1"


class FacialVideoPredictionResponse(
    FacialPredictionResponse
):
    video_metadata: dict[str, Any]
