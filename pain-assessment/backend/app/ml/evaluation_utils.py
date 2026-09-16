from typing import Any

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


def calculate_classification_metrics(
    y_true: list[int] | np.ndarray,
    y_pred: list[int] | np.ndarray,
    y_probability: np.ndarray | None = None,
) -> dict[str, Any]:
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    labels = sorted(np.unique(np.concatenate([y_true, y_pred])).tolist())

    matrix = confusion_matrix(
        y_true,
        y_pred,
        labels=labels,
    )

    metrics: dict[str, Any] = {
        "accuracy": float(
            accuracy_score(y_true, y_pred)
        ),
        "precision_score": float(
            precision_score(
                y_true,
                y_pred,
                average="macro",
                zero_division=0,
            )
        ),
        "recall_score": float(
            recall_score(
                y_true,
                y_pred,
                average="macro",
                zero_division=0,
            )
        ),
        "f1_score": float(
            f1_score(
                y_true,
                y_pred,
                average="macro",
                zero_division=0,
            )
        ),
        "confusion_matrix": matrix.tolist(),
        "class_metrics": classification_report(
            y_true,
            y_pred,
            labels=labels,
            output_dict=True,
            zero_division=0,
        ),
    }

    if y_probability is not None:
        try:
            metrics["roc_auc"] = float(
                roc_auc_score(
                    y_true,
                    y_probability,
                    multi_class="ovr",
                )
            )
        except ValueError:
            metrics["roc_auc"] = None

    return metrics


def calculate_multiclass_sensitivity_specificity(
    y_true: list[int] | np.ndarray,
    y_pred: list[int] | np.ndarray,
) -> dict[str, Any]:
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    labels = sorted(np.unique(np.concatenate([y_true, y_pred])).tolist())
    matrix = confusion_matrix(y_true, y_pred, labels=labels)

    class_results = {}

    for index, label in enumerate(labels):
        true_positive = matrix[index, index]
        false_negative = matrix[index, :].sum() - true_positive
        false_positive = matrix[:, index].sum() - true_positive
        true_negative = matrix.sum() - (
            true_positive
            + false_negative
            + false_positive
        )

        sensitivity_denominator = (
            true_positive + false_negative
        )
        specificity_denominator = (
            true_negative + false_positive
        )

        sensitivity = (
            true_positive / sensitivity_denominator
            if sensitivity_denominator
            else 0.0
        )

        specificity = (
            true_negative / specificity_denominator
            if specificity_denominator
            else 0.0
        )

        class_results[str(label)] = {
            "sensitivity": float(sensitivity),
            "specificity": float(specificity),
            "true_positive": int(true_positive),
            "false_positive": int(false_positive),
            "true_negative": int(true_negative),
            "false_negative": int(false_negative),
        }

    return class_results
