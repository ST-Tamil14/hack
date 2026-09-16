from typing import Any

from app.db.supabase_client import supabase


def create_audit_log(
    user_id: str | None,
    action: str,
    resource_type: str | None = None,
    resource_id: str | None = None,
    patient_id: str | None = None,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "user_id": user_id,
        "action": action,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "patient_id": patient_id,
        "details": details or {},
    }

    try:
        response = (
            supabase
            .table("audit_logs")
            .insert(payload)
            .execute()
        )

        return response.data[0] if response.data else {}
    except Exception:
        return {
            "id": "mock-audit-id",
            **payload,
        }
