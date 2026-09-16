from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.preprocessing import StandardScaler

from app.ml.dataset_config import (
    FACIAL_PROCESSED_ROOT,
    FACIAL_SPLITS_ROOT,
    create_dataset_directories,
)


FEATURE_NAMES = [
    "eye_openness_mean",
    "eye_openness_stddev",
    "mouth_openness_mean",
    "mouth_openness_stddev",
    "brow_eye_distance_mean",
    "brow_eye_distance_stddev",
    "facial_movement_mean",
    "facial_movement_stddev",
]


def load_split_records(
    split_name: str,
) -> list[dict[str, Any]]:
    split_path = (
        FACIAL_SPLITS_ROOT
        / f"{split_name}.json"
    )

    if not split_path.exists():
        raise FileNotFoundError(
            f"Split file not found: {split_path}"
        )

    with split_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def extract_feature_vector(
    features: dict[str, Any],
) -> list[float]:
    vector = []

    for feature_name in FEATURE_NAMES:
        value = features.get(
            feature_name,
            0.0,
        )

        if not isinstance(value, (int, float)):
            value = 0.0

        vector.append(float(value))

    return vector


def create_sliding_windows(
    feature_vectors: list[list[float]],
    label: int,
    window_size: int = 16,
    stride: int = 8,
) -> tuple[list[list[list[float]]], list[int]]:
    sequences = []
    labels = []

    if len(feature_vectors) < window_size:
        return sequences, labels

    for start in range(
        0,
        len(feature_vectors) - window_size + 1,
        stride,
    ):
        end = start + window_size

        sequence = feature_vectors[start:end]

        sequences.append(sequence)
        labels.append(label)

    return sequences, labels


def build_sequence_dataset(
    records: list[dict[str, Any]],
    window_size: int = 16,
    stride: int = 8,
) -> tuple[np.ndarray, np.ndarray]:
    all_sequences = []
    all_labels = []

    for record in records:
        features = record.get(
            "features",
            {},
        )

        label = int(
            record.get(
                "label",
                0,
            )
        )

        # A record containing one aggregate feature vector
        # is converted into a repeated sequence for prototype use.
        feature_vector = extract_feature_vector(
            features
        )

        feature_vectors = [
            feature_vector
            for _ in range(window_size)
        ]

        sequences, labels = create_sliding_windows(
            feature_vectors=feature_vectors,
            label=label,
            window_size=window_size,
            stride=stride,
        )

        all_sequences.extend(sequences)
        all_labels.extend(labels)

    if not all_sequences:
        return (
            np.empty(
                (0, window_size, len(FEATURE_NAMES)),
                dtype=np.float32,
            ),
            np.empty(
                (0,),
                dtype=np.int64,
            ),
        )

    return (
        np.asarray(
            all_sequences,
            dtype=np.float32,
        ),
        np.asarray(
            all_labels,
            dtype=np.int64,
        ),
    )


def fit_scaler(
    sequences: np.ndarray,
) -> StandardScaler:
    if len(sequences) == 0:
        raise ValueError(
            "Cannot fit scaler on an empty dataset"
        )

    sample_count, window_size, feature_count = (
        sequences.shape
    )

    flattened = sequences.reshape(
        sample_count * window_size,
        feature_count,
    )

    scaler = StandardScaler()
    scaler.fit(flattened)

    return scaler


def apply_scaler(
    sequences: np.ndarray,
    scaler: StandardScaler,
) -> np.ndarray:
    if len(sequences) == 0:
        return sequences

    sample_count, window_size, feature_count = (
        sequences.shape
    )

    flattened = sequences.reshape(
        sample_count * window_size,
        feature_count,
    )

    scaled = scaler.transform(
        flattened
    )

    return scaled.reshape(
        sample_count,
        window_size,
        feature_count,
    ).astype(np.float32)


def save_sequence_dataset(
    split_name: str,
    sequences: np.ndarray,
    labels: np.ndarray,
) -> str:
    create_dataset_directories()

    output_path = (
        FACIAL_PROCESSED_ROOT
        / f"{split_name}_sequences.npz"
    )

    np.savez_compressed(
        output_path,
        X=sequences,
        y=labels,
    )

    return str(output_path)


def prepare_facial_sequences(
    window_size: int = 16,
    stride: int = 8,
) -> dict[str, Any]:
    create_dataset_directories()

    train_records = load_split_records(
        "train"
    )

    validation_records = load_split_records(
        "validation"
    )

    test_records = load_split_records(
        "test"
    )

    train_sequences, train_labels = (
        build_sequence_dataset(
            train_records,
            window_size=window_size,
            stride=stride,
        )
    )

    validation_sequences, validation_labels = (
        build_sequence_dataset(
            validation_records,
            window_size=window_size,
            stride=stride,
        )
    )

    test_sequences, test_labels = (
        build_sequence_dataset(
            test_records,
            window_size=window_size,
            stride=stride,
        )
    )

    if len(train_sequences) == 0:
        raise ValueError(
            "Training dataset is empty"
        )

    scaler = fit_scaler(
        train_sequences
    )

    train_sequences = apply_scaler(
        train_sequences,
        scaler,
    )

    validation_sequences = apply_scaler(
        validation_sequences,
        scaler,
    )

    test_sequences = apply_scaler(
        test_sequences,
        scaler,
    )

    output_paths = {
        "train": save_sequence_dataset(
            "train",
            train_sequences,
            train_labels,
        ),
        "validation": save_sequence_dataset(
            "validation",
            validation_sequences,
            validation_labels,
        ),
        "test": save_sequence_dataset(
            "test",
            test_sequences,
            test_labels,
        ),
    }

    scaler_path = (
        FACIAL_PROCESSED_ROOT
        / "facial_scaler.npz"
    )

    np.savez(
        scaler_path,
        mean=scaler.mean_,
        scale=scaler.scale_,
    )

    return {
        "window_size": window_size,
        "feature_count": len(FEATURE_NAMES),
        "train_samples": len(train_sequences),
        "validation_samples": len(
            validation_sequences
        ),
        "test_samples": len(test_sequences),
        "output_paths": output_paths,
        "scaler_path": str(scaler_path),
    }
