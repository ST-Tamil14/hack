import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.ml.real_facial_dataset_builder import (
    build_real_facial_dataset,
)


if __name__ == "__main__":
    result = build_real_facial_dataset(
        window_size=16,
        stride=8,
    )

    print("\nDataset preparation completed.")
    print(result)
