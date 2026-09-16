from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from sklearn.preprocessing import StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.ml.physiological_sequence_extractor import (
    extract_physiological_sequence,
)


INPUT_DIR = PROJECT_ROOT / "datasets" / "raw" / "physiological"
OUTPUT_DIR = PROJECT_ROOT / "datasets" / "processed" / "physiological"

WINDOW_SIZE = 32
STRIDE = 8


def prepare_dataset() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    all_windows = []
    all_labels = []
    feature_names = None

    csv_files = sorted(INPUT_DIR.rglob("*.csv"))
    json_files = sorted(INPUT_DIR.rglob("*.json"))
    files = csv_files + json_files

    if not files:
        raise FileNotFoundError(
            f"No physiological CSV or JSON files found in {INPUT_DIR}"
        )

    print(f"Found {len(files)} physiological data files to process.")

    for index, file_path in enumerate(files, start=1):
        try:
            result = extract_physiological_sequence(
                file_path=file_path,
                window_size=WINDOW_SIZE,
                stride=STRIDE,
            )

            windows = result["windows"]
            labels = result["labels"]

            if len(windows) == 0:
                continue

            if labels is None:
                print(f"Skipping file without labels: {file_path.name}")
                continue

            all_windows.append(windows)
            all_labels.append(labels)

            if feature_names is None:
                feature_names = result["feature_names"]

            print(f"[{index}/{len(files)}] Processed {file_path.name}: {len(windows)} windows")
        except Exception as err:
            print(f"[{index}/{len(files)}] Warning: Failed to process {file_path.name}: {err}")

    if not all_windows:
        raise ValueError("No valid physiological windows were created")

    X = np.concatenate(all_windows, axis=0)
    y = np.concatenate(all_labels, axis=0)

    sample_count, time_steps, feature_count = X.shape

    scaler = StandardScaler()

    flattened = X.reshape(-1, feature_count)
    scaler.fit(flattened)

    X_scaled = scaler.transform(flattened)
    X_scaled = X_scaled.reshape(
        sample_count,
        time_steps,
        feature_count,
    ).astype(np.float32)

    np.savez(
        OUTPUT_DIR / "physiological_sequences.npz",
        X=X_scaled,
        y=y,
    )

    np.savez(
        OUTPUT_DIR / "physiological_scaler.npz",
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
        OUTPUT_DIR / "physiological_metadata.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(metadata, file, indent=2)

    print("Physiological dataset prepared")
    print(f"Samples: {sample_count}")
    print(f"Time steps: {time_steps}")
    print(f"Features: {feature_count}")


if __name__ == "__main__":
    prepare_dataset()
