import pytest
from datetime import datetime, timezone

from app.schemas.episode import EpisodeObservationCreate
from app.services.episode_service import (
    calculate_trend,
    get_patient_episodes,
    process_observation,
    review_episode,
)


def test_episode_observation_schema():
    obs = EpisodeObservationCreate(
        patient_id="PAT-TEST-001",
        pain_related_activity_score=0.72,
        confidence=0.85,
        active_modalities=["facial", "physiological"],
        data_quality=0.90,
    )
    assert obs.patient_id == "PAT-TEST-001"
    assert obs.pain_related_activity_score == 0.72


def test_calculate_trend():
    assert calculate_trend(0.40, 0.65) == "increasing"
    assert calculate_trend(0.70, 0.40) == "decreasing"
    assert calculate_trend(0.50, 0.52) == "stable"
    assert calculate_trend(None, 0.50) == "unknown"


def test_episode_lifecycle_start_update_complete():
    patient_id = "PAT-EPISODE-TEST"

    # Step 1: Low confidence observation should be rejected
    low_conf_obs = {
        "patient_id": patient_id,
        "pain_related_activity_score": 0.80,
        "confidence": 0.30,  # below 0.50 threshold
    }
    res1 = process_observation(low_conf_obs)
    assert res1["status"] == "insufficient_data"

    # Step 2: Score >= 0.55 triggers episode start
    start_obs = {
        "patient_id": patient_id,
        "pain_related_activity_score": 0.65,
        "confidence": 0.85,
        "data_quality": 0.90,
        "observed_at": datetime(2026, 9, 9, 10, 0, 0, tzinfo=timezone.utc),
    }
    res2 = process_observation(start_obs)
    assert res2["status"] == "episode_started"
    ep_id = res2["episode"]["id"]
    assert res2["episode"]["peak_score"] == 0.65

    # Step 3: High score updates episode peak & average
    peak_obs = {
        "patient_id": patient_id,
        "pain_related_activity_score": 0.85,
        "confidence": 0.88,
        "data_quality": 0.92,
        "observed_at": datetime(2026, 9, 9, 10, 0, 10, tzinfo=timezone.utc),
    }
    res3 = process_observation(peak_obs)
    assert res3["status"] == "episode_updated"
    assert res3["episode"]["peak_score"] == 0.85
    assert res3["episode"]["episode_level"] == "high"

    # Step 4: Score <= 0.40 completes the episode
    end_obs = {
        "patient_id": patient_id,
        "pain_related_activity_score": 0.35,
        "confidence": 0.85,
        "data_quality": 0.90,
        "observed_at": datetime(2026, 9, 9, 10, 0, 30, tzinfo=timezone.utc),
    }
    res4 = process_observation(end_obs)
    assert res4["status"] == "episode_completed"
    assert res4["episode"]["status"] == "completed"

    # Step 5: Review episode
    reviewed = review_episode(ep_id, "Patient administered analgesia, episode resolved.")
    assert reviewed["clinician_reviewed"] is True
    assert "analgesia" in reviewed["clinician_comment"]
