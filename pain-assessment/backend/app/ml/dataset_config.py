from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASETS_ROOT = PROJECT_ROOT / "datasets"

RAW_DATA_ROOT = DATASETS_ROOT / "raw"
PROCESSED_DATA_ROOT = DATASETS_ROOT / "processed"
ANNOTATIONS_ROOT = DATASETS_ROOT / "annotations"
SPLITS_ROOT = DATASETS_ROOT / "splits"


FACIAL_RAW_ROOT = RAW_DATA_ROOT / "facial"
FACIAL_PROCESSED_ROOT = PROCESSED_DATA_ROOT / "facial"
FACIAL_ANNOTATIONS_ROOT = ANNOTATIONS_ROOT / "facial"
FACIAL_SPLITS_ROOT = SPLITS_ROOT / "facial"


def create_dataset_directories() -> None:
    directories = [
        FACIAL_RAW_ROOT,
        FACIAL_PROCESSED_ROOT,
        FACIAL_ANNOTATIONS_ROOT,
        FACIAL_SPLITS_ROOT,
    ]

    for directory in directories:
        directory.mkdir(
            parents=True,
            exist_ok=True,
        )
