from __future__ import annotations

import csv
import json
import random
from pathlib import Path
from typing import Any

from app.ml.dataset_config import (
    FACIAL_ANNOTATIONS_ROOT,
    FACIAL_SPLITS_ROOT,
    create_dataset_directories,
)


def read_annotation_file(
    annotation_path: Path,
) -> list[dict[str, Any]]:
    if not annotation_path.exists():
        raise FileNotFoundError(
            f"Annotation file not found: {annotation_path}"
        )

    if annotation_path.suffix.lower() == ".json":
        with annotation_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            return data.get("records", [])

        raise ValueError(
            "Unsupported JSON annotation format"
        )

    if annotation_path.suffix.lower() == ".csv":
        with annotation_path.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as file:
            return list(csv.DictReader(file))

    raise ValueError(
        "Only CSV and JSON annotation files are supported"
    )


def normalize_label(
    label: Any,
) -> int:
    if isinstance(label, bool):
        return int(label)

    if isinstance(label, (int, float)):
        return int(label)

    normalized = str(label).strip().lower()

    label_mapping = {
        "no pain": 0,
        "no_pain": 0,
        "none": 0,
        "low": 1,
        "mild": 1,
        "moderate": 2,
        "high": 3,
        "severe": 3,
    }

    if normalized in label_mapping:
        return label_mapping[normalized]

    try:
        numeric_label = float(normalized)
        return int(numeric_label)

    except ValueError as exc:
        raise ValueError(
            f"Unsupported pain label: {label}"
        ) from exc


def normalize_records(
    records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    normalized_records = []

    for index, record in enumerate(records):
        sample_id = str(
            record.get(
                "sample_id",
                record.get(
                    "id",
                    f"sample_{index:06d}",
                ),
            )
        )

        patient_id = str(
            record.get(
                "patient_id",
                record.get(
                    "subject_id",
                    record.get(
                        "subject",
                        "unknown_patient",
                    ),
                ),
            )
        )

        file_path = str(
            record.get(
                "file_path",
                record.get(
                    "video_path",
                    record.get(
                        "path",
                        "",
                    ),
                ),
            )
        )

        raw_label = record.get(
            "label",
            record.get(
                "pain_label",
                record.get(
                    "pain_score",
                    0,
                ),
            ),
        )

        normalized_records.append(
            {
                "sample_id": sample_id,
                "patient_id": patient_id,
                "file_path": file_path,
                "label": normalize_label(
                    raw_label
                ),
                "metadata": record,
            }
        )

    return normalized_records


def split_by_patient(
    records: list[dict[str, Any]],
    train_ratio: float = 0.70,
    validation_ratio: float = 0.15,
    test_ratio: float = 0.15,
    seed: int = 42,
) -> dict[str, list[dict[str, Any]]]:
    total_ratio = (
        train_ratio
        + validation_ratio
        + test_ratio
    )

    if abs(total_ratio - 1.0) > 0.001:
        raise ValueError(
            "Split ratios must add up to 1.0"
        )

    patient_ids = sorted(
        {
            record["patient_id"]
            for record in records
        }
    )

    random_generator = random.Random(seed)
    random_generator.shuffle(patient_ids)

    total_patients = len(patient_ids)

    train_end = int(
        total_patients * train_ratio
    )

    validation_end = train_end + int(
        total_patients * validation_ratio
    )

    train_patients = set(
        patient_ids[:train_end]
    )

    validation_patients = set(
        patient_ids[
            train_end:validation_end
        ]
    )

    test_patients = set(
        patient_ids[validation_end:]
    )

    split_records = {
        "train": [],
        "validation": [],
        "test": [],
    }

    for record in records:
        patient_id = record["patient_id"]

        if patient_id in train_patients:
            split_records["train"].append(record)

        elif patient_id in validation_patients:
            split_records["validation"].append(record)

        elif patient_id in test_patients:
            split_records["test"].append(record)

    return split_records


def save_split_records(
    split_records: dict[str, list[dict[str, Any]]],
) -> dict[str, str]:
    create_dataset_directories()

    output_paths = {}

    for split_name, records in split_records.items():
        output_path = (
            FACIAL_SPLITS_ROOT
            / f"{split_name}.json"
        )

        with output_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                records,
                file,
                indent=2,
            )

        output_paths[split_name] = str(
            output_path
        )

    return output_paths


def prepare_facial_dataset(
    annotation_filename: str,
) -> dict[str, Any]:
    create_dataset_directories()

    annotation_path = (
        FACIAL_ANNOTATIONS_ROOT
        / annotation_filename
    )

    raw_records = read_annotation_file(
        annotation_path
    )

    normalized_records = normalize_records(
        raw_records
    )

    split_records = split_by_patient(
        normalized_records
    )

    output_paths = save_split_records(
        split_records
    )

    return {
        "total_records": len(
            normalized_records
        ),
        "total_patients": len(
            {
                record["patient_id"]
                for record in normalized_records
            }
        ),
        "split_counts": {
            split_name: len(records)
            for split_name, records in split_records.items()
        },
        "output_paths": output_paths,
    }
