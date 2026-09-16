from __future__ import annotations

from pathlib import Path
from typing import Any

import librosa
import numpy as np


VOICE_FEATURE_NAMES = [
    "rms",
    "zcr",
    "spectral_centroid",
    "spectral_bandwidth",
    "spectral_rolloff",
    "mfcc_1",
    "mfcc_2",
    "mfcc_3",
    "mfcc_4",
    "mfcc_5",
    "mfcc_6",
    "mfcc_7",
    "mfcc_8",
    "mfcc_9",
    "mfcc_10",
    "f0",
]


def extract_voice_sequence(
    audio_path: str | Path,
    target_sample_rate: int = 16000,
    hop_length: int = 512,
    n_fft: int = 2048,
) -> dict[str, Any]:
    audio_path = Path(audio_path)

    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    audio, sample_rate = librosa.load(
        str(audio_path),
        sr=target_sample_rate,
        mono=True,
    )

    if audio.size == 0:
        raise ValueError("Audio file contains no samples")

    peak = np.max(np.abs(audio))
    normalized_audio = audio / peak if peak > 0 else audio

    rms = librosa.feature.rms(y=normalized_audio, frame_length=n_fft, hop_length=hop_length)[0]
    zcr = librosa.feature.zero_crossing_rate(normalized_audio, frame_length=n_fft, hop_length=hop_length)[0]
    centroid = librosa.feature.spectral_centroid(y=normalized_audio, sr=sample_rate, n_fft=n_fft, hop_length=hop_length)[0]
    bandwidth = librosa.feature.spectral_bandwidth(y=normalized_audio, sr=sample_rate, n_fft=n_fft, hop_length=hop_length)[0]
    rolloff = librosa.feature.spectral_rolloff(y=normalized_audio, sr=sample_rate, n_fft=n_fft, hop_length=hop_length)[0]

    mfcc = librosa.feature.mfcc(y=normalized_audio, sr=sample_rate, n_mfcc=10, n_fft=n_fft, hop_length=hop_length)

    f0, _, _ = librosa.pyin(
        normalized_audio,
        fmin=librosa.note_to_hz("C2"),
        fmax=librosa.note_to_hz("C7"),
        sr=sample_rate,
        frame_length=n_fft,
        hop_length=hop_length,
    )
    f0_clean = np.nan_to_num(f0, nan=0.0)

    # Combine into matrix of shape [time_steps, 16]
    sequence_matrix = np.column_stack([
        rms,
        zcr,
        centroid,
        bandwidth,
        rolloff,
        mfcc.T,
        f0_clean,
    ]).astype(np.float32)

    return {
        "features": sequence_matrix,
        "feature_names": VOICE_FEATURE_NAMES,
        "sample_rate": sample_rate,
        "duration_seconds": float(len(audio) / sample_rate),
        "frame_count": int(len(sequence_matrix)),
    }
