from datetime import datetime
from typing import Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field


class VitalSignCreate(BaseModel):
    patient_id: Union[UUID, str] = Field(
        ...,
        description="Patient UUID or patient code (e.g., 'P001')",
    )

    heart_rate: Optional[float] = Field(
        default=None,
        ge=0,
        le=300,
    )

    systolic_bp: Optional[float] = Field(
        default=None,
        ge=0,
        le=300,
    )

    diastolic_bp: Optional[float] = Field(
        default=None,
        ge=0,
        le=200,
    )

    respiratory_rate: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
    )

    spo2: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
    )

    temperature: Optional[float] = Field(
        default=None,
        ge=20,
        le=50,
    )

    hrv: Optional[float] = Field(
        default=None,
        ge=0,
    )

    eda_gsr: Optional[float] = Field(
        default=None,
        ge=0,
    )

    skin_temperature: Optional[float] = Field(
        default=None,
        ge=0,
        le=50,
    )

    perfusion_index: Optional[float] = Field(
        default=None,
        ge=0,
    )

    consciousness_status: Optional[str] = None
    sedation_status: Optional[str] = None

    clinical_pain_score: Optional[float] = Field(
        default=None,
        ge=0,
        le=10,
    )

    recorded_at: Optional[datetime] = None


class VitalSignUpdate(BaseModel):
    heart_rate: Optional[float] = Field(
        default=None,
        ge=0,
        le=300,
    )

    systolic_bp: Optional[float] = Field(
        default=None,
        ge=0,
        le=300,
    )

    diastolic_bp: Optional[float] = Field(
        default=None,
        ge=0,
        le=200,
    )

    respiratory_rate: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
    )

    spo2: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
    )

    temperature: Optional[float] = Field(
        default=None,
        ge=20,
        le=50,
    )

    hrv: Optional[float] = Field(
        default=None,
        ge=0,
    )

    eda_gsr: Optional[float] = Field(
        default=None,
        ge=0,
    )

    skin_temperature: Optional[float] = Field(
        default=None,
        ge=0,
        le=50,
    )

    perfusion_index: Optional[float] = Field(
        default=None,
        ge=0,
    )

    consciousness_status: Optional[str] = None
    sedation_status: Optional[str] = None

    clinical_pain_score: Optional[float] = Field(
        default=None,
        ge=0,
        le=10,
    )

    recorded_at: Optional[datetime] = None


class VitalSignResponse(VitalSignCreate):
    id: UUID
    patient_id: UUID
    created_at: datetime
