from app.services.fusion_result_service import generate_clinical_message

def test_clinical_message():
    high_result = {
        "pain_related_activity_level": "high",
        "confidence": 0.85,
        "missing_modalities": []
    }
    msg_high = generate_clinical_message(high_result)
    print("High level clinical message:", msg_high)
    assert "increased pain-related activity" in msg_high

    low_conf_result = {
        "pain_related_activity_level": "moderate",
        "confidence": 0.50,
        "missing_modalities": ["voice"]
    }
    msg_low_conf = generate_clinical_message(low_conf_result)
    print("Low confidence clinical message:", msg_low_conf)
    assert "Confidence is limited" in msg_low_conf
    assert "Missing modalities: voice." in msg_low_conf

    insufficient_result = {
        "pain_related_activity_level": "insufficient_data",
        "confidence": 0.0,
        "missing_modalities": ["facial", "voice", "behavioral", "physiological"]
    }
    msg_insufficient = generate_clinical_message(insufficient_result)
    print("Insufficient data message:", msg_insufficient)
    assert "Insufficient reliable data" in msg_insufficient

    print("Clinical message tests passed successfully!")

if __name__ == "__main__":
    test_clinical_message()
