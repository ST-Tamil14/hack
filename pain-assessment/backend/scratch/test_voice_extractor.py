import os
import soundfile as sf
import numpy as np
from app.ml.voice_feature_extractor import extract_voice_features

def test_voice_vocal_events():
    test_audio_path = "scratch/sample_voice_events.wav"
    os.makedirs("scratch", exist_ok=True)

    sample_rate = 16000
    t = np.linspace(0, 3, 3 * sample_rate, endpoint=False)
    # Generate audio with bursts (short bursts and longer sustained tones)
    audio_signal = np.zeros_like(t)
    
    # Burst 1: 0.1s to 0.4s (short burst)
    idx1 = (t >= 0.1) & (t < 0.4)
    audio_signal[idx1] = 0.8 * np.sin(2 * np.pi * 300 * t[idx1])
    
    # Burst 2: 1.0s to 1.8s (long event with low frequency energy <500Hz)
    idx2 = (t >= 1.0) & (t < 1.8)
    audio_signal[idx2] = 0.9 * np.sin(2 * np.pi * 220 * t[idx2])

    sf.write(test_audio_path, audio_signal, sample_rate)

    try:
        features = extract_voice_features(test_audio_path)
        print("Voice extraction with vocal events successful!")
        assert "vocal_events" in features, "vocal_events missing from features!"
        
        events = features["vocal_events"]
        print("Extracted vocal_events:", events)

        expected_event_keys = [
            "high_energy_event_count", "low_frequency_event_count",
            "short_vocal_burst_count", "long_vocal_event_count",
            "estimated_vocal_event_count", "estimated_vocal_event_rate",
            "event_duration_mean_seconds", "event_duration_max_seconds"
        ]
        for key in expected_event_keys:
            assert key in events, f"Missing key in vocal_events: {key}"
            
        print("All expected vocal event keys verified successfully!")
    finally:
        if os.path.exists(test_audio_path):
            os.remove(test_audio_path)

if __name__ == "__main__":
    test_voice_vocal_events()
