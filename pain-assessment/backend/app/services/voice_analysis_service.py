from __future__ import annotations

from pathlib import Path
from typing import Any

from app.ml.pain_phrase_detector import detect_pain_phrases
from app.ml.speech_recognition import transcribe_audio
from app.ml.voice_feature_extractor import extract_voice_features
from app.services.voice_baseline_service import (
    compare_voice_with_baseline,
    voice_is_usable,
)


def analyze_voice_file(
    audio_path: str | Path,
    patient_id: str | None = None,
    patient_profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    audio_path = Path(audio_path)

    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    # 1. Transcribe audio using Whisper
    transcription = transcribe_audio(audio_path)
    text = transcription.get("text", "")
    language = transcription.get("language")

    # 2. Extract acoustic features using librosa
    acoustic_features = extract_voice_features(audio_path)

    # 3. Detect pain phrases
    phrase_analysis = detect_pain_phrases(
        text=text,
        language=language,
    )

    # 4. Extract non-speech vocalization details
    vocal_events = acoustic_features.get("vocal_events", {})
    non_speech_vocalizations = {
        "estimated_vocal_event_count": vocal_events.get("estimated_vocal_event_count", 0),
        "estimated_vocal_event_rate": vocal_events.get("estimated_vocal_event_rate", 0.0),
        "mean_event_duration_seconds": vocal_events.get("event_duration_mean_seconds", 0.0),
    }

    # 5. Speech content group
    speech_content = {
        "text": text,
        "language": language,
        "pain_phrase_count": phrase_analysis.get("pain_phrase_count", 0),
        "pain_phrase_score": phrase_analysis.get("pain_phrase_score", 0.0),
        "matched_phrases": phrase_analysis.get("matched_phrases", []),
    }

    # 6. Baseline comparison (if patient_id provided)
    baseline_result = None
    baseline_deviation_score = 0.0
    if patient_id:
        try:
            baseline_result = compare_voice_with_baseline(
                patient_id=patient_id,
                current_features=acoustic_features,
            )
            baseline_deviation_score = baseline_result.get("overall_voice_deviation") or 0.0
        except Exception:
            baseline_result = None

    # 7. Prototype score components
    vocal_event_score = min((non_speech_vocalizations["estimated_vocal_event_rate"] or 0.0) / 3.0, 1.0)
    pain_phrase_score = speech_content["pain_phrase_score"]
    pause_ratio = acoustic_features.get("pause_ratio") or 0.0
    speech_interruption_score = min(pause_ratio * 1.5, 1.0)
    acoustic_deviation_score = baseline_deviation_score if baseline_result else min((acoustic_features.get("f0_stddev_hz") or 0.0) / 100.0, 1.0)

    # Temporary prototype voice score formula
    preliminary_voice_score = (
        0.40 * acoustic_deviation_score
        + 0.30 * vocal_event_score
        + 0.20 * pain_phrase_score
        + 0.10 * speech_interruption_score
    )

    quality_score = float(acoustic_features.get("quality_score") or 0.75)

    # Check usability against patient profile if supplied
    communication_ability = patient_profile.get("communication_ability") if patient_profile else None
    speech_limitation = bool(patient_profile.get("speech_limitation", False)) if patient_profile else False

    is_usable = voice_is_usable(
        communication_ability=communication_ability,
        speech_limitation=speech_limitation,
        quality_score=quality_score,
    )

    return {
        "speech_content": speech_content,
        "acoustic_features": acoustic_features,
        "non_speech_vocalizations": non_speech_vocalizations,
        "quality_score": round(quality_score, 4),
        "baseline_comparison": baseline_result,
        "modality_result": {
            "pain_related_score": round(max(0.0, min(1.0, preliminary_voice_score)), 4),
            "confidence": round(quality_score if is_usable else 0.0, 4),
            "quality_score": round(quality_score, 4),
            "baseline_deviation": round(baseline_deviation_score, 4),
            "speech_content_score": round(pain_phrase_score, 4),
            "acoustic_deviation_score": round(acoustic_deviation_score, 4),
            "non_speech_vocalization_score": round(vocal_event_score, 4),
            "is_usable": is_usable,
            "model_type": "preliminary_rule_based",
        },
    }
