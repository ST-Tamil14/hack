import json
import os
import tempfile
from pathlib import Path
from typing import Any

import cv2
import librosa
import numpy as np
import pandas as pd
from fastapi import HTTPException

from app.db.supabase_client import supabase
from app.ml.behavioral_feature_extractor import (
    BehavioralFeatureExtractor,
)
from app.ml.facial_feature_extractor import (
    FacialFeatureExtractor,
)
from app.ml.physiological_feature_extractor import (
    PhysiologicalFeatureExtractor,
)
from app.ml.voice_feature_extractor import (
    extract_voice_features,
)
from app.services.preprocessing_service import (
    download_storage_file,
    get_file_record,
)


def get_processing_job(job_id: str) -> dict[str, Any]:
    response = (
        supabase.table("processing_jobs")
        .select("*")
        .eq("id", job_id)
        .maybe_single()
        .execute()
    )

    if not response or not response.data:
        raise HTTPException(
            status_code=404,
            detail="Processing job not found",
        )

    return response.data


def extract_facial_features(
    file_path: str,
) -> dict[str, Any]:
    extractor = FacialFeatureExtractor()

    try:
        return extractor.extract_from_video(
            file_path=file_path,
            sample_every_n_frames=5,
        )
    finally:
        extractor.close()


def extract_behavioral_features(
    file_path: str,
) -> dict[str, Any]:
    extractor = BehavioralFeatureExtractor()

    try:
        return extractor.extract_from_video(
            file_path=file_path,
            sample_every_n_frames=5,
        )
    finally:
        extractor.close()


def extract_physiological_features(
    file_path: str,
    extension: str,
) -> dict[str, Any]:
    extractor = PhysiologicalFeatureExtractor()

    return extractor.extract(
        file_path=file_path,
        extension=extension,
    )


def extract_video_features(file_path: str) -> dict[str, Any]:
    capture = cv2.VideoCapture(file_path)

    if not capture.isOpened():
        raise ValueError("Unable to open video file")

    frame_count = int(
        capture.get(cv2.CAP_PROP_FRAME_COUNT)
    )

    fps = float(
        capture.get(cv2.CAP_PROP_FPS)
    )

    width = int(
        capture.get(cv2.CAP_PROP_FRAME_WIDTH)
    )

    height = int(
        capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
    )

    brightness_values = []
    motion_values = []

    previous_frame = None
    sampled_frames = 0

    while True:
        success, frame = capture.read()

        if not success:
            break

        # Process every fifth frame to reduce computation.
        if sampled_frames % 5 != 0:
            sampled_frames += 1
            continue

        gray_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY,
        )

        brightness_values.append(
            float(np.mean(gray_frame))
        )

        if previous_frame is not None:
            frame_difference = cv2.absdiff(
                gray_frame,
                previous_frame,
            )

            motion_values.append(
                float(np.mean(frame_difference))
            )

        previous_frame = gray_frame
        sampled_frames += 1

    capture.release()

    duration = None

    if fps > 0:
        duration = frame_count / fps

    return {
        "frame_count": frame_count,
        "fps": fps,
        "width": width,
        "height": height,
        "duration_seconds": duration,
        "average_brightness": calculate_mean(
            brightness_values
        ),
        "average_motion": calculate_mean(
            motion_values
        ),
        "motion_variability": calculate_std(
            motion_values
        ),
    }


def extract_audio_features(file_path: str) -> dict[str, Any]:
    audio, sample_rate = librosa.load(
        file_path,
        sr=None,
        mono=True,
    )

    if len(audio) == 0:
        raise ValueError("Audio file is empty")

    duration = len(audio) / sample_rate

    rms_values = librosa.feature.rms(
        y=audio
    )[0]

    zero_crossing_values = (
        librosa.feature.zero_crossing_rate(audio)[0]
    )

    spectral_centroid_values = (
        librosa.feature.spectral_centroid(
            y=audio,
            sr=sample_rate,
        )[0]
    )

    mfcc_values = librosa.feature.mfcc(
        y=audio,
        sr=sample_rate,
        n_mfcc=13,
    )

    return {
        "sample_rate": float(sample_rate),
        "sample_count": int(len(audio)),
        "duration_seconds": float(duration),
        "rms_mean": calculate_mean(rms_values),
        "rms_stddev": calculate_std(rms_values),
        "zero_crossing_rate_mean": calculate_mean(
            zero_crossing_values
        ),
        "spectral_centroid_mean": calculate_mean(
            spectral_centroid_values
        ),
        "mfcc_mean": [
            float(value)
            for value in np.mean(
                mfcc_values,
                axis=1,
            )
        ],
        "mfcc_stddev": [
            float(value)
            for value in np.std(
                mfcc_values,
                axis=1,
            )
        ],
    }


