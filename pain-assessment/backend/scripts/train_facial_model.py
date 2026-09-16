from __future__ import annotations

import json
import random
import sys
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
)
from torch import nn
from torch.utils.data import (
    DataLoader,
    TensorDataset,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.ml.facial_model import (
    create_facial_model,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

PROCESSED_ROOT = (
    PROJECT_ROOT
    / "datasets"
    / "processed"
    / "facial"
)

MODEL_ROOT = (
    PROJECT_ROOT
    / "models"
)

MODEL_ROOT.mkdir(
    parents=True,
    exist_ok=True,
)

RANDOM_SEED = 42
BATCH_SIZE = 16
EPOCHS = 20
LEARNING_RATE = 0.001

DEVICE = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)


def set_seed(seed: int = RANDOM_SEED):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def load_dataset(
    split_name: str,
) -> tuple[np.ndarray, np.ndarray]:
    dataset_path = (
        PROCESSED_ROOT
        / f"real_{split_name}_sequences.npz"
    )

    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {dataset_path}"
        )

    data = np.load(
        dataset_path
    )

    X = data["X"].astype(
        np.float32
    )

    y = data["y"].astype(
        np.int64
    )

    return X, y


def create_dataloader(
    X: np.ndarray,
    y: np.ndarray,
    shuffle: bool,
) -> DataLoader:
    dataset = TensorDataset(
        torch.tensor(X),
        torch.tensor(y),
    )

    return DataLoader(
        dataset,
        batch_size=BATCH_SIZE,
        shuffle=shuffle,
    )


def calculate_class_weights(
    labels: np.ndarray,
    num_classes: int,
) -> torch.Tensor:
    class_counts = np.bincount(
        labels,
        minlength=num_classes,
    )

    total_samples = len(labels)

    weights = []

    for count in class_counts:
        if count == 0:
            weights.append(0.0)
        else:
            weight = (
                total_samples
                / (
                    num_classes
                    * count
                )
            )
            weights.append(weight)

    return torch.tensor(
        weights,
        dtype=torch.float32,
    )


def train_one_epoch(
    model: nn.Module,
    loader: DataLoader,
    loss_function: nn.Module,
    optimizer: torch.optim.Optimizer,
) -> tuple[float, float]:
    model.train()

    total_loss = 0.0
    all_predictions = []
    all_labels = []

    for X_batch, y_batch in loader:
        X_batch = X_batch.to(DEVICE)
        y_batch = y_batch.to(DEVICE)

        optimizer.zero_grad()

        logits = model(X_batch)

        loss = loss_function(
            logits,
            y_batch,
        )

        loss.backward()

        torch.nn.utils.clip_grad_norm_(
            model.parameters(),
            max_norm=1.0,
        )

        optimizer.step()

        total_loss += (
            loss.item()
            * X_batch.size(0)
        )

        predictions = torch.argmax(
            logits,
            dim=1,
        )

        all_predictions.extend(
            predictions.detach()
            .cpu()
            .numpy()
            .tolist()
        )

        all_labels.extend(
            y_batch.detach()
            .cpu()
            .numpy()
            .tolist()
        )

    average_loss = (
        total_loss
        / len(loader.dataset)
    )

    accuracy = accuracy_score(
        all_labels,
        all_predictions,
    )

    return average_loss, accuracy


def evaluate(
    model: nn.Module,
    loader: DataLoader,
    loss_function: nn.Module,
) -> tuple[float, float, float, list[int], list[int]]:
    model.eval()

    total_loss = 0.0
    all_predictions = []
    all_labels = []

    with torch.no_grad():
        for X_batch, y_batch in loader:
            X_batch = X_batch.to(DEVICE)
            y_batch = y_batch.to(DEVICE)

            logits = model(X_batch)

            loss = loss_function(
                logits,
                y_batch,
            )

            total_loss += (
                loss.item()
                * X_batch.size(0)
            )

            predictions = torch.argmax(
                logits,
                dim=1,
            )

            all_predictions.extend(
                predictions.cpu()
                .numpy()
                .tolist()
            )

            all_labels.extend(
                y_batch.cpu()
                .numpy()
                .tolist()
            )

    average_loss = (
        total_loss
        / len(loader.dataset)
    )

    accuracy = accuracy_score(
        all_labels,
        all_predictions,
    )

    macro_f1 = f1_score(
        all_labels,
        all_predictions,
        average="macro",
        zero_division=0,
    )

    return (
        average_loss,
        accuracy,
        macro_f1,
        all_labels,
        all_predictions,
    )


