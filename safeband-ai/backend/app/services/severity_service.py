def calculate_severity(
    fall_probability: float,
    acceleration_magnitude: float,
    inactivity_seconds: float,
    heart_rate: float | None = None,
    spo2: float | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
) -> dict:
    risk_score = 0
    reasons = []

    # Fall probability
    if fall_probability >= 0.90:
        risk_score += 35
        reasons.append("Very high fall probability")
    elif fall_probability >= 0.80:
        risk_score += 25
        reasons.append("High fall probability")
    elif fall_probability >= 0.60:
        risk_score += 15
        reasons.append("Moderate fall probability")

    # Impact strength
    if acceleration_magnitude >= 25:
        risk_score += 30
        reasons.append("Very strong impact detected")
    elif acceleration_magnitude >= 18:
        risk_score += 20
        reasons.append("Strong impact detected")
    elif acceleration_magnitude >= 12:
        risk_score += 10
        reasons.append("Moderate impact detected")

    # Inactivity
    if inactivity_seconds >= 30:
        risk_score += 20
        reasons.append("Extended inactivity after possible fall")
    elif inactivity_seconds >= 10:
        risk_score += 10
        reasons.append("Post-fall inactivity detected")

    # Health context
    if heart_rate is not None:
        if heart_rate >= 140 or heart_rate <= 45:
            risk_score += 10
            reasons.append("Abnormal heart-rate reading")

    if spo2 is not None and spo2 < 92:
        risk_score += 10
        reasons.append("Low SpO2 reading")

    # Location context
    location_available = (
        latitude is not None and longitude is not None
    )

    if location_available:
        reasons.append("Location available for emergency response")
    else:
        reasons.append("Location unavailable")

    risk_score = min(risk_score, 100)

    if risk_score >= 70:
        severity = "high"
    elif risk_score >= 40:
        severity = "medium"
    else:
        severity = "low"

    return {
        "severity": severity,
        "risk_score": risk_score,
        "location_available": location_available,
        "reasons": reasons,
        "warning": (
            "Prototype risk estimate; not a clinical injury diagnosis"
        ),
    }