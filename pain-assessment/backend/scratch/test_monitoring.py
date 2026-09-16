from app.services.monitoring_service import (
    calculate_data_availability,
    generate_monitoring_message
)
from fastapi.testclient import TestClient
from app.main import app

def test_monitoring_service():
    # Test data availability calculation
    recent_jobs = [{"id": "job-1", "modality": "facial"}]
    fusion_res = {
        "active_modalities": ["facial", "physiological"],
        "missing_modalities": ["voice", "behavioral"],
        "pain_related_activity_level": "moderate",
        "confidence": 0.75
    }

    avail = calculate_data_availability(fusion_res, recent_jobs)
    print("Data availability:", avail)
    assert avail["status"] == "partial_data"

    msg = generate_monitoring_message(fusion_res)
    print("Monitoring message:", msg)
    assert "Moderate pain-related activity was observed" in msg

    no_fusion_msg = generate_monitoring_message(None)
    assert "No multimodal assessment is available" in no_fusion_msg

    print("Monitoring service tests passed successfully!")

if __name__ == "__main__":
    test_monitoring_service()
