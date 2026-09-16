import uuid
from datetime import datetime, timezone
from typing import Any

from app.db.supabase_client import supabase

# In-memory storage fallback for offline/development execution
_in_memory_evaluations: list[dict[str, Any]] = []


def save_model_evaluation(
    evaluation: dict[str, Any],
    evaluated_by: str | None = None,
) -> dict[str, Any]:
    record_id = str(uuid.uuid4())
    now_iso = datetime.now(timezone.utc).isoformat()

    payload = {
        **evaluation,
        "id": record_id,
        "evaluated_by": evaluated_by,
        "evaluated_at": now_iso,
    }

    try:
        response = (
            supabase
            .table("model_evaluations")
            .insert(payload)
            .execute()
        )
        if response.data:
            return response.data[0]
    except Exception as err:
        # Fallback to local memory log if Supabase table is unavailable
        print(f"[Evaluation Service] Supabase insert note: {err}")

    _in_memory_evaluations.insert(0, payload)
    return payload


def get_model_evaluations(
    model_name: str | None = None,
    modality: str | None = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    try:
        query = (
            supabase
            .table("model_evaluations")
            .select("*")
            .order("evaluated_at", desc=True)
            .limit(limit)
        )

        if model_name:
            query = query.eq("model_name", model_name)

        if modality:
            query = query.eq("modality", modality)

        response = query.execute()

        if response.data:
            return response.data
    except Exception as err:
        print(f"[Evaluation Service] Supabase query note: {err}")

    # Fallback to in-memory store
    results = _in_memory_evaluations
    if model_name:
        results = [e for e in results if e.get("model_name") == model_name]
    if modality:
        results = [e for e in results if e.get("modality") == modality]

    return results[:limit]
