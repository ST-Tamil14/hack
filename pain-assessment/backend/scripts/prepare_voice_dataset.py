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

from app.ml.voice_sequence_extractor import VOICE_FEATURE_NAMES, extract_voice_sequence


INPUT_DIR = PROJECT_ROOT / "datasets" / "raw" / "voice"
OUTPUT_DIR = PROJECT_ROOT / "datasets" / "processed" / "voice"

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

    for start in range(0, len(sequence) - window_size + 1, stride):
        end = start + window_size
        windows.append(sequence[start:end])
        labels.append(label)

    return windows, labels


def prepare_dataset() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    all_windows = []
    all_labels = []
    feature_names = VOICE_FEATURE_NAMES

    # Check for synthetic 500-sample CSV
    csv_candidates = [
        INPUT_DIR / "synthetic_voice_audio_pain_dataset_500.csv",
        PROJECT_ROOT / "datasets" / "raw" / "synthetic_voice_audio_pain_dataset_500.csv",
    ]

    csv_path = next((p for p in csv_candidates if p.exists()), None)

    if csv_path:
        print(f"Loading voice dataset from CSV: {csv_path}")
        df = pd.read_csv(csv_path)

        col_map = {
            "RMS_energy": "rms",
            "zero_crossing_rate": "zcr",
            "spectral_centroid_hz": "spectral_centroid",
            "spectral_bandwidth_hz": "spectral_bandwidth",
            "pitch_hz": "f0",
            "MFCC1": "mfcc_1",
            "MFCC2": "mfcc_2",
            "MFCC3": "mfcc_3",
            "MFCC4": "mfcc_4",
            "MFCC5": "mfcc_5",
            "MFCC6": "mfcc_6",
            "MFCC7": "mfcc_7",
            "MFCC8": "mfcc_8",
            "MFCC9": "mfcc_9",
            "MFCC10": "mfcc_10",
        }

        # Select available voice columns
        csv_features = [
            "RMS_energy", "zero_crossing_rate", "spectral_centroid_hz", "spectral_bandwidth_hz",
            "pitch_hz", "MFCC1", "MFCC2", "MFCC3", "MFCC4", "MFCC5",
            "MFCC6", "MFCC7", "MFCC8", "MFCC9", "MFCC10", "pitch_hz"
        ]
        valid_cols = [c for c in csv_features if c in df.columns]

        if len(valid_cols) >= 15:
            values = df[valid_cols].to_numpy(dtype=np.float32)
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

            feature_names = [col_map.get(c, c) for c in valid_cols]

    if not all_windows:
        annotation_path = (
            PROJECT_ROOT
            / "datasets"
            / "annotations"
            / "voice"
            / "sample_voice_annotations.csv"
        )

        if annotation_path.exists():
            annotations = pd.read_csv(annotation_path)

            for _, row in annotations.iterrows():
                file_name = str(row["file_path"])
                audio_path = INPUT_DIR / file_name
                label = int(row["label"])

                if not audio_path.exists():
                    continue

                result = extract_voice_sequence(audio_path)
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
        raise ValueError("No voice sequences were created")

    X = np.asarray(all_windows, dtype=np.float32)
    y = np.asarray(all_labels, dtype=np.int64)

    sample_count, time_steps, feature_count = X.shape

    scaler = StandardScaler()
    flattened = X.reshape(-1, feature_count)
    scaler.fit(flattened)

    normalized = scaler.transform(flattened).reshape(
        sample_count, time_steps, feature_count
    ).astype(np.float32)

    np.savez(
        OUTPUT_DIR / "voice_sequences.npz",
        X=normalized,
        y=y,
    )

    np.savez(
        OUTPUT_DIR / "voice_scaler.npz",
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

    with open(OUTPUT_DIR / "voice_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print("Voice dataset prepared successfully")
    print(f"Samples: {sample_count}")
    print(f"Features: {feature_count}")
    print(f"Window size: {time_steps}")


if __name__ == "__main__":
    prepare_dataset()
