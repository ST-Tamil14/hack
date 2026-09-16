from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class MultimodalFileResponse(BaseModel):
    id: UUID
    patient_id: UUID

    modality: str
    file_type: str

    original_filename: str
    storage_path: str

    file_size_bytes: Optional[int] = None
    content_type: Optional[str] = None

    duration_seconds: Optional[float] = None
    sample_rate: Optional[float] = None

    processing_status: str
    quality_score: Optional[float] = None

    metadata: dict[str, Any] = Field(default_factory=dict)

    uploaded_at: datetime
    processed_at: Optional[datetime] = None
