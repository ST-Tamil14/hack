from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class ClinicianFeedbackCreate(BaseModel):
    clinician_label: Literal[
        "true_positive",
        "false_positive",
        "true_negative",
        "false_negative",
        "uncertain",
    ]
    clinician_feedback: Optional[str] = None


class MonitoringAlertResponse(BaseModel):
    id: str
    patient_id: str
    episode_id: Optional[str] = None
    alert_type: str
    severity: Literal["informational", "review_recommended", "urgent_review"]
    message: str
    score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    status: Literal["open", "acknowledged", "resolved", "dismissed"]
    clinician_label: Optional[str] = None
    clinician_feedback: Optional[str] = None
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[str] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[str] = None
    created_at: str
    updated_at: str
