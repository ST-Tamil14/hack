from pathlib import Path
import random

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.preprocessing import LabelEncoder


BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "models" / "fall_detection_model.joblib"
LABEL_ENCODER_PATH = BASE_DIR / "models" / "fall_label_encoder.joblib"

model = joblib.load(MODEL_PATH)
label_encoder = joblib.load(LABEL_ENCODER_PATH)

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

REQUIRED_COLUMNS = FEATURE_COLUMNS + [
    TARGET_COLUMN
]

RANDOM_SEED = 42
TRAIN_RATIO = 0.80


def load_one_csv(file_path: Path) -> pd.DataFrame:
    print(f"Reading: {file_path.name}")

    df = pd.read_csv(file_path)

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        print(
            f"Skipped {file_path.name}. "
            f"Missing columns: {missing_columns}"
        )
        return pd.DataFrame()

    df = df[REQUIRED_COLUMNS].copy()

    for column in FEATURE_COLUMNS:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    df = df.dropna(
        subset=REQUIRED_COLUMNS
    )

    if df.empty:
        print(
            f"Skipped {file_path.name}: "
            "no valid rows."
        )
        return pd.DataFrame()

    print(f"Valid rows: {len(df)}")

    return df


def load_files(file_paths):
    datasets = []

    for file_path in file_paths:
        df = load_one_csv(file_path)

        if not df.empty:
            datasets.append(df)

    if not datasets:
        raise ValueError(
            "No compatible CSV files were found."
        )

    return pd.concat(
        datasets,
        ignore_index=True,
    )


def main():
    csv_files = sorted(
        BASE_DIR.glob("*.csv")
    )

    if not csv_files:
        raise FileNotFoundError(
            "No CSV files found in the datasets folder."
        )

    print(f"Total CSV files found: {len(csv_files)}")

    random.seed(RANDOM_SEED)
    random.shuffle(csv_files)

    train_file_count = int(
        len(csv_files) * TRAIN_RATIO
    )

    if train_file_count <= 0:
        raise ValueError(
            "Not enough files for training."
        )

    if train_file_count >= len(csv_files):
        train_file_count = len(csv_files) - 1

    train_files = csv_files[
        :train_file_count
    ]

    test_files = csv_files[
        train_file_count:
    ]

    print("\nTraining files:")
    print(len(train_files))

    print("\nTesting files:")
    print(len(test_files))

    print("\nLoading training data...")
    train_df = load_files(train_files)

    print("\nLoading testing data...")
    test_df = load_files(test_files)

    print("\nTraining rows:", len(train_df))
    print("Testing rows:", len(test_df))

    print("\nTraining label distribution:")
    print(
        train_df[TARGET_COLUMN].value_counts()
    )

    print("\nTesting label distribution:")
    print(
        test_df[TARGET_COLUMN].value_counts()
    )

    X_train = train_df[FEATURE_COLUMNS]
    y_train = train_df[TARGET_COLUMN].astype(str)

    X_test = test_df[FEATURE_COLUMNS]
    y_test = test_df[TARGET_COLUMN].astype(str)

    label_encoder = LabelEncoder()

    y_train_encoded = label_encoder.fit_transform(
        y_train
    )

    try:
        y_test_encoded = label_encoder.transform(
            y_test
        )
    except ValueError as error:
        raise ValueError(
            "The testing dataset contains a label "
            "that does not exist in the training dataset."
        ) from error

    print("\nDetected classes:")
    print(label_encoder.classes_)

    model = RandomForestClassifier(
        n_estimators=500,
        random_state=42,
        class_weight={0: 1, 1: 3},
        n_jobs=-1,
    )

    print("\nTraining Random Forest model...")

    model.fit(
        X_train,
        y_train_encoded,
    )

    predictions = model.predict(X_test)

    print("\nAccuracy:")
    print(
        round(
            accuracy_score(
                y_test_encoded,
                predictions,
            ),
            4,
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

    joblib.dump(
        model,
        MODEL_PATH,
    )

    joblib.dump(
        label_encoder,
        LABEL_ENCODER_PATH,
    )

    print("\nModel saved successfully.")
    print(f"Model path: {MODEL_PATH}")
    print(f"Encoder path: {LABEL_ENCODER_PATH}")


if __name__ == "__main__":
    main()