from typing import Any

from pydantic import BaseModel, Field


class AssessmentRunResponse(BaseModel):
    patient_id: str

    modality_results: dict[str, Any]

    fusion_result: dict[str, Any]

    baseline_comparisons: list[dict[str, Any]] = Field(
        default_factory=list
    )

    data_availability: dict[str, Any] = Field(
        default_factory=dict
    )

    clinical_message: str
