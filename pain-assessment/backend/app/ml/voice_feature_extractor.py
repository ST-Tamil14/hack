from __future__ import annotations

from pathlib import Path
from typing import Any

import librosa
import numpy as np


def safe_float(value: Any) -> float | None:
    """
    Convert NumPy numeric values into regular Python floats.
    """
    if value is None:
        return None

    value = float(value)

    if not np.isfinite(value):
        return None

    return round(value, 6)


def calculate_statistics(values: np.ndarray) -> dict[str, float | None]:
    """
    Calculate basic statistics for a numeric array.
    """
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]

    if values.size == 0:
        return {
            "mean": None,
            "stddev": None,
            "min": None,
            "max": None,
            "median": None,
        }

    return {
        "mean": safe_float(np.mean(values)),
        "stddev": safe_float(np.std(values)),
        "min": safe_float(np.min(values)),
        "max": safe_float(np.max(values)),
        "median": safe_float(np.median(values)),
    }


def count_contiguous_regions(
    boolean_array: np.ndarray,
) -> int:
    """
    Count continuous True regions in a Boolean array.
    """
    if boolean_array.size == 0:
        return 0

    padded = np.concatenate(
        [
            np.array([False]),
            boolean_array,
            np.array([False]),
        ]
    )

    starts = np.logical_and(
        ~padded[:-1],
        padded[1:],
    )

    ends = np.logical_and(
        padded[:-1],
        ~padded[1:],
    )

    return int(min(np.sum(starts), np.sum(ends)))


def estimate_vocal_events(
    audio: np.ndarray,
    sample_rate: int,
    rms: np.ndarray,
    hop_length: int = 512,
) -> dict[str, Any]:
    """
    Estimate non-speech vocal events using simple acoustic heuristics.

    This is a preliminary rule-based detector. A trained classifier
    should be used for reliable moaning, crying, or gasping detection.
    """

    if audio.size == 0 or rms.size == 0:
        return {
            "high_energy_event_count": 0,
            "low_frequency_event_count": 0,
            "short_vocal_burst_count": 0,
            "long_vocal_event_count": 0,
            "estimated_vocal_event_count": 0,
            "estimated_vocal_event_rate": 0.0,
            "event_duration_mean_seconds": 0.0,
            "event_duration_max_seconds": 0.0,
        }

    rms_threshold = max(
        float(np.percentile(rms, 65)),
        0.01,
    )

    active_frames = rms > rms_threshold

    event_count = count_contiguous_regions(
        active_frames
    )

    frame_duration = hop_length / sample_rate

    event_lengths: list[float] = []

    start_index: int | None = None

    for index, is_active in enumerate(active_frames):
        if is_active and start_index is None:
            start_index = index

        elif not is_active and start_index is not None:
            duration = (
                index - start_index
            ) * frame_duration

            event_lengths.append(duration)
            start_index = None

    if start_index is not None:
        duration = (
            len(active_frames) - start_index
        ) * frame_duration

        event_lengths.append(duration)

    short_vocal_burst_count = sum(
        0.05 <= duration < 0.50
        for duration in event_lengths
    )

    long_vocal_event_count = sum(
        duration >= 0.50
        for duration in event_lengths
    )

    # Low-frequency energy can be useful for detecting some
    # groaning or moaning-like sounds, but it is not pain-specific.
    spectrogram = np.abs(
        librosa.stft(
            audio,
            n_fft=2048,
            hop_length=hop_length,
        )
    )

    frequencies = librosa.fft_frequencies(
        sr=sample_rate,
        n_fft=2048,
    )

    low_frequency_mask = frequencies < 500

    if np.any(low_frequency_mask):
        low_frequency_energy = np.mean(
            spectrogram[low_frequency_mask],
            axis=0,
        )

        low_frequency_threshold = np.percentile(
            low_frequency_energy,
            70,
        )

        low_frequency_events = (
            low_frequency_energy
            > low_frequency_threshold
        )

        low_frequency_event_count = (
            count_contiguous_regions(
                low_frequency_events
            )
        )
    else:
        low_frequency_event_count = 0

    duration_seconds = len(audio) / sample_rate

    event_rate = (
        event_count / duration_seconds
        if duration_seconds > 0
        else 0.0
    )

    return {
        "high_energy_event_count": event_count,
        "low_frequency_event_count": (
            low_frequency_event_count
        ),
        "short_vocal_burst_count": (
            short_vocal_burst_count
        ),
        "long_vocal_event_count": (
            long_vocal_event_count
        ),
        "estimated_vocal_event_count": event_count,
        "estimated_vocal_event_rate": safe_float(
            event_rate
        ),
        "event_duration_mean_seconds": safe_float(
            np.mean(event_lengths)
            if event_lengths
            else 0.0
        ),
        "event_duration_max_seconds": safe_float(
            np.max(event_lengths)
            if event_lengths
            else 0.0
        ),
    }