def extract_tabular_features(
    file_path: str,
    extension: str,
) -> dict[str, Any]:
    if extension == ".csv":
        dataframe = pd.read_csv(file_path)

    elif extension == ".json":
        with open(
            file_path,
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        if isinstance(data, list):
            dataframe = pd.DataFrame(data)
        else:
            dataframe = pd.DataFrame([data])

    else:
        raise ValueError(
            f"Unsupported tabular extension: {extension}"
        )

    numeric_dataframe = dataframe.select_dtypes(
        include=[np.number]
    )

    features: dict[str, Any] = {
        "sample_count": int(len(dataframe)),
        "column_count": int(len(dataframe.columns)),
        "missing_value_count": int(
            dataframe.isnull().sum().sum()
        ),
        "numeric_feature_count": int(
            len(numeric_dataframe.columns)
        ),
    }

    for column in numeric_dataframe.columns:
        values = numeric_dataframe[column].dropna()

        if values.empty:
            continue

        features[f"{column}_mean"] = float(
            values.mean()
        )

        features[f"{column}_stddev"] = float(
            values.std()
            if len(values) > 1
            else 0.0
        )

        features[f"{column}_minimum"] = float(
            values.min()
        )

        features[f"{column}_maximum"] = float(
            values.max()
        )

    return features


def calculate_mean(values: Any) -> float:
    values = list(values)

    if not values:
        return 0.0

    return round(float(np.mean(values)), 6)


def calculate_std(values: Any) -> float:
    values = list(values)

    if not values:
        return 0.0

    return round(float(np.std(values)), 6)


def save_extracted_features(
    patient_id: str,
    file_id: str,
    processing_job_id: str,
    modality: str,
    features: dict[str, Any],
    quality_score: float | None = None,
) -> dict[str, Any]:
    payload = {
        "patient_id": patient_id,
        "file_id": file_id,
        "processing_job_id": processing_job_id,
        "modality": modality,
        "feature_version": "v1",
        "features": features,
        "feature_count": len(features),
        "quality_score": quality_score,
        "extraction_status": "completed",
    }

    response = (
        supabase.table("extracted_features")
        .insert(payload)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=500,
            detail="Failed to save extracted features",
        )

    return response.data[0]


def extract_features(
    file_id: str,
    processing_job_id: str,
) -> dict[str, Any]:
    file_record = get_file_record(file_id)
    job_record = get_processing_job(processing_job_id)

    if job_record["file_id"] != file_id:
        raise HTTPException(
            status_code=400,
            detail="File and processing job do not match",
        )

    temporary_path = None

    try:
        temporary_path, extension = download_storage_file(
            file_record["storage_path"]
        )

        modality = file_record["modality"]
        content_type = file_record["content_type"]

        if content_type.startswith("video/"):
            if modality == "facial":
                features = extract_facial_features(
                    temporary_path
                )
            elif modality == "behavioral":
                features = extract_behavioral_features(
                    temporary_path
                )
            else:
                features = extract_video_features(
                    temporary_path
                )

        elif content_type.startswith("audio/"):
            if modality == "voice":
                features = extract_voice_features(
                    temporary_path
                )
            else:
                features = extract_audio_features(
                    temporary_path
                )

        elif (
            extension in {".csv", ".json"}
            or content_type == "text/csv"
        ):
            if modality == "physiological":
                features = extract_physiological_features(
                    file_path=temporary_path,
                    extension=extension,
                )
            else:
                features = extract_tabular_features(
                    file_path=temporary_path,
                    extension=extension,
                )

        else:
            raise ValueError(
                f"Unsupported content type: {content_type}"
            )

        result = save_extracted_features(
            patient_id=file_record["patient_id"],
            file_id=file_id,
            processing_job_id=processing_job_id,
            modality=modality,
            features=features,
            quality_score=features.get("quality_score")
            or file_record.get("quality_score"),
        )

        return result

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Feature extraction failed: {str(exc)}",
        )

    finally:
        if temporary_path and os.path.exists(
            temporary_path
        ):
            os.remove(temporary_path)
