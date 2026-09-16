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


VIDEO_TYPES = {
    "video/mp4",
    "video/webm",
    "video/avi",
    "video/mov",
}

AUDIO_TYPES = {
    "audio/wav",
    "audio/mpeg",
    "audio/webm",
    "audio/ogg",
}

TABULAR_TYPES = {
    "text/csv",
    "application/json",
    "application/octet-stream",
}


def get_file_record(file_id: str) -> dict[str, Any]:
    response = (
        supabase.table("multimodal_files")
        .select("*")
        .eq("id", file_id)
        .maybe_single()
        .execute()
    )

    if not response or not response.data:
        raise HTTPException(
            status_code=404,
            detail="File record not found",
        )

    return response.data


def update_file_preprocessing_status(
    file_id: str,
    status: str,
    error_message: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    payload: dict[str, Any] = {
        "preprocessing_status": status,
        "preprocessing_error": error_message,
    }

    if metadata:
        payload.update(metadata)

    supabase.table("multimodal_files").update(
        payload
    ).eq("id", file_id).execute()


def download_storage_file(
    storage_path: str,
) -> tuple[str, str]:
    """
    Downloads a private Supabase Storage file into a temporary file.

    Returns:
        temporary file path and original file extension
    """

    file_response = (
        supabase.storage
        .from_("clinical-data")
        .download(storage_path)
    )

    if not file_response:
        raise HTTPException(
            status_code=404,
            detail="Unable to download file from storage",
        )

    extension = Path(storage_path).suffix.lower()

    temporary_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=extension,
    )

    temporary_file.write(file_response)
    temporary_file.close()

    return temporary_file.name, extension


def calculate_video_metadata(file_path: str) -> dict[str, Any]:
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

    capture.release()

    duration = None

    if fps > 0:
        duration = frame_count / fps

    quality_score = calculate_quality_score(
        width=width,
        height=height,
        duration=duration,
    )

    return {
        "duration_seconds": duration,
        "frame_count": frame_count,
        "width": width,
        "height": height,
        "quality_score": quality_score,
    }


def calculate_audio_metadata(file_path: str) -> dict[str, Any]:
    audio, sample_rate = librosa.load(
        file_path,
        sr=None,
        mono=False,
    )

    if audio.ndim == 1:
        channels = 1
        sample_count = len(audio)
    else:
        channels = audio.shape[0]
        sample_count = audio.shape[-1]

    duration = sample_count / sample_rate

    quality_score = calculate_audio_quality_score(
        audio=audio,
        sample_rate=sample_rate,
    )

    return {
        "duration_seconds": float(duration),
        "channels": channels,
        "sample_count": int(sample_count),
        "sample_rate": float(sample_rate),
        "quality_score": quality_score,
    }


def calculate_tabular_metadata(
    file_path: str,
    extension: str,
) -> dict[str, Any]:
    if extension == ".csv":
        dataframe = pd.read_csv(file_path)

        return {
            "sample_count": int(len(dataframe)),
            "channels": int(len(dataframe.columns)),
            "quality_score": calculate_tabular_quality_score(
                dataframe
            ),
        }

    if extension == ".json":
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            sample_count = len(data)
        else:
            sample_count = 1

        return {
            "sample_count": sample_count,
            "quality_score": 0.8,
        }

    return {
        "quality_score": 0.5,
    }


def calculate_quality_score(
    width: int,
    height: int,
    duration: float | None,
) -> float:
    score = 1.0

    if width < 320 or height < 240:
        score -= 0.3

    if duration is None or duration <= 0:
        score -= 0.3

    return round(max(0.0, min(1.0, score)), 2)


def calculate_audio_quality_score(
    audio: np.ndarray,
    sample_rate: int,
) -> float:
    score = 1.0

    if sample_rate < 8000:
        score -= 0.3

    if np.isnan(audio).any():
        score -= 0.3

    if np.max(np.abs(audio)) < 0.001:
        score -= 0.4

    return round(max(0.0, min(1.0, score)), 2)


def calculate_tabular_quality_score(
    dataframe: pd.DataFrame,
) -> float:
    if dataframe.empty:
        return 0.0

    missing_ratio = (
        dataframe.isnull().sum().sum()
        / dataframe.size
    )

    score = 1.0 - float(missing_ratio)

    return round(max(0.0, min(1.0, score)), 2)


def preprocess_file(file_id: str) -> dict[str, Any]:
    file_record = get_file_record(file_id)

    update_file_preprocessing_status(
        file_id=file_id,
        status="processing",
    )

    temporary_path = None

    try:
        temporary_path, extension = download_storage_file(
            file_record["storage_path"]
        )

        content_type = file_record["content_type"]
        file_size = os.path.getsize(temporary_path)

        metadata: dict[str, Any] = {
            "file_size_bytes": file_size,
        }

        if content_type in VIDEO_TYPES:
            metadata.update(
                calculate_video_metadata(temporary_path)
            )

        elif content_type in AUDIO_TYPES:
            metadata.update(
                calculate_audio_metadata(temporary_path)
            )

        elif content_type in TABULAR_TYPES:
            metadata.update(
                calculate_tabular_metadata(
                    temporary_path,
                    extension,
                )
            )

        else:
            raise ValueError(
                f"Unsupported content type: {content_type}"
            )

        update_file_preprocessing_status(
            file_id=file_id,
            status="completed",
            metadata=metadata,
        )

        return {
            "file_id": file_id,
            "modality": file_record["modality"],
            "file_type": content_type,
            "preprocessing_status": "completed",
            **metadata,
        }

    except Exception as exc:
        update_file_preprocessing_status(
            file_id=file_id,
            status="failed",
            error_message=str(exc),
        )

        raise HTTPException(
            status_code=500,
            detail=f"Preprocessing failed: {str(exc)}",
        )

    finally:
        if temporary_path and os.path.exists(temporary_path):
            os.remove(temporary_path)
