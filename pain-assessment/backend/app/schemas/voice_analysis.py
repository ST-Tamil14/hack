from typing import Any

from pydantic import BaseModel, Field


class VoiceAnalysisResponse(BaseModel):
    file_id: str | None = None
    transcript: str
    language: str | None = None
    speech_content: dict[str, Any] = Field(default_factory=dict)
    pain_phrase_analysis: dict[str, Any] = Field(default_factory=dict)
    acoustic_features: dict[str, Any] = Field(default_factory=dict)
    non_speech_vocalizations: dict[str, Any] = Field(default_factory=dict)
    quality_score: float | None = None
    modality_result: dict[str, Any] = Field(default_factory=dict)
