from datetime import datetime
from typing import Any, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field


class KPICatalogResponse(BaseModel):
    id: UUID
    kpi_name: str
    kpi_category: str
    description: str
    available_features: List[str]
    required_modalities: List[str]
    default_time_window_seconds: int
    is_default: bool
    created_at: datetime


class KPICreate(BaseModel):
    patient_id: Union[UUID, str] = Field(
        ...,
        description="Patient UUID or patient code (e.g., 'P001')",
    )

    kpi_name: str = Field(
        ...,
        min_length=1,
        max_length=150,
    )

    kpi_category: str = Field(
        ...,
        min_length=1,
        max_length=50,
    )

    description: Optional[str] = None

    selected_features: List[str] = Field(
        default_factory=list,
    )

    required_modalities: List[str] = Field(
        default_factory=list,
    )

    time_window_seconds: int = Field(
        default=10,
        ge=1,
        le=3600,
    )

    output_scale: str = "low_medium_high"


class KPIUpdate(BaseModel):
    kpi_name: Optional[str] = None
    kpi_category: Optional[str] = None
    description: Optional[str] = None
    selected_features: Optional[List[str]] = None
    required_modalities: Optional[List[str]] = None

    time_window_seconds: Optional[int] = Field(
        default=None,
        ge=1,
        le=3600,
    )

    output_scale: Optional[str] = None
    is_active: Optional[bool] = None


class KPIResponse(KPICreate):
    id: UUID
    patient_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
