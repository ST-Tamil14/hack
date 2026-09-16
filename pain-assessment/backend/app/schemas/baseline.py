from datetime import datetime
from typing import Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field


class BaselineObservationCreate(BaseModel):
    patient_id: Union[UUID, str] = Field(
        ...,
        description="Patient UUID or patient code (e.g., 'P001')",
    )
    modality: str = Field(
        ...,
        min_length=1,
        max_length=50,
    )
    feature_name: str = Field(
        ...,
        min_length=1,
        max_length=150,
    )
    feature_value: float
    observed_at: Optional[datetime] = None
    source_type: Optional[str] = None

    quality_score: Optional[float] = Field(
        default=None,
        ge=0,
        le=1,
    )


class BaselineResponse(BaseModel):
    id: UUID
    patient_id: UUID
    modality: str
    feature_name: str

    baseline_mean: Optional[float] = None
    baseline_median: Optional[float] = None
    baseline_min: Optional[float] = None
    baseline_max: Optional[float] = None
    baseline_stddev: Optional[float] = None

    sample_count: int

    baseline_start: Optional[datetime] = None
    baseline_end: Optional[datetime] = None

    is_active: bool
    created_at: datetime
    updated_at: datetime


class BaselineDeviationResponse(BaseModel):
    patient_id: UUID
    modality: str
    feature_name: str

    baseline_mean: Optional[float] = None
    current_value: float
    deviation: Optional[float] = None
    deviation_percentage: Optional[float] = None
