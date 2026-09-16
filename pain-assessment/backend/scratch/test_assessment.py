from app.services.assessment_service import (
    calculate_facial_score,
    calculate_physiological_score,
    calculate_behavioral_score,
    calculate_voice_score,
    get_nested_value,
    get_numeric_feature,
    build_data_availability,
    build_clinical_message,
)

def test_assessment_helpers():
    # Test nested dot notation lookup
    nested_data = {
        "vocal_events": {
            "estimated_vocal_event_count": 8
        }
    }
    val = get_numeric_feature(nested_data, ["vocal_events.estimated_vocal_event_count"])
    assert val == 8.0, f"Expected 8.0, got {val}"

    # Test individual modality score calculators
    facial_feat = {"facial_movement_mean": 0.10, "mouth_openness_mean": 0.25, "brow_eye_distance_mean": 0.10}
    f_score = calculate_facial_score(facial_feat)
    print("Facial score:", f_score)
    assert 0.0 <= f_score <= 1.0

    phys_feat = {"heart_rate_change": 15.0, "respiration_rate_change": 5.0, "eda_peak_rate": 5.0}
    p_score = calculate_physiological_score(phys_feat)
    print("Physiological score:", p_score)
    assert 0.0 <= p_score <= 1.0

    beh_feat = {"movement_intensity_mean": 0.12, "sudden_movement_count": 5, "stillness_ratio": 0.3}
    b_score = calculate_behavioral_score(beh_feat)
    print("Behavioral score:", b_score)
    assert 0.0 <= b_score <= 1.0

    v_feat = {"f0_stddev_hz": 50.0, "pause_ratio": 0.4, "vocal_events": {"estimated_vocal_event_count": 5}}
    v_score = calculate_voice_score(v_feat)
    print("Voice score:", v_score)
    assert 0.0 <= v_score <= 1.0

    # Test data availability builder
    latest_feats = {
        "facial": {"id": "f1", "features": facial_feat},
        "physiological": {"id": "p1", "features": phys_feat}
    }
    avail = build_data_availability(latest_feats)
    print("Data availability:", avail)
    assert avail["available_modality_count"] == 2
    assert "behavioral" in avail["missing_modalities"]

    print("Assessment service tests passed successfully!")

if __name__ == "__main__":
    test_assessment_helpers()
