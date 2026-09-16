from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.core.auth import require_roles
from app.services.audit_service import create_audit_log
from app.services.voice_analysis_service import analyze_voice_file


router = APIRouter(
    prefix="/voice-analysis",
    tags=["Voice Analysis"],
)


@router.post("/analyze")
async def analyze_voice(
    audio: UploadFile = File(...),
    current_user: dict = Depends(require_roles("admin", "doctor", "nurse", "researcher")),
):
    allowed_types = {
        "audio/wav",
        "audio/mpeg",
        "audio/webm",
        "audio/x-wav",
        "audio/mp3",
        "audio/ogg",
        "application/octet-stream",
    }

    if audio.content_type and audio.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Unsupported audio format",
        )

    audio_bytes = await audio.read()

    if not audio_bytes:
        raise HTTPException(
            status_code=400,
            detail="Empty audio file",
        )

    suffix = Path(audio.filename or "audio.wav").suffix or ".wav"

    with NamedTemporaryFile(
        suffix=suffix,
        delete=False,
    ) as temporary_file:
        temporary_file.write(audio_bytes)
        temporary_path = temporary_file.name

    try:
        result = analyze_voice_file(temporary_path)

        create_audit_log(
            user_id=current_user["id"],
            action="MODEL_PREDICTION_EXECUTED",
            resource_type="voice_model",
            details={"filename": audio.filename},
        )

        return {
            "file_id": None,
            "transcript": result["speech_content"]["text"],
            "language": result["speech_content"]["language"],
            "speech_content": result["speech_content"],
            "pain_phrase_analysis": {
                "pain_phrase_count": result["speech_content"]["pain_phrase_count"],
                "pain_phrase_score": result["speech_content"]["pain_phrase_score"],
                "matched_phrases": result["speech_content"]["matched_phrases"],
            },
            "acoustic_features": result["acoustic_features"],
            "non_speech_vocalizations": result["non_speech_vocalizations"],
            "quality_score": result["quality_score"],
            "modality_result": result["modality_result"],
        }

    finally:
        Path(temporary_path).unlink(missing_ok=True)
