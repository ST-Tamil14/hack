from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.ml.fusion_model import FUSION_FEATURE_NAMES


OUTPUT_DIR = PROJECT_ROOT / "datasets" / "processed" / "fusion"

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


def prepare_dataset() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    csv_candidates = [
        PROJECT_ROOT / "datasets" / "raw" / "synthetic_full_multimodal_pain_dataset_500.csv",
        PROJECT_ROOT / "datasets" / "raw" / "facial" / "synthetic_multimodal_pain_dataset_500.csv",
        PROJECT_ROOT / "datasets" / "annotations" / "fusion" / "fusion_annotations.csv",
    ]

    annotation_path = next((p for p in csv_candidates if p.exists()), None)

    if not annotation_path:
        raise FileNotFoundError(f"No fusion dataset file found in candidates: {csv_candidates}")

    print(f"Loading fusion dataset from: {annotation_path}")
    df = pd.read_csv(annotation_path)

    features_list = []
    labels_list = []

    for _, row in df.iterrows():
        f_score = float(row.get("facial_pain_score") or row.get("facial_score") or 0.0)
        p_score = float(row.get("physiological_pain_score") or row.get("physiological_score") or 0.0)
        b_score = float(row.get("behavioral_pain_score") or row.get("behavioral_score") or 0.0)
        v_score = float(row.get("audio_pain_score") or row.get("voice_score") or 0.0)

        f_conf = float(row.get("AI_confidence") or row.get("facial_confidence") or 0.8)
        p_conf = float(row.get("physio_model_confidence") or row.get("physiological_confidence") or 0.8)
        b_conf = float(row.get("behavioral_confidence") or 0.8)
        v_conf = float(row.get("voice_confidence") or 0.8)

        f_qual = float(row.get("facial_quality_weight") or 0.9)
        p_qual = float(row.get("physiological_quality_weight") or 0.9)
        b_qual = float(row.get("behavior_quality_weight") or 0.9)
        v_qual = float(row.get("audio_quality_weight") or 0.9)

        f_avail = 1.0 if pd.notna(row.get("facial_pain_score") or row.get("facial_score")) else 0.0
        p_avail = 1.0 if pd.notna(row.get("physiological_pain_score") or row.get("physiological_score")) else 0.0
        b_avail = 1.0 if pd.notna(row.get("behavioral_pain_score") or row.get("behavioral_score")) else 0.0
        v_avail = 1.0 if pd.notna(row.get("audio_pain_score") or row.get("voice_score")) else 0.0

        # Profile indicators
        comm = str(row.get("communication_ability", "")).lower()
        mobility = str(row.get("mobility_status", "")).lower()
        sedation = str(row.get("sedation_status", "")).lower()

        c_nonverbal = 1.0 if "non-verbal" in comm or "non verbal" in comm else 0.0
        c_intubated = 1.0 if "intubated" in comm else 0.0
        m_restricted = 1.0 if "restricted" in mobility or "limited" in mobility or "assisted" in mobility else 0.0
        f_limitation = 1.0 if row.get("facial_movement_limitation") is True else 0.0
        s_limitation = 1.0 if row.get("speech_limitation") is True else 0.0
        sedated = 1.0 if "sedated" in sedation or "moderate" in sedation or "heavy" in sedation else 0.0

        feature_vector = [
            f_score, p_score, b_score, v_score,
            f_conf, p_conf, b_conf, v_conf,
            f_qual, p_qual, b_qual, v_qual,
            f_avail, p_avail, b_avail, v_avail,
            c_nonverbal, c_intubated, m_restricted, f_limitation, s_limitation, sedated,
        ]

        features_list.append(feature_vector)

        # Label resolution
        if "final_label" in row and pd.notna(row["final_label"]):
            l_val = row["final_label"]
            label = int(l_val) if str(l_val).isdigit() else PAIN_CLASS_MAPPING.get(str(l_val), 0)
        elif "pain_class" in row and pd.notna(row["pain_class"]):
            p_val = row["pain_class"]
            label = int(p_val) if str(p_val).isdigit() else PAIN_CLASS_MAPPING.get(str(p_val), 0)
        else:
            label = 0

        labels_list.append(label)

    X = np.asarray(features_list, dtype=np.float32)
    y = np.asarray(labels_list, dtype=np.int64)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X).astype(np.float32)

    np.savez(
        OUTPUT_DIR / "fusion_dataset.npz",
        X=X_scaled,
        y=y,
    )

    np.savez(
        OUTPUT_DIR / "fusion_scaler.npz",
        mean=scaler.mean_,
        scale=scaler.scale_,
    )

    metadata = {
        "feature_names": FUSION_FEATURE_NAMES,
        "feature_count": len(FUSION_FEATURE_NAMES),
        "sample_count": len(X),
        "class_count": 4,
    }

    with open(OUTPUT_DIR / "fusion_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print("Fusion dataset prepared successfully")
    print(f"Samples: {len(X)}")
    print(f"Features: {len(FUSION_FEATURE_NAMES)}")


if __name__ == "__main__":
    prepare_dataset()
