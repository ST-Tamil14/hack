from pathlib import Path

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.preprocessing import LabelEncoder


DATASET_FOLDER = Path("datasets")

TRAIN_FILES = [
    "fall_dataset_1.csv",
    "fall_dataset_2.csv",
    "fall_dataset_3.csv",
]

TEST_FILE = "fall_dataset_4.csv"

MODEL_PATH = Path(
    "models/fall_detection_model.joblib"
)

ENCODER_PATH = Path(
    "models/fall_label_encoder.joblib"
)

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

TARGET_COLUMN = "FallCheck"


def load_one_file(file_name):
    file_path = DATASET_FOLDER / file_name

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    df = pd.read_csv(file_path)

    required_columns = FEATURE_COLUMNS + [
        TARGET_COLUMN
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"{file_name} is missing: "
            f"{missing_columns}"
        )

    df = df[required_columns].copy()

    for column in FEATURE_COLUMNS:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    return df.dropna(
        subset=required_columns
    )


def main():
    train_data = pd.concat(
        [
            load_one_file(file_name)
            for file_name in TRAIN_FILES
        ],
        ignore_index=True,
    )

    test_data = load_one_file(TEST_FILE)

    X_train = train_data[FEATURE_COLUMNS]
    y_train = train_data[TARGET_COLUMN].astype(str)

    X_test = test_data[FEATURE_COLUMNS]
    y_test = test_data[TARGET_COLUMN].astype(str)

    label_encoder = LabelEncoder()

    y_train_encoded = label_encoder.fit_transform(
        y_train
    )

    y_test_encoded = label_encoder.transform(
        y_test
    )

    model = RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1,
    )

    model.fit(
        X_train,
        y_train_encoded,
    )

    predictions = model.predict(X_test)

    print("Training rows:", len(train_data))
    print("Testing rows:", len(test_data))

    print("\nAccuracy:")
    print(
        accuracy_score(
            y_test_encoded,
            predictions,
        )
    )

    print("\nClassification report:")
    print(
        classification_report(
            y_test_encoded,
            predictions,
            target_names=label_encoder.classes_,
            zero_division=0,
        )
    )

    print("\nConfusion matrix:")
    print(
        confusion_matrix(
            y_test_encoded,
            predictions,
        )
    )

    MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(model, MODEL_PATH)
    joblib.dump(
        label_encoder,
        ENCODER_PATH,
    )

    print("\nModel saved successfully.")


if __name__ == "__main__":
    main()