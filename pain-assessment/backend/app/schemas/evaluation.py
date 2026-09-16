from typing import Any

from pydantic import BaseModel, Field


class ModelEvaluationCreate(BaseModel):
    model_name: str
    model_version: str
    modality: str

    dataset_name: str | None = None
    evaluation_type: str | None = None

    sample_count: int | None = None
    patient_count: int | None = None

    accuracy: float | None = Field(default=None, ge=0, le=1)
    precision_score: float | None = Field(default=None, ge=0, le=1)
    recall_score: float | None = Field(default=None, ge=0, le=1)
    f1_score: float | None = Field(default=None, ge=0, le=1)
    sensitivity: float | None = Field(default=None, ge=0, le=1)
    specificity: float | None = Field(default=None, ge=0, le=1)
    roc_auc: float | None = Field(default=None, ge=0, le=1)

    mae: float | None = Field(default=None, ge=0)
    rmse: float | None = Field(default=None, ge=0)
    correlation: float | None = None

    language: str | None = None
    age_group: str | None = None
    clinical_group: str | None = None

    missing_modality_condition: str | None = None
    noise_condition: str | None = None

    confusion_matrix: dict[str, Any] | list[Any] | None = None
    class_metrics: dict[str, Any] | None = None
    notes: str | None = None
