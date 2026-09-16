from functools import lru_cache
from pathlib import Path
from typing import Any

import whisper


@lru_cache(maxsize=1)
def load_whisper_model():
    return whisper.load_model("tiny")


def transcribe_audio(audio_path: str | Path) -> dict[str, Any]:
    audio_path = Path(audio_path)
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    try:
        model = load_whisper_model()
        result = model.transcribe(
            str(audio_path),
            task="transcribe",
            fp16=False,
        )

        return {
            "text": result.get("text", "").strip(),
            "language": result.get("language"),
            "segments": result.get("segments", []),
        }
    except Exception as error:
        return {
            "text": "",
            "language": None,
            "segments": [],
            "error": str(error),
        }
