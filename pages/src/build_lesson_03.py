"""Build pages/lesson-03-stft.html: the template plus the voice clip, embedded as base64 PCM.

Run from the repo root: python pages/src/build_lesson_03.py
"""
import base64
import wave
from pathlib import Path

here = Path(__file__).resolve().parent
repo = here.parents[1]

with wave.open(str(here / "assets/libri-198-209-0000-excerpt.wav"), "rb") as f:
    assert f.getframerate() == 16000 and f.getsampwidth() == 2 and f.getnchannels() == 1
    pcm = f.readframes(f.getnframes())          # 16-bit little-endian, as the page expects

page = (here / "lesson-03-stft.template.html").read_text()
assert page.count("/*VOICE_B64*/") == 1
page = page.replace("/*VOICE_B64*/", base64.b64encode(pcm).decode())
(repo / "pages/lesson-03-stft.html").write_text(page)
print(f"wrote pages/lesson-03-stft.html ({len(page) // 1024} KB)")
