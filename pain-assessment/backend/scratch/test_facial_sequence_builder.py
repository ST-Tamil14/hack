import os
import numpy as np
from app.services.dataset_service import prepare_facial_dataset
from app.ml.facial_sequence_builder import prepare_facial_sequences

def test_sequence_builder():
    # 1. Prepare facial dataset splits from sample_annotations.csv
    dataset_info = prepare_facial_dataset("sample_annotations.csv")
    print("Dataset prepared:", dataset_info)

    # 2. Build facial sequence dataset and fitted scalers
    sequence_info = prepare_facial_sequences(window_size=16, stride=8)
    print("Sequences prepared:", sequence_info)

    assert sequence_info["window_size"] == 16
    assert sequence_info["feature_count"] == 8
    assert os.path.exists(sequence_info["output_paths"]["train"])
    assert os.path.exists(sequence_info["scaler_path"])

    # Load generated npz to verify shapes
    train_npz = np.load(sequence_info["output_paths"]["train"])
    X_train = train_npz["X"]
    y_train = train_npz["y"]
    print("X_train shape:", X_train.shape)
    print("y_train shape:", y_train.shape)

    assert len(X_train.shape) == 3
    assert X_train.shape[1] == 16
    assert X_train.shape[2] == 8
    print("Facial sequence builder test passed successfully!")

if __name__ == "__main__":
    test_sequence_builder()