def main():
    set_seed()

    print(f"Using device: {DEVICE}")

    X_train, y_train = load_dataset(
        "train"
    )

    X_validation, y_validation = (
        load_dataset("validation")
    )

    X_test, y_test = load_dataset(
        "test"
    )

    if len(X_train) == 0:
        raise ValueError(
            "Training dataset is empty"
        )

    if len(X_validation) == 0:
        print(
            "Warning: validation dataset is empty"
        )

    if len(X_test) == 0:
        print(
            "Warning: test dataset is empty"
        )

    feature_count = X_train.shape[2]
    num_classes = 4

    train_loader = create_dataloader(
        X_train,
        y_train,
        shuffle=True,
    )

    validation_loader = create_dataloader(
        X_validation,
        y_validation,
        shuffle=False,
    )

    test_loader = create_dataloader(
        X_test,
        y_test,
        shuffle=False,
    )

    model = create_facial_model(
        feature_count=feature_count,
        num_classes=num_classes,
    ).to(DEVICE)

    class_weights = calculate_class_weights(
        y_train,
        num_classes=num_classes,
    ).to(DEVICE)

    loss_function = nn.CrossEntropyLoss(
        weight=class_weights,
    )

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=LEARNING_RATE,
    )

    best_validation_f1 = -1.0
    best_model_path = (
        MODEL_ROOT
        / "facial_cnn_lstm_best.pt"
    )

    training_history = []

    for epoch in range(1, EPOCHS + 1):
        train_loss, train_accuracy = (
            train_one_epoch(
                model=model,
                loader=train_loader,
                loss_function=loss_function,
                optimizer=optimizer,
            )
        )

        if len(X_validation) > 0:
            (
                validation_loss,
                validation_accuracy,
                validation_f1,
                _,
                _,
            ) = evaluate(
                model=model,
                loader=validation_loader,
                loss_function=loss_function,
            )
        else:
            validation_loss = 0.0
            validation_accuracy = 0.0
            validation_f1 = 0.0

        history_item = {
            "epoch": epoch,
            "train_loss": train_loss,
            "train_accuracy": train_accuracy,
            "validation_loss": validation_loss,
            "validation_accuracy": validation_accuracy,
            "validation_macro_f1": validation_f1,
        }

        training_history.append(
            history_item
        )

        print(
            f"Epoch {epoch:02d}/{EPOCHS} | "
            f"Train Loss: {train_loss:.4f} | "
            f"Train Acc: {train_accuracy:.4f} | "
            f"Val Loss: {validation_loss:.4f} | "
            f"Val Acc: {validation_accuracy:.4f} | "
            f"Val F1: {validation_f1:.4f}"
        )

        if validation_f1 > best_validation_f1:
            best_validation_f1 = validation_f1

            torch.save(
                {
                    "model_state_dict": (
                        model.state_dict()
                    ),
                    "feature_count": feature_count,
                    "num_classes": num_classes,
                    "best_validation_f1": (
                        best_validation_f1
                    ),
                },
                best_model_path,
            )

    if best_model_path.exists():
        checkpoint = torch.load(
            best_model_path,
            map_location=DEVICE,
        )

        model.load_state_dict(
            checkpoint["model_state_dict"]
        )

    if len(X_test) > 0:
        (
            test_loss,
            test_accuracy,
            test_f1,
            test_labels,
            test_predictions,
        ) = evaluate(
            model=model,
            loader=test_loader,
            loss_function=loss_function,
        )

        print("\nTest Results")
        print(
            f"Test Loss: {test_loss:.4f}"
        )
        print(
            f"Test Accuracy: {test_accuracy:.4f}"
        )
        print(
            f"Test Macro F1: {test_f1:.4f}"
        )

        print(
            classification_report(
                test_labels,
                test_predictions,
                labels=[0, 1, 2, 3],
                target_names=[
                    "No pain-related activity",
                    "Low",
                    "Moderate",
                    "High",
                ],
                zero_division=0,
            )
        )

    history_path = (
        MODEL_ROOT
        / "facial_training_history.json"
    )

    with history_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            training_history,
            file,
            indent=2,
        )

    print(
        f"Best model saved to: {best_model_path}"
    )

    print(
        f"Training history saved to: {history_path}"
    )


if __name__ == "__main__":
    main()
