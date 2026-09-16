import math


def calculate_magnitude(x: float, y: float, z: float) -> float:
    return math.sqrt(x**2 + y**2 + z**2)


def detect_fall(
    acc_x: float,
    acc_y: float,
    acc_z: float,
    gyro_x: float,
    gyro_y: float,
    gyro_z: float,
) -> dict:
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

    # Temporary thresholds for synthetic testing
    high_impact = acceleration_magnitude > 18
    high_rotation = gyroscope_magnitude > 8

    if high_impact and high_rotation:
        fall_probability = 0.95
        detected = True
        reason = "High acceleration impact and sudden rotation detected"

    elif high_impact:
        fall_probability = 0.80
        detected = True
        reason = "High acceleration impact detected"

    elif high_rotation:
        fall_probability = 0.65
        detected = False
        reason = "Sudden rotation detected without strong impact"

    else:
        fall_probability = 0.05
        detected = False
        reason = "Normal movement pattern"

    return {
        "fall_detected": detected,
        "fall_probability": fall_probability,
        "acceleration_magnitude": round(
            acceleration_magnitude,
            3,
        ),
        "gyroscope_magnitude": round(
            gyroscope_magnitude,
            3,
        ),
        "reason": reason,
    }