from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.ml.physiological_model import create_physiological_model


DATA_PATH = (
    PROJECT_ROOT
    / "datasets"
    / "processed"
    / "physiological"
    / "physiological_sequences.npz"
)

MODEL_DIR = PROJECT_ROOT / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

BATCH_SIZE = 32
EPOCHS = 25
LEARNING_RATE = 0.001


def load_data() -> tuple[np.ndarray, np.ndarray]:
    data = np.load(DATA_PATH)

    X = data["X"].astype(np.float32)
    y = data["y"].astype(np.int64)

    return X, y


def train() -> None:
    X, y = load_data()

    if len(X) < 4:
        raise ValueError("At least 4 training samples are required")

    # Stratified train / validation split
    X_train, X_validation, y_train, y_validation = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y if len(np.unique(y)) > 1 else None,
    )

    train_dataset = TensorDataset(
        torch.tensor(X_train),
        torch.tensor(y_train),
    )

    validation_dataset = TensorDataset(
        torch.tensor(X_validation),
        torch.tensor(y_validation),
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
    )

    validation_loader = DataLoader(
        validation_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
    )

    feature_count = X.shape[2]

    model = create_physiological_model(
        feature_count=feature_count,
        num_classes=4,
    )

    class_counts = np.bincount(y_train, minlength=4)
    class_weights = len(y_train) / (
        4 * np.maximum(class_counts, 1)
    )

    criterion = nn.CrossEntropyLoss(
        weight=torch.tensor(
            class_weights,
            dtype=torch.float32,
        )
    )

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=LEARNING_RATE,
    )

    best_f1 = -1.0
    history = []

    for epoch in range(EPOCHS):
        model.train()

        train_predictions = []
        train_targets = []
        train_loss_total = 0.0

        for batch_X, batch_y in train_loader:
            optimizer.zero_grad()

            logits = model(batch_X)
            loss = criterion(logits, batch_y)

            loss.backward()
            torch.nn.utils.clip_grad_norm_(
                model.parameters(),
                max_norm=1.0,
            )
            optimizer.step()

            train_loss_total += loss.item()

            predictions = torch.argmax(logits, dim=1)

            train_predictions.extend(
                predictions.detach().cpu().numpy()
            )
            train_targets.extend(
                batch_y.detach().cpu().numpy()
            )

        model.eval()

        validation_predictions = []
        validation_targets = []

        with torch.no_grad():
            for batch_X, batch_y in validation_loader:
                logits = model(batch_X)
                predictions = torch.argmax(logits, dim=1)

                validation_predictions.extend(
                    predictions.cpu().numpy()
                )
                validation_targets.extend(
                    batch_y.cpu().numpy()
                )

        train_accuracy = accuracy_score(
            train_targets,
            train_predictions,
        )

        train_f1 = f1_score(
            train_targets,
            train_predictions,
            average="macro",
            zero_division=0,
        )

        if len(validation_targets) > 0:
            validation_accuracy = accuracy_score(
                validation_targets,
                validation_predictions,
            )

            validation_f1 = f1_score(
                validation_targets,
                validation_predictions,
                average="macro",
                zero_division=0,
            )
        else:
            validation_accuracy = 0.0
            validation_f1 = 0.0

        epoch_result = {
            "epoch": epoch + 1,
            "train_loss": train_loss_total / max(
                len(train_loader),
                1,
            ),
            "train_accuracy": train_accuracy,
            "train_macro_f1": train_f1,
            "validation_accuracy": validation_accuracy,
            "validation_macro_f1": validation_f1,
        }

        history.append(epoch_result)

        print(epoch_result)

        if validation_f1 > best_f1 or epoch == 0:
            best_f1 = max(best_f1, validation_f1)

            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "feature_count": feature_count,
                    "num_classes": 4,
                },
                MODEL_DIR / "physiological_cnn_lstm_best.pt",
            )

    with open(
        MODEL_DIR / "physiological_training_history.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(history, file, indent=2)

    print("Training completed")
    print(f"Best validation macro-F1: {best_f1:.4f}")


if __name__ == "__main__":
    train()
