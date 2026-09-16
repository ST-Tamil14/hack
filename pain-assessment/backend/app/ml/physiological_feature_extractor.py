from typing import Any

import numpy as np
import pandas as pd
from scipy.signal import find_peaks


class PhysiologicalFeatureExtractor:
    """
    Extracts basic physiological features from CSV or JSON data.

    Expected columns may include:
    heart_rate, hrv, respiration_rate, eda_gsr,
    skin_temperature, spo2, systolic_bp, diastolic_bp
    """

    COLUMN_ALIASES = {
        "heart_rate": [
            "heart_rate",
            "hr",
            "pulse",
        ],
        "hrv": [
            "hrv",
            "rmssd",
            "sdnn",
        ],
        "respiration_rate": [
            "respiration_rate",
            "respiratory_rate",
            "resp_rate",
            "rr",
        ],
        "eda_gsr": [
            "eda",
            "eda_gsr",
            "gsr",
            "skin_conductance",
        ],
        "skin_temperature": [
            "skin_temperature",
            "skin_temp",
            "temperature",
        ],
        "spo2": [
            "spo2",
            "oxygen_saturation",
        ],
        "systolic_bp": [
            "systolic_bp",
            "sbp",
        ],
        "diastolic_bp": [
            "diastolic_bp",
            "dbp",
        ],
    }

    def load_data(
        self,
        file_path: str,
        extension: str,
    ) -> pd.DataFrame:
        if extension.lower() == ".csv":
            dataframe = pd.read_csv(file_path)

        elif extension.lower() == ".json":
            dataframe = self._load_json(file_path)

        else:
            raise ValueError(
                f"Unsupported physiological file type: {extension}"
            )

        dataframe.columns = [
            str(column).strip().lower()
            for column in dataframe.columns
        ]

        return dataframe

    def extract(
        self,
        file_path: str,
        extension: str,
    ) -> dict[str, Any]:
        dataframe = self.load_data(
            file_path=file_path,
            extension=extension,
        )

        if dataframe.empty:
            raise ValueError(
                "Physiological data file is empty"
            )

        features: dict[str, Any] = {
            "sample_count": int(len(dataframe)),
            "column_count": int(len(dataframe.columns)),
            "missing_value_count": int(
                dataframe.isnull().sum().sum()
            ),
            "missing_value_ratio": round(
                float(
                    dataframe.isnull().sum().sum()
                    / dataframe.size
                ),
                6,
            ),
        }

        for feature_name, aliases in self.COLUMN_ALIASES.items():
            column_name = self._find_column(
                dataframe,
                aliases,
            )

            if column_name is None:
                continue

            values = pd.to_numeric(
                dataframe[column_name],
                errors="coerce",
            ).dropna()

            if values.empty:
                continue

            numeric_values = values.to_numpy(
                dtype=np.float64
            )

            features[f"{feature_name}_mean"] = self._mean(
                numeric_values
            )

            features[f"{feature_name}_stddev"] = self._std(
                numeric_values
            )

            features[f"{feature_name}_minimum"] = float(
                np.min(numeric_values)
            )

            features[f"{feature_name}_maximum"] = float(
                np.max(numeric_values)
            )

            if feature_name == "eda_gsr":
                features.update(
                    self._extract_eda_features(
                        numeric_values
                    )
                )

            if feature_name == "heart_rate":
                features.update(
                    self._extract_heart_rate_features(
                        numeric_values
                    )
                )

            if feature_name == "respiration_rate":
                features.update(
                    self._extract_respiration_features(
                        numeric_values
                    )
                )

        features["quality_score"] = (
            self._calculate_quality_score(
                dataframe
            )
        )

        return features

    def _load_json(
        self,
        file_path: str,
    ) -> pd.DataFrame:
        data = pd.read_json(file_path)

        if isinstance(data, pd.DataFrame):
            return data

        return pd.DataFrame(data)

    def _find_column(
        self,
        dataframe: pd.DataFrame,
        aliases: list[str],
    ) -> str | None:
        for alias in aliases:
            if alias in dataframe.columns:
                return alias

        return None

    def _extract_eda_features(
        self,
        values: np.ndarray,
    ) -> dict[str, Any]:
        if len(values) < 3:
            return {
                "eda_peak_count": 0,
                "eda_peak_rate": 0.0,
            }

        baseline = np.median(values)
        threshold = baseline + (
            0.5 * np.std(values)
        )

        peaks, _ = find_peaks(
            values,
            height=threshold,
            distance=2,
        )

        return {
            "eda_peak_count": int(len(peaks)),
            "eda_peak_rate": round(
                float(len(peaks) / len(values)),
                6,
            ),
        }

    def _extract_heart_rate_features(
        self,
        values: np.ndarray,
    ) -> dict[str, Any]:
        return {
            "heart_rate_range": round(
                float(np.max(values) - np.min(values)),
                6,
            ),
            "heart_rate_change": round(
                float(values[-1] - values[0]),
                6,
            ),
        }

    def _extract_respiration_features(
        self,
        values: np.ndarray,
    ) -> dict[str, Any]:
        return {
            "respiration_range": round(
                float(np.max(values) - np.min(values)),
                6,
            ),
            "respiration_change": round(
                float(values[-1] - values[0]),
                6,
            ),
        }

    def _calculate_quality_score(
        self,
        dataframe: pd.DataFrame,
    ) -> float:
        missing_ratio = (
            dataframe.isnull().sum().sum()
            / dataframe.size
        )

        score = 1.0 - float(missing_ratio)

        if len(dataframe) < 10:
            score -= 0.2

        return round(
            max(0.0, min(1.0, score)),
            4,
        )

    def _mean(
        self,
        values: np.ndarray,
    ) -> float:
        return round(
            float(np.mean(values)),
            6,
        )

    def _std(
        self,
        values: np.ndarray,
    ) -> float:
        return round(
            float(np.std(values)),
            6,
        )
