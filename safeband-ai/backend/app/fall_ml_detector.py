from pathlib import Path

import joblib
import pandas as pd


MODEL_PATH = Path("models/fall_detection_model.joblib")
ENCODER_PATH = Path("models/fall_label_encoder.joblib")

FALL_CONFIDENCE_THRESHOLD = 0.75

FEATURE_COLUMNS = [
    "ADXL345_Acc_X",
    "ADXL345_Acc_Y",
    "ADXL345_Acc_Z",
    "ITG3200_Gyro_X",
    "ITG3200_Gyro_Y",
    "ITG3200_Gyro_Z",
    "MMA8451Q_Acc_X",
    "MMA8451Q_Acc_Y",
    "MMA8451Q_Acc_Z",
]

model = joblib.load(MODEL_PATH)
label_encoder = joblib.load(ENCODER_PATH)


def is_fall_label(label: str) -> bool:
    normalized_label = str(label).strip().lower()

    return normalized_label in {
        "1",
        "fall",
        "fallen",
        "true",
        "yes",
    }


def predict_fall(
    adxl_acc_x: float,
    adxl_acc_y: float,
    adxl_acc_z: float,
    gyro_x: float,
    gyro_y: float,
    gyro_z: float,
    mma_acc_x: float,
    mma_acc_y: float,
    mma_acc_z: float,
) -> dict:
    input_data = pd.DataFrame(
        [
            {
                "ADXL345_Acc_X": adxl_acc_x,
                "ADXL345_Acc_Y": adxl_acc_y,
                "ADXL345_Acc_Z": adxl_acc_z,
                "ITG3200_Gyro_X": gyro_x,
                "ITG3200_Gyro_Y": gyro_y,
                "ITG3200_Gyro_Z": gyro_z,
                "MMA8451Q_Acc_X": mma_acc_x,
                "MMA8451Q_Acc_Y": mma_acc_y,
                "MMA8451Q_Acc_Z": mma_acc_z,
            }
        ],
        columns=FEATURE_COLUMNS,
    )

    prediction_id = model.predict(input_data)[0]
    predicted_label = label_encoder.inverse_transform(
        [prediction_id]
    )[0]

    probabilities = model.predict_proba(input_data)[0]
    confidence = float(max(probabilities))

    model_detected_fall = is_fall_label(predicted_label)

    fall_detected = (
        model_detected_fall
        and confidence >= FALL_CONFIDENCE_THRESHOLD
    )

    return {
        "prediction": str(predicted_label),
        "confidence": round(confidence, 4),
        "fall_detected": fall_detected,
        "model_detected_fall": model_detected_fall,
        "confidence_threshold": FALL_CONFIDENCE_THRESHOLD,
        "status": (
            "fall_detected"
            if fall_detected
            else "possible_fall_or_normal_activity"
        ),
    }