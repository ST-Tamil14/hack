from typing import Any, Dict, List, Optional, Union

import numpy as np
from sklearn.calibration import calibration_curve
from sklearn.metrics import brier_score_loss


def calculate_binary_calibration_metrics(
    y_true: Union[List[int], np.ndarray],
    probabilities: Union[List[float], np.ndarray],
    number_of_bins: int = 10,
) -> Dict[str, Any]:
    """Calculates binary calibration metrics including Brier score, calibration error (mean absolute error),

    Expected Calibration Error (ECE), and binned calibration curve values.
    """
    y_true = np.asarray(y_true, dtype=int)
    probabilities = np.asarray(probabilities, dtype=float)

    if len(y_true) == 0:
        return {
            "brier_score": 0.0,
            "calibration_error": 0.0,
            "expected_calibration_error": 0.0,
            "fraction_positive": [],
            "mean_predicted_value": [],
            "sample_count": 0,
        }

    brier_score = float(brier_score_loss(y_true, probabilities))

    fraction_positive, mean_predicted_value = calibration_curve(
        y_true,
        probabilities,
        n_bins=number_of_bins,
        strategy="uniform",
    )

    calibration_error = float(
        np.mean(np.abs(fraction_positive - mean_predicted_value))
    )

    # Compute Expected Calibration Error (ECE) with bin sample weighting
    bin_edges = np.linspace(0, 1, number_of_bins + 1)
    bin_assignments = np.digitize(probabilities, bin_edges) - 1
    bin_assignments = np.clip(bin_assignments, 0, number_of_bins - 1)

    ece = 0.0
    total_samples = len(y_true)
    for b in range(number_of_bins):
        mask = bin_assignments == b
        bin_size = np.sum(mask)
        if bin_size > 0:
            bin_acc = np.mean(y_true[mask])
            bin_conf = np.mean(probabilities[mask])
            ece += (bin_size / total_samples) * np.abs(bin_acc - bin_conf)

    return {
        "brier_score": brier_score,
        "calibration_error": calibration_error,
        "expected_calibration_error": float(ece),
        "fraction_positive": fraction_positive.tolist(),
        "mean_predicted_value": mean_predicted_value.tolist(),
        "sample_count": int(total_samples),
    }


def calculate_multiclass_calibration_metrics(
    y_true: Union[List[int], np.ndarray],
    probabilities_matrix: Union[List[List[float]], np.ndarray],
    class_names: Optional[List[str]] = None,
    number_of_bins: int = 10,
) -> Dict[str, Any]:
    """Calculates one-vs-rest binary calibration metrics for multi-class predictions

    (e.g., no_pain_related_activity, low, moderate, high).
    """
    if class_names is None:
        class_names = ["no_pain_related_activity", "low", "moderate", "high"]

    y_true = np.asarray(y_true, dtype=int)
    probabilities_matrix = np.asarray(probabilities_matrix, dtype=float)

    per_class_results = {}
    total_ece = 0.0
    total_brier = 0.0

    num_classes = len(class_names)
    for idx, c_name in enumerate(class_names):
        binary_y_true = (y_true == idx).astype(int)
        class_probs = (
            probabilities_matrix[:, idx]
            if probabilities_matrix.ndim == 2
            else np.zeros_like(binary_y_true)
        )

        res = calculate_binary_calibration_metrics(
            binary_y_true, class_probs, number_of_bins=number_of_bins
        )
        per_class_results[c_name] = res
        total_ece += res["expected_calibration_error"]
        total_brier += res["brier_score"]

    macro_ece = total_ece / max(1, num_classes)
    macro_brier = total_brier / max(1, num_classes)

    return {
        "macro_ece": macro_ece,
        "macro_brier": macro_brier,
        "per_class": per_class_results,
    }
