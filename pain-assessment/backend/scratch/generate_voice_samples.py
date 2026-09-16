import numpy as np
from pathlib import Path
from scipy.io import wavfile

VOICE_RAW_DIR = Path("datasets/raw/voice")
VOICE_RAW_DIR.mkdir(parents=True, exist_ok=True)

sr = 16000
frequencies = [200, 250, 320, 410, 270]

for i, freq in enumerate(frequencies, start=1):
    t = np.linspace(0, 3.0, sr * 3, False)
    # Generate audio with fundamental tone and harmonics
    audio_signal = 0.5 * np.sin(2 * np.pi * freq * t) + 0.25 * np.sin(2 * np.pi * 2 * freq * t)
    audio_int16 = (audio_signal * 32767).astype(np.int16)
    
    file_path = VOICE_RAW_DIR / f"audio_{i:03d}.wav"
    wavfile.write(file_path, sr, audio_int16)
    print(f"Created synthetic voice file: {file_path}")
