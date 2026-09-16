from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class PatientCreate(BaseModel):
    patient_code: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Anonymous patient identifier",
    )

    age_group: Optional[str] = None
    clinical_department: Optional[str] = None
    diagnosis: Optional[str] = None
    pain_location: Optional[str] = None
    pain_type: Optional[str] = None
    recent_procedure: Optional[str] = None

    medical_conditions: Optional[str] = None
    medication_status: Optional[str] = None
    sedation_status: Optional[str] = None
    mobility_status: Optional[str] = None
    communication_ability: Optional[str] = None
    preferred_language: Optional[str] = None

    facial_movement_limitation: bool = False
    speech_limitation: bool = False

    initial_pain_score: Optional[float] = Field(
        default=None,
        ge=0,
        le=10,
    )

    clinical_notes: Optional[str] = None


class PatientUpdate(BaseModel):
    age_group: Optional[str] = None
    clinical_department: Optional[str] = None
    diagnosis: Optional[str] = None
    pain_location: Optional[str] = None
    pain_type: Optional[str] = None
    recent_procedure: Optional[str] = None

    medical_conditions: Optional[str] = None
    medication_status: Optional[str] = None
    sedation_status: Optional[str] = None
    mobility_status: Optional[str] = None
    communication_ability: Optional[str] = None
    preferred_language: Optional[str] = None

    facial_movement_limitation: Optional[bool] = None
    speech_limitation: Optional[bool] = None

    initial_pain_score: Optional[float] = Field(
        default=None,
        ge=0,
        le=10,
    )

    clinical_notes: Optional[str] = None


class PatientResponse(PatientCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime
