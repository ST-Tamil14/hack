import math
from typing import Dict


def calculate_magnitude(x: float, y: float, z: float) -> float:
    return math.sqrt(
        (x * x) +
        (y * y) +
        (z * z)
    )


def classify_activity(
    acc_x: float,
    acc_y: float,
    acc_z: float,
    gyro_x: float,
    gyro_y: float,
    gyro_z: float,
) -> Dict:

    acceleration_magnitude = calculate_magnitude(
        acc_x,
        acc_y,
        acc_z,
    )

    gyroscope_magnitude = calculate_magnitude(
        gyro_x,
        gyro_y,
        gyro_z,
    )

    # Prototype thresholds.
    # These values should be calibrated using your dataset.
    if acceleration_magnitude > 25:
        activity = "possible_fall"
        confidence = 0.90

    elif acceleration_magnitude < 2:
        activity = "lying_or_stationary"
        confidence = 0.75

    elif gyroscope_magnitude > 8:
        activity = "high_motion"
        confidence = 0.80

    else:
        activity = "normal_activity"
        confidence = 0.70

    return {
        "activity": activity,
        "confidence": round(confidence, 3),
        "acceleration_magnitude": round(
            acceleration_magnitude,
            3,
        ),
        "gyroscope_magnitude": round(
            gyroscope_magnitude,
            3,
        ),
    }