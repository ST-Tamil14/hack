from app.services.voice_baseline_service import (
    compare_voice_features_with_baseline,
    calculate_percentage_deviation,
    classify_deviation,
)

def test_voice_baseline_service():
    current_features = {
        "rms_mean": 0.14,
        "rms_stddev": 0.07,
        "zero_crossing_rate_mean": 0.12,
        "spectral_centroid_mean": 2200.5,
        "spectral_bandwidth_mean": 2400.2,
        "spectral_rolloff_mean": 4300.4,
        "f0_mean_hz": 210.5,
        "f0_stddev_hz": 45.2,
        "voiced_ratio": 0.52,
        "pause_ratio": 0.48,
        "pause_count": 12,
        "duration_seconds": 10.0,
        "vocal_events": {
            "estimated_vocal_event_count": 9
        }
    }

    baseline_features = {
        "rms_mean": {
            "baseline_mean": 0.08,
            "baseline_stddev": 0.02
        },
        "f0_mean_hz": {
            "baseline_mean": 175.0,
            "baseline_stddev": 20.0
        },
        "pause_ratio": {
            "baseline_mean": 0.25,
            "baseline_stddev": 0.08
        },
        "estimated_vocal_event_count": {
            "baseline_mean": 3.0,
            "baseline_stddev": 1.0
        }
    }

    result = compare_voice_features_with_baseline(
        current_features=current_features,
        baseline_features=baseline_features
    )

    print("Comparison status:", result["comparison_status"])
    print("RMS Mean Comparison:", result["feature_comparisons"]["rms_mean"])
    print("F0 Mean Comparison:", result["feature_comparisons"]["f0_mean_hz"])
    print("Pause Ratio Comparison:", result["feature_comparisons"]["pause_ratio"])
    print("Event Count Comparison:", result["feature_comparisons"]["estimated_vocal_event_count"])

    assert result["comparison_status"] == "completed"
    assert result["feature_comparisons"]["rms_mean"]["percentage_deviation"] == 75.0
    assert result["feature_comparisons"]["rms_mean"]["deviation_class"] == "marked_deviation"
    print("Voice baseline comparison test passed successfully!")

if __name__ == "__main__":
    test_voice_baseline_service()
