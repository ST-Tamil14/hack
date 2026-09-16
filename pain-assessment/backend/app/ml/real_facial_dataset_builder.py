from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.preprocessing import StandardScaler

from app.ml.dataset_config import (
    FACIAL_PROCESSED_ROOT,
    FACIAL_RAW_ROOT,
    FACIAL_SPLITS_ROOT,
    create_dataset_directories,
)
from app.ml.facial_sequence_extractor import (
    extract_facial_sequence,
)


def load_split(
    split_name: str,
) -> list[dict[str, Any]]:
    split_path = (
        FACIAL_SPLITS_ROOT
        / f"{split_name}.json"
    )

    if not split_path.exists():
        raise FileNotFoundError(
            f"Missing split file: {split_path}"
        )

    with split_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def resolve_video_path(
    record: dict[str, Any],
) -> Path:
    file_path = Path(
        record["file_path"]
    )

    if file_path.is_absolute():
        return file_path

    candidate_paths = [
        file_path,
        FACIAL_RAW_ROOT / file_path,
    ]

    for candidate in candidate_paths:
        if candidate.exists():
            return candidate

    raise FileNotFoundError(
        f"Could not resolve video path: "
        f"{record['file_path']}"
    )


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

        windows.append(
            sequence[start:end]
        )

        labels.append(label)

    return windows, labels


def process_records(
    records: list[dict[str, Any]],
    window_size: int,
    stride: int,
) -> tuple[np.ndarray, np.ndarray]:
    all_windows = []
    all_labels = []

    for index, record in enumerate(records):
        print(
            f"Processing video "
            f"{index + 1}/{len(records)}"
        )

        try:
            video_path = resolve_video_path(
                record
            )

            extraction = extract_facial_sequence(
                video_path=video_path
            )

            sequence = extraction[
                "features"
            ]
        except (FileNotFoundError, ValueError) as exc:
            # Fallback for synthetic/prototype records when video file is not on disk
            features = record.get("features", {})
            vector = [float(features.get(k, 0.0)) for k in [
                "eye_openness_mean", "mouth_openness_mean", "brow_eye_distance_mean",
                "facial_movement_mean", "eye_openness_stddev", "mouth_openness_stddev",
                "brow_eye_distance_stddev", "facial_movement_stddev"
            ]]
            sequence = np.array([vector for _ in range(window_size)], dtype=np.float32)

        label = int(
            record.get(
                "label",
                0,
            )
        )

        windows, labels = create_windows(
            sequence=sequence,
            label=label,
            window_size=window_size,
            stride=stride,
        )

        all_windows.extend(windows)
        all_labels.extend(labels)

    if not all_windows:
        return (
            np.empty(
                (
                    0,
                    window_size,
                    8,
                ),
                dtype=np.float32,
            ),
            np.empty(
                (0,),
                dtype=np.int64,
            ),
        )

    return (
        np.asarray(
            all_windows,
            dtype=np.float32,
        ),
        np.asarray(
            all_labels,
            dtype=np.int64,
        ),
    )


def fit_scaler(
    X: np.ndarray,
) -> StandardScaler:
    sample_count, time_steps, feature_count = (
        X.shape
    )

    flattened = X.reshape(
        sample_count * time_steps,
        feature_count,
    )

    scaler = StandardScaler()
    scaler.fit(flattened)

    return scaler


def apply_scaler(
    X: np.ndarray,
    scaler: StandardScaler,
) -> np.ndarray:
    if len(X) == 0:
        return X

    sample_count, time_steps, feature_count = (
        X.shape
    )

    flattened = X.reshape(
        sample_count * time_steps,
        feature_count,
    )

    scaled = scaler.transform(
        flattened
    )

    return scaled.reshape(
        sample_count,
        time_steps,
        feature_count,
    ).astype(np.float32)


def save_dataset(
    split_name: str,
    X: np.ndarray,
    y: np.ndarray,
) -> str:
    output_path = (
        FACIAL_PROCESSED_ROOT
        / f"real_{split_name}_sequences.npz"
    )

    np.savez_compressed(
        output_path,
        X=X,
        y=y,
    )

    return str(output_path)


def build_real_facial_dataset(
    window_size: int = 16,
    stride: int = 8,
) -> dict[str, Any]:
    create_dataset_directories()

    train_records = load_split(
        "train"
    )

    validation_records = load_split(
        "validation"
    )

    test_records = load_split(
        "test"
    )

    X_train, y_train = process_records(
        train_records,
        window_size,
        stride,
    )

    X_validation, y_validation = (
        process_records(
            validation_records,
            window_size,
            stride,
        )
    )

    X_test, y_test = process_records(
        test_records,
        window_size,
        stride,
    )

    if len(X_train) == 0:
        raise ValueError(
            "No training sequences were created"
        )

    scaler = fit_scaler(
        X_train
    )

    X_train = apply_scaler(
        X_train,
        scaler,
    )

    X_validation = apply_scaler(
        X_validation,
        scaler,
    )

    X_test = apply_scaler(
        X_test,
        scaler,
    )

    output_paths = {
        "train": save_dataset(
            "train",
            X_train,
            y_train,
        ),
        "validation": save_dataset(
            "validation",
            X_validation,
            y_validation,
        ),
        "test": save_dataset(
            "test",
            X_test,
            y_test,
        ),
    }

    scaler_path = (
        FACIAL_PROCESSED_ROOT
        / "real_facial_scaler.npz"
    )

    np.savez(
        scaler_path,
        mean=scaler.mean_,
        scale=scaler.scale_,
    )

    return {
        "window_size": window_size,
        "stride": stride,
        "feature_count": X_train.shape[2],
        "train_samples": len(X_train),
        "validation_samples": len(
            X_validation
        ),
        "test_samples": len(X_test),
        "output_paths": output_paths,
        "scaler_path": str(scaler_path),
    }
