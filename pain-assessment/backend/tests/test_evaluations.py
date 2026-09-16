import numpy as np
import pytest

from app.ml.evaluation_utils import (
    calculate_classification_metrics,
    calculate_multiclass_sensitivity_specificity,
)
from app.schemas.evaluation import ModelEvaluationCreate
from app.services.evaluation_service import (
    get_model_evaluations,
    save_model_evaluation,
)


def test_model_evaluation_schema():
    eval_input = {
        "model_name": "test_facial_model",
        "model_version": "v1.0",
        "modality": "facial",
        "accuracy": 0.85,
        "precision_score": 0.82,
        "recall_score": 0.84,
        "f1_score": 0.83,
        "sensitivity": 0.80,
        "specificity": 0.90,
    }
    schema = ModelEvaluationCreate(**eval_input)
    assert schema.model_name == "test_facial_model"
    assert schema.accuracy == 0.85
    assert schema.f1_score == 0.83


def test_classification_metrics_calculation():
    y_true = [0, 1, 2, 3, 0, 1, 2, 3]
    y_pred = [0, 1, 2, 3, 0, 1, 2, 2]  # 7/8 correct

    metrics = calculate_classification_metrics(y_true, y_pred)
    assert "accuracy" in metrics
    assert "precision_score" in metrics
    assert "recall_score" in metrics
    assert "f1_score" in metrics
    assert "confusion_matrix" in metrics
    assert metrics["accuracy"] == 7 / 8


def test_multiclass_sensitivity_specificity():
    y_true = [0, 0, 1, 1, 2, 2]
    y_pred = [0, 0, 1, 2, 2, 2]

    sens_spec = calculate_multiclass_sensitivity_specificity(y_true, y_pred)
    assert "0" in sens_spec
    assert "1" in sens_spec
    assert "2" in sens_spec

    # Class 0: 2/2 true positive -> sensitivity 1.0
    assert sens_spec["0"]["sensitivity"] == 1.0
    assert sens_spec["0"]["specificity"] == 1.0


def test_save_and_get_model_evaluations():
    eval_payload = {
        "model_name": "unit_test_model",
        "model_version": "v1.0.0",
        "modality": "physiological",
        "accuracy": 0.92,
        "f1_score": 0.91,
    }

    saved = save_model_evaluation(eval_payload, evaluated_by="test-user")
    assert saved["model_name"] == "unit_test_model"

    results = get_model_evaluations(model_name="unit_test_model")
    assert len(results) >= 1
    assert results[0]["model_name"] == "unit_test_model"
