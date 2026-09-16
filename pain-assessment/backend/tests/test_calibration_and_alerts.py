import numpy as np
import pytest
import torch
from fastapi.testclient import TestClient

from app.main import app
from app.ml.calibration_utils import (
    calculate_binary_calibration_metrics,
    calculate_multiclass_calibration_metrics,
)
from app.ml.temperature_scaling import TemperatureScaler, fit_temperature
from app.services.alert_state_service import (
    AlertState,
    ScoreSmoother,
    get_safe_alert_message,
    update_alert_state,
)

client = TestClient(app)


def test_binary_calibration_metrics():
    y_true = [1, 1, 0, 0, 1, 0, 1, 0, 1, 0]
    probs = [0.9, 0.8, 0.2, 0.1, 0.85, 0.3, 0.75, 0.15, 0.95, 0.05]

    res = calculate_binary_calibration_metrics(y_true, probs, number_of_bins=5)
    assert "brier_score" in res
    assert "calibration_error" in res
    assert "expected_calibration_error" in res
    assert res["brier_score"] >= 0.0
    assert res["expected_calibration_error"] >= 0.0
    assert res["sample_count"] == 10


def test_multiclass_calibration_metrics():
    y_true = [0, 1, 2, 3, 1, 2]
    probs = np.array([
        [0.7, 0.1, 0.1, 0.1],
        [0.1, 0.7, 0.1, 0.1],
        [0.1, 0.1, 0.7, 0.1],
        [0.1, 0.1, 0.1, 0.7],
        [0.2, 0.6, 0.1, 0.1],
        [0.1, 0.2, 0.6, 0.1],
    ])

    res = calculate_multiclass_calibration_metrics(y_true, probs, number_of_bins=3)
    assert "macro_ece" in res
    assert "macro_brier" in res
    assert "per_class" in res
    assert len(res["per_class"]) == 4


def test_temperature_scaling_module():
    scaler = TemperatureScaler()
    logits = torch.tensor([[2.0, 1.0, 0.1, -1.0]])

    calibrated_logits = scaler(logits)
    probs = scaler.probabilities(logits)

    assert calibrated_logits.shape == logits.shape
    assert probs.shape == logits.shape
    assert torch.isclose(probs.sum(), torch.tensor(1.0), atol=1e-4)

    # Test fitting temperature
    val_logits = torch.randn(20, 4)
    val_labels = torch.randint(0, 4, (20,))
    fitted_scaler = fit_temperature(val_logits, val_labels, max_iter=10)
    assert fitted_scaler.temperature.item() > 0.0


def test_score_smoother():
    smoother = ScoreSmoother(window_size=3)
    assert smoother.update(0.6) == 0.6
    assert smoother.update(0.8) == 0.7
    assert smoother.update(1.0) == pytest.approx(0.8)
    assert smoother.update(0.6) == pytest.approx(0.8)  # window is [0.8, 1.0, 0.6]


def test_alert_hysteresis_state_transitions():
    state = AlertState()

    # Single high window (0.70 >= 0.65) -> consecutive high = 1 -> no alert yet
    state, event = update_alert_state(state, 0.70)
    assert event == "no_alert"
    assert not state.active

    # Second high window -> consecutive high = 2 -> alert started
    state, event = update_alert_state(state, 0.72)
    assert event == "alert_started"
    assert state.active

    # Drop to 0.50 (between 0.45 and 0.65) -> stays active
    state, event = update_alert_state(state, 0.50)
    assert event == "alert_continues"
    assert state.active

    # Drop below 0.45 for 1st window -> stays active
    state, event = update_alert_state(state, 0.35)
    assert event == "alert_continues"

    # 2nd low window -> stays active
    state, event = update_alert_state(state, 0.30)
    assert event == "alert_continues"

    # 3rd low window -> alert ended
    state, event = update_alert_state(state, 0.25)
    assert event == "alert_ended"
    assert not state.active


def test_safe_alert_message_mapping():
    sev, msg = get_safe_alert_message(0.85, 0.90, active_modalities_count=2)
    assert sev == "urgent_review"
    assert "High pain-related activity detected" in msg

    sev_low, msg_low = get_safe_alert_message(0.30, 0.85, active_modalities_count=2)
    assert sev_low == "informational"
    assert "Low pain-related activity" in msg_low

    sev_insuff, msg_insuff = get_safe_alert_message(0.85, 0.30, active_modalities_count=2)
    assert sev_insuff == "informational"
    assert "data is insufficient" in msg_insuff


AUTH_HEADERS = {"Authorization": "Bearer mock-admin-token"}


def test_alerts_rest_api_endpoints():
    # Test active alerts endpoint
    res = client.get("/alerts/active", headers=AUTH_HEADERS)
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) > 0

    alert_id = data[0]["id"]

    # Test patient alerts endpoint
    patient_id = data[0]["patient_id"]
    res_pat = client.get(f"/alerts/patient/{patient_id}", headers=AUTH_HEADERS)
    assert res_pat.status_code == 200
    assert len(res_pat.json()) > 0

    # Test acknowledge endpoint
    res_ack = client.post(f"/alerts/{alert_id}/acknowledge", headers=AUTH_HEADERS)
    assert res_ack.status_code == 200
    assert res_ack.json()["status"] == "acknowledged"

    # Test clinician feedback endpoint
    feedback_payload = {
        "clinician_label": "true_positive",
        "clinician_feedback": "Validated pain activity during exam.",
    }
    res_fb = client.post(f"/alerts/{alert_id}/feedback", json=feedback_payload, headers=AUTH_HEADERS)
    assert res_fb.status_code == 200
    assert res_fb.json()["clinician_label"] == "true_positive"

    # Test resolve endpoint
    res_res = client.post(f"/alerts/{alert_id}/resolve", headers=AUTH_HEADERS)
    assert res_res.status_code == 200
    assert res_res.json()["status"] == "resolved"

    # Test performance metrics endpoint
    res_met = client.get("/alerts/metrics/performance", headers=AUTH_HEADERS)
    assert res_met.status_code == 200
    met_data = res_met.json()
    assert "false_alarm_rate" in met_data
    assert "missed_episode_rate" in met_data
    assert "positive_predictive_value" in met_data
    assert "expected_calibration_error" in met_data

    # Test calibrations endpoint
    res_cal = client.get("/alerts/calibrations", headers=AUTH_HEADERS)
    assert res_cal.status_code == 200
    assert len(res_cal.json()) > 0
