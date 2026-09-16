from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.ml.fusion_model import create_fusion_model


DATA_PATH = (
    PROJECT_ROOT
    / "datasets"
    / "processed"
    / "fusion"
    / "fusion_dataset.npz"
)

MODEL_DIR = PROJECT_ROOT / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

BATCH_SIZE = 16
EPOCHS = 20
LEARNING_RATE = 0.001


def load_data() -> tuple[np.ndarray, np.ndarray]:
    data = np.load(DATA_PATH)
    X = data["X"].astype(np.float32)
    y = data["y"].astype(np.int64)
    return X, y


def train() -> None:
    X, y = load_data()

    if len(X) < 2:
        raise ValueError("At least two training samples are required")

    split_index = max(1, int(len(X) * 0.8))

    X_train, y_train = X[:split_index], y[:split_index]
    X_val, y_val = X[split_index:], y[split_index:]

    train_loader = DataLoader(
        TensorDataset(torch.tensor(X_train), torch.tensor(y_train)),
        batch_size=BATCH_SIZE,
        shuffle=True,
    )
    val_loader = DataLoader(
        TensorDataset(torch.tensor(X_val), torch.tensor(y_val)),
        batch_size=BATCH_SIZE,
        shuffle=False,
    )

    feature_count = X.shape[1]
    model = create_fusion_model(input_size=feature_count, num_classes=4)

    class_counts = np.bincount(y_train, minlength=4)
    class_weights = len(y_train) / (4 * np.maximum(class_counts, 1))

    criterion = nn.CrossEntropyLoss(
        weight=torch.tensor(class_weights, dtype=torch.float32)
    )
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

    best_f1 = -1.0
    history = []

    for epoch in range(EPOCHS):
        model.train()
        train_preds, train_targets, train_loss_total = [], [], 0.0

        for batch_X, batch_y in train_loader:
            optimizer.zero_grad()
            logits = model(batch_X)
            loss = criterion(logits, batch_y)

            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

            train_loss_total += loss.item()
            preds = torch.argmax(logits, dim=1)
            train_preds.extend(preds.detach().cpu().numpy())
            train_targets.extend(batch_y.detach().cpu().numpy())

        model.eval()
        val_preds, val_targets = [], []
        with torch.no_grad():
            for batch_X, batch_y in val_loader:
                logits = model(batch_X)
                preds = torch.argmax(logits, dim=1)
                val_preds.extend(preds.cpu().numpy())
                val_targets.extend(batch_y.cpu().numpy())

        train_acc = accuracy_score(train_targets, train_preds)
        train_f1 = f1_score(train_targets, train_preds, average="macro", zero_division=0)

        if len(val_targets) > 0:
            val_acc = accuracy_score(val_targets, val_preds)
            val_f1 = f1_score(val_targets, val_preds, average="macro", zero_division=0)
            val_precision = precision_score(val_targets, val_preds, average="macro", zero_division=0)
            val_recall = recall_score(val_targets, val_preds, average="macro", zero_division=0)
        else:
            val_acc, val_f1, val_precision, val_recall = 0.0, 0.0, 0.0, 0.0

        epoch_result = {
            "epoch": epoch + 1,
            "train_loss": float(train_loss_total / max(len(train_loader), 1)),
            "train_accuracy": float(train_acc),
            "train_macro_f1": float(train_f1),
            "validation_accuracy": float(val_acc),
            "validation_macro_f1": float(val_f1),
            "validation_precision": float(val_precision),
            "validation_recall": float(val_recall),
        }
        history.append(epoch_result)

        if val_f1 > best_f1 or epoch == 0:
            best_f1 = max(best_f1, val_f1)
            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "feature_count": feature_count,
                    "num_classes": 4,
                },
                MODEL_DIR / "multimodal_fusion_best.pt",
            )

    with open(MODEL_DIR / "fusion_training_history.json", "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

    print("Multimodal Fusion model training completed")
    print(f"Best validation macro-F1: {best_f1:.4f}")


if __name__ == "__main__":
    train()
