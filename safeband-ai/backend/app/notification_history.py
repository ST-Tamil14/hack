from datetime import datetime, timezone

from app.database import supabase


def get_user_notifications(user_id: str):
    response = (
        supabase
        .table("notifications")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )

    return response.data or []


def get_emergency_notifications(user_id: str):
    response = (
        supabase
        .table("notifications")
        .select("*")
        .eq("user_id", user_id)
        .eq("notification_type", "emergency_alert")
        .order("created_at", desc=True)
        .execute()
    )

    return response.data or []


def acknowledge_notification(notification_id: int):
    current_time = datetime.now(timezone.utc).isoformat()

    response = (
        supabase
        .table("notifications")
        .update({
            "status": "acknowledged",
            "acknowledged_at": current_time,
        })
        .eq("id", notification_id)
        .execute()
    )

    return response.data or []


def resolve_notification(notification_id: int):
    current_time = datetime.now(timezone.utc).isoformat()

    response = (
        supabase
        .table("notifications")
        .update({
            "status": "resolved",
            "resolved_at": current_time,
        })
        .eq("id", notification_id)
        .execute()
    )

    return response.data or []