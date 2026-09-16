from datetime import datetime

from pydantic import BaseModel, Field


class InterventionCreate(BaseModel):
    intervention_type: str = Field(
        min_length=1,
        max_length=100,
    )

    intervention_name: str | None = Field(
        default=None,
        max_length=150,
    )

    description: str | None = None

    started_at: datetime
    completed_at: datetime | None = None

    administered_by: str | None = None

    clinician_comment: str | None = None


class InterventionUpdate(BaseModel):
    intervention_name: str | None = None
    description: str | None = None
    completed_at: datetime | None = None
    clinician_comment: str | None = None


class InterventionResponse(BaseModel):
    id: str
    patient_id: str

    intervention_type: str
    intervention_name: str | None = None
    description: str | None = None

    started_at: datetime
    completed_at: datetime | None = None

    pre_assessment_id: str | None = None
    post_assessment_id: str | None = None

    pre_score: float | None = None
    post_score: float | None = None
    score_change: float | None = None

    response_status: str = "pending"
    clinician_comment: str | None = None

    created_at: datetime | None = None
    updated_at: datetime | None = None
