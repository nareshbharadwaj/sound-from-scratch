"""Reading and writing WAV files with only the standard library and NumPy.

Convention used everywhere in this repo: a waveform is a 1-D float32 NumPy
array with values in [-1, 1], and its sample rate is always passed explicitly.
"""

import wave
from pathlib import Path

import numpy as np


def write_wav(path, x, sample_rate):
    """Save a mono float waveform as a 16-bit PCM WAV file.

    Values outside [-1, 1] are clipped, which is audible as distortion, so
    normalize first if you are unsure of the range.
    """
    x = np.asarray(x, dtype=np.float64)
    if x.ndim != 1:
        raise ValueError(f"expected a 1-D waveform, got shape {x.shape}")
    pcm = np.round(np.clip(x, -1.0, 1.0) * 32767).astype("<i2")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(int(sample_rate))
        f.writeframes(pcm.tobytes())


def read_wav(path):
    """Load a 16-bit PCM WAV file. Returns (waveform, sample_rate).

    Stereo files are averaged to mono.
    """
    with wave.open(str(path), "rb") as f:
        if f.getsampwidth() != 2:
            raise ValueError("only 16-bit PCM WAV files are supported")
        channels = f.getnchannels()
        sample_rate = f.getframerate()
        pcm = np.frombuffer(f.readframes(f.getnframes()), dtype="<i2")
    x = pcm.astype(np.float32) / 32768.0
    if channels > 1:
        x = x.reshape(-1, channels).mean(axis=1)
    return x, sample_rate
