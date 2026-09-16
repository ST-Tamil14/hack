def confirm_fall(
    fall_probability: float,
    inactivity_seconds: float,
    user_response: str | None = None,
) -> dict:
    """
    Temporary rule-based fall confirmation.

    This is a prototype logic and is not a clinical diagnosis.
    """

    if user_response == "cancelled":
        return {
            "confirmed": False,
            "status": "cancelled_by_user",
            "reason": "User cancelled the possible fall alert",
        }

    if user_response == "confirmed":
        return {
            "confirmed": True,
            "status": "confirmed_by_user",
            "reason": "User confirmed the fall",
        }

    if (
        fall_probability >= 0.80
        and inactivity_seconds >= 10
    ):
        return {
            "confirmed": True,
            "status": "confirmed_by_inactivity",
            "reason": "High fall probability followed by inactivity",
        }

    if (
        fall_probability >= 0.90
        and inactivity_seconds >= 5
    ):
        return {
            "confirmed": True,
            "status": "confirmed_by_high_probability",
            "reason": "Very high fall probability and post-fall inactivity",
        }

    return {
        "confirmed": False,
        "status": "waiting_for_confirmation",
        "reason": "More evidence or user response is required",
    }