from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProcessingJobCreate(BaseModel):
    file_id: str


class ProcessingJobStatusUpdate(BaseModel):
    status: str
    progress: int = Field(default=0, ge=0, le=100)
    error_message: Optional[str] = None
    result_path: Optional[str] = None


class ProcessingJobResponse(BaseModel):
    id: str
    patient_id: str
    file_id: str
    modality: str
    processor_name: str
    status: str
    progress: int
    error_message: Optional[str] = None
    result_path: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
