import uuid
from datetime import datetime, timezone
from typing import Any

from app.core.monitoring_config import (
    EPISODE_END_THRESHOLD,
    EPISODE_START_THRESHOLD,
    MIN_CONFIDENCE_FOR_EPISODE,
    MIN_DATA_QUALITY_FOR_EPISODE,
)
from app.db.supabase_client import supabase

# In-memory storage fallbacks for offline execution & testing
_in_memory_episodes: list[dict[str, Any]] = []
_in_memory_observations: list[dict[str, Any]] = []


def calculate_trend(
    previous_score: float | None,
    current_score: float | None,
) -> str:
    if previous_score is None or current_score is None:
        return "unknown"

    difference = current_score - previous_score

    if difference >= 0.05:
        return "increasing"

    if difference <= -0.05:
        return "decreasing"

    return "stable"


def get_open_episode(patient_id: str) -> dict[str, Any] | None:
    try:
        response = (
            supabase
            .table("pain_episodes")
            .select("*")
            .eq("patient_id", patient_id)
            .eq("status", "ongoing")
            .order("started_at", desc=True)
            .limit(1)
            .execute()
        )
        if response.data:
            return response.data[0]
    except Exception as err:
        print(f"[Episode Service] DB query note: {err}")

    # Fallback to in-memory list
    for ep in _in_memory_episodes:
        if ep.get("patient_id") == patient_id and ep.get("status") == "ongoing":
            return ep
    return None


def create_episode(
    patient_id: str,
    observation: dict[str, Any],
) -> dict[str, Any]:
    now = observation.get("observed_at") or datetime.now(timezone.utc)
    if isinstance(now, str):
        now_dt = datetime.fromisoformat(now.replace("Z", "+00:00"))
    else:
        now_dt = now

    score = observation["pain_related_activity_score"]

    if score >= 0.75:
        level = "high"
    elif score >= 0.50:
        level = "moderate"
    else:
        level = "low"

    record_id = str(uuid.uuid4())
    payload = {
        "id": record_id,
        "patient_id": patient_id,
        "started_at": now_dt.isoformat(),
        "peak_score": score,
        "average_score": score,
        "episode_level": level,
        "active_modalities": observation.get("active_modalities", []),
        "modality_contributions": observation.get("modality_contributions", {}),
        "confidence": observation.get("confidence"),
        "status": "ongoing",
        "clinician_reviewed": False,
        "created_at": now_dt.isoformat(),
        "updated_at": now_dt.isoformat(),
    }

    try:
        response = (
            supabase
            .table("pain_episodes")
            .insert(payload)
            .execute()
        )
        if response.data:
            return response.data[0]
    except Exception as err:
        print(f"[Episode Service] DB insert note: {err}")

    _in_memory_episodes.insert(0, payload)
    return payload


def save_episode_observation(
    episode_id: str,
    observation: dict[str, Any],
) -> dict[str, Any]:
    obs_id = str(uuid.uuid4())
    now = observation.get("observed_at") or datetime.now(timezone.utc)
    observed_iso = now.isoformat() if hasattr(now, "isoformat") else str(now)

    payload = {
        "id": obs_id,
        "episode_id": episode_id,
        "patient_id": observation["patient_id"],
        "pain_related_activity_score": observation["pain_related_activity_score"],
        "confidence": observation.get("confidence"),
        "active_modalities": observation.get("active_modalities", []),
        "missing_modalities": observation.get("missing_modalities", []),
        "modality_contributions": observation.get("modality_contributions", {}),
        "data_quality": observation.get("data_quality"),
        "observed_at": observed_iso,
    }

    try:
        response = (
            supabase
            .table("pain_episode_observations")
            .insert(payload)
            .execute()
        )
        if response.data:
            return response.data[0]
    except Exception as err:
        print(f"[Episode Service] DB obs insert note: {err}")

    _in_memory_observations.insert(0, payload)
    return payload


