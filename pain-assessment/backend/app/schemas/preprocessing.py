from typing import Optional

from pydantic import BaseModel


class PreprocessingResult(BaseModel):
    file_id: str
    modality: str
    file_type: str
    file_size_bytes: Optional[int] = None

    duration_seconds: Optional[float] = None
    frame_count: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    channels: Optional[int] = None
    sample_count: Optional[int] = None

    quality_score: Optional[float] = None
    preprocessing_status: str
    message: Optional[str] = None
