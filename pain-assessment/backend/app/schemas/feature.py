from typing import Any, Optional

from pydantic import BaseModel


class FeatureExtractionResponse(BaseModel):
    id: Optional[str] = None
    patient_id: str
    file_id: str
    processing_job_id: Optional[str] = None
    modality: str
    feature_version: str
    features: dict[str, Any]
    feature_count: int
    quality_score: Optional[float] = None
    extraction_status: str
