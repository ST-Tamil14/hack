from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


PHYSIOLOGICAL_FEATURE_NAMES = [
    "heart_rate",
    "hrv",
    "respiration_rate",
    "eda_gsr",
    "skin_temperature",
    "spo2",
    "systolic_bp",
    "diastolic_bp",
]

COLUMN_MAPPING = {
    "heart_rate_bpm": "heart_rate",
    "Hr": "heart_rate",
    "hrv_rmssd_ms": "hrv",
    "Ibi": "hrv",
    "respiratory_rate_bpm": "respiration_rate",
    "Resp": "respiration_rate",
    "eda_microsiemens": "eda_gsr",
    "Eda_E4": "eda_gsr",
    "Eda_RB": "eda_gsr",
    "skin_temperature_c": "skin_temperature",
    "Tmp": "skin_temperature",
    "spo2_percent": "spo2",
    "systolic_bp_mmhg": "systolic_bp",
    "diastolic_bp_mmhg": "diastolic_bp",
}

PAIN_CLASS_MAPPING = {
    "No Pain": 0,
    "no pain": 0,
    "Low": 1,
    "low": 1,
    "Moderate": 2,
    "moderate": 2,
    "High": 3,
    "high": 3,
}


def load_physiological_file(file_path: str | Path) -> pd.DataFrame:
    """
    Load physiological data from CSV or JSON with automatic format detection.
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if file_path.suffix.lower() == ".csv":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as file_handle:
            first_line = file_handle.readline()

        sep = ";" if ";" in first_line else ","
        decimal = "," if (sep == ";" and "," in first_line) else "."

        dataframe = pd.read_csv(file_path, sep=sep, decimal=decimal, low_memory=False)

    elif file_path.suffix.lower() == ".json":
        dataframe = pd.read_json(file_path)

    else:
        raise ValueError("Only CSV and JSON files are supported")

    # Standardize column names using mapping
    dataframe = dataframe.rename(columns=COLUMN_MAPPING)

    # Remove duplicate columns if multiple aliases map to the same name (e.g. Eda_E4 and Eda_RB)
    if dataframe.columns.duplicated().any():
        dataframe = dataframe.loc[:, ~dataframe.columns.duplicated(keep="first")]

    # Downsample high-frequency streams (e.g., 250Hz PMHDB) to ~1Hz time-series
    if ("Seconds" in dataframe.columns or "seconds" in dataframe.columns) and len(dataframe) > 5000:
        downsample_factor = 250
        dataframe = dataframe.iloc[::downsample_factor].reset_index(drop=True)

    # Derive pain label from PMHDB continuous COVAS (0-100) scale or thermal stimulus
    if "COVAS" in dataframe.columns and "label" not in dataframe.columns and "pain_class" not in dataframe.columns:
        covas_col = dataframe["COVAS"]
        if isinstance(covas_col, pd.DataFrame):
            covas_col = covas_col.iloc[:, 0]
        covas = pd.to_numeric(covas_col, errors="coerce").fillna(0.0)
        labels = np.zeros(len(covas), dtype=np.int64)
        labels[covas >= 5.0] = 1
        labels[covas >= 35.0] = 2
        labels[covas >= 65.0] = 3
        dataframe["label"] = labels
    elif "Heater_cleaned" in dataframe.columns and "label" not in dataframe.columns and "pain_class" not in dataframe.columns:
        temp_col = dataframe["Heater_cleaned"]
        if isinstance(temp_col, pd.DataFrame):
            temp_col = temp_col.iloc[:, 0]
        temp = pd.to_numeric(temp_col, errors="coerce").fillna(32.0)
        labels = np.zeros(len(temp), dtype=np.int64)
        labels[temp >= 40.0] = 1
        labels[temp >= 44.0] = 2
        labels[temp >= 47.0] = 3
        dataframe["label"] = labels

    return dataframe


def prepare_physiological_dataframe(
    dataframe: pd.DataFrame,
) -> tuple[pd.DataFrame, list[str]]:
    """
    Select physiological columns, ensure all 8 features exist with defaults, and clean missing values.
    """
    selected = pd.DataFrame(index=dataframe.index)

    # Defaults for missing physiological variables
    defaults = {
        "heart_rate": 75.0,
        "hrv": 50.0,
        "respiration_rate": 16.0,
        "eda_gsr": 2.5,
        "skin_temperature": 34.0,
        "spo2": 98.0,
        "systolic_bp": 120.0,
        "diastolic_bp": 80.0,
    }

    for feature in PHYSIOLOGICAL_FEATURE_NAMES:
        if feature in dataframe.columns:
            col_data = dataframe[feature]
            if isinstance(col_data, pd.DataFrame):
                col_data = col_data.iloc[:, 0]
            selected[feature] = pd.to_numeric(col_data, errors="coerce")
        else:
            selected[feature] = defaults[feature]

    # Convert IBI in seconds to HRV (ms) if needed
    if "hrv" in selected.columns:
        valid_hrv = selected["hrv"].dropna()
        if not valid_hrv.empty and valid_hrv.median() < 5.0:
            selected["hrv"] = selected["hrv"] * 1000.0

    selected = selected.replace([np.inf, -np.inf], np.nan)
    selected = selected.interpolate(limit_direction="both")
    for feature in PHYSIOLOGICAL_FEATURE_NAMES:
        selected[feature] = selected[feature].fillna(defaults[feature])

    return selected[PHYSIOLOGICAL_FEATURE_NAMES], PHYSIOLOGICAL_FEATURE_NAMES


def create_physiological_windows(
    values: np.ndarray,
    labels: np.ndarray | None = None,
    window_size: int = 32,
    stride: int = 8,
) -> tuple[np.ndarray, np.ndarray | None]:
    """
    Convert a continuous physiological sequence into fixed-length windows.
    """
    if values.ndim != 2:
        raise ValueError("values must have shape [time_steps, feature_count]")

    if len(values) < window_size:
        return (
            np.empty((0, window_size, values.shape[1]), dtype=np.float32),
            None if labels is None else np.empty((0,), dtype=np.int64),
        )

    windows: list[np.ndarray] = []
    window_labels: list[int] = []

    for start in range(0, len(values) - window_size + 1, stride):
        end = start + window_size

        windows.append(values[start:end])

        if labels is not None:
            current_labels = labels[start:end]

            # Majority label inside the window
            counts = np.bincount(current_labels.astype(int), minlength=4)
            window_labels.append(int(np.argmax(counts)))

    window_array = np.asarray(windows, dtype=np.float32)

    if labels is None:
        return window_array, None

    return (
        window_array,
        np.asarray(window_labels, dtype=np.int64),
    )


def extract_physiological_sequence(
    file_path: str | Path,
    window_size: int = 32,
    stride: int = 8,
) -> dict[str, Any]:
    """
    Load a physiological file and create normalized-ready windows.
    """
    dataframe = load_physiological_file(file_path)
    prepared, feature_names = prepare_physiological_dataframe(dataframe)

    values = prepared.to_numpy(dtype=np.float32)

    labels = None

    if "label" in dataframe.columns:
        labels = pd.to_numeric(
            dataframe["label"],
            errors="coerce",
        ).fillna(0).to_numpy(dtype=np.int64)
    elif "pain_class" in dataframe.columns:
        labels = (
            dataframe["pain_class"]
            .map(PAIN_CLASS_MAPPING)
            .fillna(0)
            .to_numpy(dtype=np.int64)
        )

    windows, window_labels = create_physiological_windows(
        values=values,
        labels=labels,
        window_size=window_size,
        stride=stride,
    )

    return {
        "windows": windows,
        "labels": window_labels,
        "feature_names": feature_names,
        "sample_count": int(len(values)),
        "window_count": int(len(windows)),
        "feature_count": int(len(feature_names)),
    }
