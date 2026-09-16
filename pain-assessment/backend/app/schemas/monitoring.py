from typing import Any

from pydantic import BaseModel, Field


class MonitoringResponse(BaseModel):
    patient: dict[str, Any]
    latest_vitals: dict[str, Any] | None = None
    active_kpis: list[dict[str, Any]] = Field(
        default_factory=list
    )
    latest_fusion_result: dict[str, Any] | None = None
    baseline_deviations: list[dict[str, Any]] = Field(
        default_factory=list
    )
    recent_processing_jobs: list[dict[str, Any]] = Field(
        default_factory=list
    )
    data_availability: dict[str, Any] = Field(
        default_factory=dict
    )
    clinical_message: str