def extract_voice_features(
    file_path: str | Path,
    target_sample_rate: int = 16000,
) -> dict[str, Any]:
    """
    Extract preliminary acoustic features from an audio file.

    Extracted feature groups:
    - Audio metadata
    - Loudness/RMS
    - Zero-crossing rate
    - Spectral features
    - Fundamental frequency/pitch
    - Voiced and pause ratios
    - Non-speech vocalization estimates
    - MFCC features
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Audio file was not found: {file_path}"
        )

    audio, sample_rate = librosa.load(
        str(file_path),
        sr=target_sample_rate,
        mono=True,
    )

    if audio.size == 0:
        raise ValueError("The audio file contains no samples.")

    duration_seconds = len(audio) / sample_rate

    # Normalize very loud input while preserving silence.
    peak = np.max(np.abs(audio))

    if peak > 0:
        normalized_audio = audio / peak
    else:
        normalized_audio = audio

    # Frame-level loudness.
    rms = librosa.feature.rms(
        y=normalized_audio,
        frame_length=2048,
        hop_length=512,
    )[0]

    vocal_events = estimate_vocal_events(
        audio=normalized_audio,
        sample_rate=sample_rate,
        rms=rms,
        hop_length=512,
    )

    # Zero-crossing rate.
    zero_crossing_rate = librosa.feature.zero_crossing_rate(
        normalized_audio,
        frame_length=2048,
        hop_length=512,
    )[0]

    # Spectral features.
    spectral_centroid = librosa.feature.spectral_centroid(
        y=normalized_audio,
        sr=sample_rate,
        n_fft=2048,
        hop_length=512,
    )[0]

    spectral_bandwidth = librosa.feature.spectral_bandwidth(
        y=normalized_audio,
        sr=sample_rate,
        n_fft=2048,
        hop_length=512,
    )[0]

    spectral_rolloff = librosa.feature.spectral_rolloff(
        y=normalized_audio,
        sr=sample_rate,
        n_fft=2048,
        hop_length=512,
        roll_percent=0.85,
    )[0]

    # Fundamental frequency estimation.
    f0, voiced_flag, voiced_probabilities = librosa.pyin(
        normalized_audio,
        fmin=librosa.note_to_hz("C2"),
        fmax=librosa.note_to_hz("C7"),
        sr=sample_rate,
        frame_length=2048,
        hop_length=512,
    )

    valid_f0 = f0[np.isfinite(f0)]

    # Estimate silence using an RMS threshold.
    rms_threshold = max(
        float(np.max(rms)) * 0.10,
        0.001,
    )

    voiced_rms_frames = rms > rms_threshold

    voiced_ratio = (
        float(np.mean(voiced_rms_frames))
        if rms.size > 0
        else 0.0
    )

    pause_ratio = 1.0 - voiced_ratio

    # Count transitions from voiced to pause.
    pause_starts = np.logical_and(
        ~voiced_rms_frames[:-1],
        voiced_rms_frames[1:],
    )

    pause_count = int(np.sum(pause_starts))

    # MFCC features.
    mfcc = librosa.feature.mfcc(
        y=normalized_audio,
        sr=sample_rate,
        n_mfcc=13,
        n_fft=2048,
        hop_length=512,
    )

    mfcc_features: dict[str, float | None] = {}

    for index, coefficient in enumerate(mfcc):
        statistics = calculate_statistics(coefficient)

        mfcc_features[
            f"mfcc_{index + 1}_mean"
        ] = statistics["mean"]

        mfcc_features[
            f"mfcc_{index + 1}_stddev"
        ] = statistics["stddev"]

    f0_statistics = calculate_statistics(valid_f0)

    rms_statistics = calculate_statistics(rms)
    zcr_statistics = calculate_statistics(zero_crossing_rate)
    centroid_statistics = calculate_statistics(spectral_centroid)
    bandwidth_statistics = calculate_statistics(spectral_bandwidth)
    rolloff_statistics = calculate_statistics(spectral_rolloff)

    # Audio quality estimation.
    clipping_ratio = float(
        np.mean(np.abs(audio) >= 0.99)
    )

    silence_ratio = pause_ratio

    quality_score = 1.0

    if clipping_ratio > 0.05:
        quality_score -= 0.25

    if silence_ratio > 0.90:
        quality_score -= 0.35

    if duration_seconds < 0.5:
        quality_score -= 0.25

    quality_score = max(
        0.0,
        min(1.0, quality_score),
    )

    features: dict[str, Any] = {
        "sample_rate": sample_rate,
        "sample_count": int(len(audio)),
        "duration_seconds": safe_float(duration_seconds),

        "rms_mean": rms_statistics["mean"],
        "rms_stddev": rms_statistics["stddev"],
        "rms_min": rms_statistics["min"],
        "rms_max": rms_statistics["max"],

        "zero_crossing_rate_mean": zcr_statistics["mean"],
        "zero_crossing_rate_stddev": zcr_statistics["stddev"],

        "spectral_centroid_mean": centroid_statistics["mean"],
        "spectral_centroid_stddev": centroid_statistics["stddev"],

        "spectral_bandwidth_mean": bandwidth_statistics["mean"],
        "spectral_bandwidth_stddev": bandwidth_statistics["stddev"],

        "spectral_rolloff_mean": rolloff_statistics["mean"],
        "spectral_rolloff_stddev": rolloff_statistics["stddev"],

        "f0_mean_hz": f0_statistics["mean"],
        "f0_stddev_hz": f0_statistics["stddev"],
        "f0_min_hz": f0_statistics["min"],
        "f0_max_hz": f0_statistics["max"],
        "f0_median_hz": f0_statistics["median"],

        "voiced_ratio": safe_float(voiced_ratio),
        "pause_ratio": safe_float(pause_ratio),
        "pause_count": pause_count,

        "clipping_ratio": safe_float(clipping_ratio),
        "quality_score": safe_float(quality_score),

        "vocal_events": vocal_events,

        "mfcc": mfcc_features,
    }

    return features