def update_episode(
    episode: dict[str, Any],
    observation: dict[str, Any],
) -> dict[str, Any]:
    score = observation["pain_related_activity_score"]
    ep_id = episode["id"]

    previous_peak = float(episode.get("peak_score") or 0)

    # Fetch existing scores for episode
    scores = [score]
    try:
        observation_response = (
            supabase
            .table("pain_episode_observations")
            .select("pain_related_activity_score")
            .eq("episode_id", ep_id)
            .execute()
        )
        db_scores = [
            float(row["pain_related_activity_score"])
            for row in (observation_response.data or [])
            if row.get("pain_related_activity_score") is not None
        ]
        if db_scores:
            scores = db_scores + [score]
    except Exception:
        mem_scores = [
            float(o["pain_related_activity_score"])
            for o in _in_memory_observations
            if o.get("episode_id") == ep_id
        ]
        scores = mem_scores + [score]

    new_peak = max(previous_peak, score)
    new_avg = sum(scores) / len(scores)

    if new_peak >= 0.75:
        level = "high"
    elif new_peak >= 0.50:
        level = "moderate"
    else:
        level = "low"

    updated_payload = {
        "peak_score": round(new_peak, 4),
        "average_score": round(new_avg, 4),
        "episode_level": level,
        "confidence": observation.get("confidence"),
        "active_modalities": observation.get("active_modalities", []),
        "modality_contributions": observation.get("modality_contributions", {}),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    try:
        response = (
            supabase
            .table("pain_episodes")
            .update(updated_payload)
            .eq("id", ep_id)
            .execute()
        )
        if response.data:
            return response.data[0]
    except Exception as err:
        print(f"[Episode Service] DB update note: {err}")

    # Fallback in-memory update
    for ep in _in_memory_episodes:
        if ep["id"] == ep_id:
            ep.update(updated_payload)
            return ep

    return {**episode, **updated_payload}


def complete_episode(
    episode_id: str,
    ended_at: datetime | str,
) -> dict[str, Any]:
    ended_iso = ended_at.isoformat() if hasattr(ended_at, "isoformat") else str(ended_at)
    now_iso = datetime.now(timezone.utc).isoformat()

    # Calculate duration if started_at is present
    duration_seconds = None
    ep_to_update = None
    for ep in _in_memory_episodes:
        if ep["id"] == episode_id:
            ep_to_update = ep
            break

    if ep_to_update and ep_to_update.get("started_at"):
        try:
            s_dt = datetime.fromisoformat(str(ep_to_update["started_at"]).replace("Z", "+00:00"))
            e_dt = datetime.fromisoformat(ended_iso.replace("Z", "+00:00"))
            duration_seconds = round(max(0.0, (e_dt - s_dt).total_seconds()), 2)
        except Exception:
            pass

    update_fields = {
        "ended_at": ended_iso,
        "duration_seconds": duration_seconds,
        "status": "completed",
        "updated_at": now_iso,
    }

    try:
        response = (
            supabase
            .table("pain_episodes")
            .update(update_fields)
            .eq("id", episode_id)
            .execute()
        )
        if response.data:
            return response.data[0]
    except Exception as err:
        print(f"[Episode Service] DB complete note: {err}")

    if ep_to_update:
        ep_to_update.update(update_fields)
        return ep_to_update

    return {"id": episode_id, **update_fields}


def process_observation(
    observation: dict[str, Any],
) -> dict[str, Any]:
    patient_id = observation["patient_id"]
    score = float(observation["pain_related_activity_score"])
    confidence = float(observation.get("confidence") or 0.0)
    data_quality = observation.get("data_quality")

    reliable = confidence >= MIN_CONFIDENCE_FOR_EPISODE

    if data_quality is not None:
        reliable = reliable and (float(data_quality) >= MIN_DATA_QUALITY_FOR_EPISODE)

    episode = get_open_episode(patient_id)

    if not reliable:
        return {
            "status": "insufficient_data",
            "message": "Insufficient reliable data because signal confidence or data quality is below threshold.",
            "episode": episode,
        }

    if episode is None:
        if score >= EPISODE_START_THRESHOLD:
            new_episode = create_episode(
                patient_id,
                observation,
            )

            save_episode_observation(
                new_episode["id"],
                observation,
            )

            return {
                "status": "episode_started",
                "message": "Pain-related activity episode started.",
                "episode": new_episode,
            }

        return {
            "status": "no_active_episode",
            "message": "No active episode; score below start threshold.",
            "episode": None,
        }

    save_episode_observation(
        episode["id"],
        observation,
    )

    if score <= EPISODE_END_THRESHOLD:
        ended_at = observation.get("observed_at") or datetime.now(timezone.utc)

        completed = complete_episode(
            episode["id"],
            ended_at,
        )

        return {
            "status": "episode_completed",
            "message": "Pain-related activity episode completed as score returned below threshold.",
            "episode": completed,
        }

    updated = update_episode(
        episode,
        observation,
    )

    return {
        "status": "episode_updated",
        "message": "Pain-related activity episode updated.",
        "episode": updated,
    }


def review_episode(
    episode_id: str,
    clinician_comment: str,
) -> dict[str, Any]:
    update_data = {
        "clinician_reviewed": True,
        "clinician_comment": clinician_comment,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        res = supabase.table("pain_episodes").update(update_data).eq("id", episode_id).execute()
        if res.data:
            return res.data[0]
    except Exception:
        pass

    for ep in _in_memory_episodes:
        if ep["id"] == episode_id:
            ep.update(update_data)
            return ep

    return {"id": episode_id, **update_data}


def get_patient_episodes(
    patient_id: str,
    limit: int = 50,
) -> list[dict[str, Any]]:
    try:
        response = (
            supabase
            .table("pain_episodes")
            .select("*")
            .eq("patient_id", patient_id)
            .order("started_at", desc=True)
            .limit(limit)
            .execute()
        )
        if response.data:
            return response.data
    except Exception:
        pass

    filtered = [ep for ep in _in_memory_episodes if ep.get("patient_id") == patient_id]
    return filtered[:limit]


def get_episode_by_id(episode_id: str) -> dict[str, Any] | None:
    try:
        response = (
            supabase
            .table("pain_episodes")
            .select("*")
            .eq("id", episode_id)
            .single()
            .execute()
        )
        if response and getattr(response, "data", None):
            return response.data
    except Exception:
        pass

    for ep in _in_memory_episodes:
        if ep["id"] == episode_id:
            return ep
    return None
