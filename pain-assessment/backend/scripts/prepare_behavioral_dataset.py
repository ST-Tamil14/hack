from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.ml.behavioral_sequence_extractor import (
    POSE_FEATURE_NAMES,
    extract_behavioral_sequence,
)


INPUT_DIR = PROJECT_ROOT / "datasets" / "raw" / "behavioral"
OUTPUT_DIR = PROJECT_ROOT / "datasets" / "processed" / "behavioral"

WINDOW_SIZE = 32
STRIDE = 8

PAIN_CLASS_MAPPING = {
    "No Pain": 0,
    "no pain": 0,
    "Low": 1,
    "low": 1,
    "Moderate": 2,
    "moderate": 2,
    "High": 3,
    "high": 3,
}


def create_windows(
    sequence: np.ndarray,
    label: int,
    window_size: int,
    stride: int,
) -> tuple[list[np.ndarray], list[int]]:
    windows = []
    labels = []

    if len(sequence) < window_size:
        return windows, labels

    for start in range(
        0,
        len(sequence) - window_size + 1,
        stride,
    ):
        end = start + window_size

        windows.append(sequence[start:end])
        labels.append(label)

    return windows, labels


def prepare_dataset() -> None:
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    all_windows = []
    all_labels = []
    feature_names = POSE_FEATURE_NAMES

    # Check for synthetic 500-sample CSV first
    csv_candidates = [
        INPUT_DIR / "synthetic_behavioral_body_movement_dataset_500.csv",
        PROJECT_ROOT / "datasets" / "raw" / "synthetic_behavioral_body_movement_dataset_500.csv",
    ]

    csv_path = next((p for p in csv_candidates if p.exists()), None)

    if csv_path:
        print(f"Loading behavioral dataset from CSV: {csv_path}")
        df = pd.read_csv(csv_path)

        feature_cols = [
            "body_posture_score", "movement_speed_mps", "range_of_motion_deg",
            "movement_smoothness", "protective_movement", "guarding",
            "restlessness", "gait_asymmetry", "transfer_difficulty",
            "activity_interruption", "movement_acceleration",
        ]
        available_cols = [c for c in feature_cols if c in df.columns]

        if len(available_cols) == 11:
            values = df[available_cols].to_numpy(dtype=np.float32)
            if "pain_class" in df.columns:
                labels = df["pain_class"].map(PAIN_CLASS_MAPPING).fillna(0).to_numpy(dtype=np.int64)
            elif "label" in df.columns:
                labels = df["label"].astype(int).to_numpy(dtype=np.int64)
            else:
                labels = np.zeros(len(values), dtype=np.int64)

            for start in range(0, len(values) - WINDOW_SIZE + 1, STRIDE):
                end = start + WINDOW_SIZE
                window = values[start:end]
                window_label = int(np.bincount(labels[start:end], minlength=4).argmax())
                all_windows.append(window)
                all_labels.append(window_label)

            feature_names = available_cols

    if not all_windows:
        # Fallback to video annotations if available
        annotation_path = (
            PROJECT_ROOT
            / "datasets"
            / "annotations"
            / "behavioral"
            / "sample_annotations.csv"
        )

        if annotation_path.exists():
            annotations = pd.read_csv(annotation_path)

            for _, row in annotations.iterrows():
                video_path = INPUT_DIR / str(row["file_path"])
                label = int(row["label"])

                if not video_path.exists():
                    continue

                result = extract_behavioral_sequence(
                    video_path=video_path,
                )

                sequence = result["features"]

                windows, labels = create_windows(
                    sequence=sequence,
                    label=label,
                    window_size=WINDOW_SIZE,
                    stride=STRIDE,
                )

                all_windows.extend(windows)
                all_labels.extend(labels)

    if not all_windows:
        raise ValueError("No behavioral sequences were created")

    X = np.asarray(all_windows, dtype=np.float32)
    y = np.asarray(all_labels, dtype=np.int64)

    sample_count, time_steps, feature_count = X.shape

    scaler = StandardScaler()
    flattened = X.reshape(-1, feature_count)
    scaler.fit(flattened)

    normalized = scaler.transform(flattened).reshape(
        sample_count,
        time_steps,
        feature_count,
    ).astype(np.float32)

    np.savez(
        OUTPUT_DIR / "behavioral_sequences.npz",
        X=normalized,
        y=y,
    )

    np.savez(
        OUTPUT_DIR / "behavioral_scaler.npz",
        mean=scaler.mean_,
        scale=scaler.scale_,
    )

    metadata = {
        "feature_names": feature_names,
        "feature_count": feature_count,
        "window_size": time_steps,
        "sample_count": sample_count,
        "class_count": 4,
    }

    with open(
        OUTPUT_DIR / "behavioral_metadata.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(metadata, file, indent=2)

    print("Behavioral dataset prepared")
    print(f"Samples: {sample_count}")
    print(f"Features: {feature_count}")
    print(f"Window size: {time_steps}")


if __name__ == "__main__":
    prepare_dataset()
