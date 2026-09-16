from pathlib import Path
import tempfile
import numpy as np
from scipy.io import wavfile
from fastapi.testclient import TestClient

from app.main import app
from app.ml.pain_phrase_detector import detect_pain_phrases
from app.ml.voice_feature_extractor import extract_voice_features
from app.services.voice_analysis_service import analyze_voice_file
from app.services.voice_baseline_service import (
    calculate_voice_feature_deviation,
    voice_is_usable,
)

client = TestClient(app)


def test_multilingual_pain_phrase_detector():
    # 1. English
    en_result = detect_pain_phrases("My abdomen hurts and I need help", language="en")
    assert en_result["pain_phrase_count"] >= 2
    assert "hurts" in en_result["matched_phrases"]
    assert en_result["pain_phrase_score"] > 0.0

    # 2. Tamil
    ta_result = detect_pain_phrases("எனக்கு வலிக்கிறது உதவி", language="ta")
    assert ta_result["pain_phrase_count"] >= 2
    assert "வலிக்கிறது" in ta_result["matched_phrases"]
    assert ta_result["pain_phrase_score"] > 0.0

    # 3. Hindi
    hi_result = detect_pain_phrases("मुझे बहुत दर्द हो रहा है मदद कीजिए", language="hi")
    assert hi_result["pain_phrase_count"] >= 1
    assert "दर्द" in hi_result["matched_phrases"] or "दर्द हो रहा है" in hi_result["matched_phrases"]
    assert hi_result["pain_phrase_score"] > 0.0


def test_voice_usability_rules():
    # Verbal + high quality -> Usable
    assert voice_is_usable("Fully verbal", False, 0.85) is True

    # Intubated / Non-verbal / Speech limitation -> Unusable
    assert voice_is_usable("Intubated", False, 0.85) is False
    assert voice_is_usable("Non-verbal", False, 0.85) is False
    assert voice_is_usable("Fully verbal", True, 0.85) is False

    # Low quality audio (< 0.40) -> Unusable
    assert voice_is_usable("Fully verbal", False, 0.30) is False


def test_voice_baseline_deviation_calculation():
    # Normal range (< 1.0 z-score)
    normal_dev = calculate_voice_feature_deviation("f0_mean_hz", 200.0, 195.0, 10.0)
    assert normal_dev["category"] == "normal_range"
    assert normal_dev["z_score"] == 0.5

    # Mild deviation (1.0 <= z-score < 2.0)
    mild_dev = calculate_voice_feature_deviation("f0_mean_hz", 210.0, 195.0, 10.0)
    assert mild_dev["category"] == "mild_deviation"
    assert mild_dev["z_score"] == 1.5

    # Marked deviation (>= 2.0 z-score)
    marked_dev = calculate_voice_feature_deviation("f0_mean_hz", 240.0, 195.0, 10.0)
    assert marked_dev["category"] == "marked_deviation"
    assert marked_dev["z_score"] == 4.5

    # Missing value
    missing_dev = calculate_voice_feature_deviation("f0_mean_hz", None, 195.0, 10.0)
    assert missing_dev["category"] == "unavailable"


def test_voice_analysis_pipeline_and_api():
    # Generate synthetic audio tone WAV file (1 sec, 440 Hz)
    sr = 16000
    t = np.linspace(0, 1.0, sr, False)
    tone = np.sin(440 * 2 * np.pi * t)
    audio_int16 = (tone * 32767).astype(np.int16)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
        tmp_wav_path = Path(tmp_wav.name)
        wavfile.write(tmp_wav_path, sr, audio_int16)

    try:
        # 1. Feature Extraction
        features = extract_voice_features(tmp_wav_path)
        assert "rms_mean" in features
        assert "f0_mean_hz" in features
        assert "quality_score" in features

        # 2. Service Analysis
        analysis = analyze_voice_file(tmp_wav_path)
        assert "speech_content" in analysis
        assert "acoustic_features" in analysis
        assert "non_speech_vocalizations" in analysis
        assert "modality_result" in analysis

        # 3. API Endpoint Test
        with open(tmp_wav_path, "rb") as f:
            response = client.post(
                "/voice-analysis/analyze",
                files={"audio": ("test_tone.wav", f, "audio/wav")},
                headers={"Authorization": "Bearer mock-admin-token"},
            )
        assert response.status_code == 200
        data = response.json()
        assert "transcript" in data
        assert "acoustic_features" in data
        assert "non_speech_vocalizations" in data
        assert "quality_score" in data

    finally:
        tmp_wav_path.unlink(missing_ok=True)
