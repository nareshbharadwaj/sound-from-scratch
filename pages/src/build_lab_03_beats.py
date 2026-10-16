"""Build pages/lab-03-beats.html: spectrograms of two close tones, computed with sfs.stft.

Run from the repo root: python pages/src/build_lab_03_beats.py
"""
import json
import sys
from pathlib import Path

import numpy as np

here = Path(__file__).resolve().parent
repo = here.parents[1]
sys.path.insert(0, str(repo / "src"))
from sfs.signals import sine  # noqa: E402
from sfs.stft import stft  # noqa: E402

SR, DUR = 8000, 1.0
F_LO, F_HI = 850, 1170                      # bins kept around the 900-1120 Hz view
x = sine(1000, DUR, SR, 0.4) + sine(1020, DUR, SR, 0.4)

specs, figures = [], []
for i, (n_fft, hop) in enumerate([(32, 8), (256, 32), (2048, 256)]):
    S = np.abs(stft(x, n_fft, hop))
    bin_hz = SR / n_fft
    k0 = max(0, int(np.floor(F_LO / bin_hz)))
    k1 = int(np.ceil(F_HI / bin_hz))
    S = S[k0 : k1 + 1] / S.max()
    specs.append(dict(f0=k0 * bin_hz, binHz=bin_hz, hop=hop / SR, duration=DUR,
                      mag=np.round(S, 3).tolist()))
    ms = n_fft * 1000 // SR
    spacing = f"{bin_hz:.0f}" if bin_hz >= 10 else f"{bin_hz:.1f}"
    figures.append(f'<p class="sublabel">{ms} ms frames · bins {spacing} Hz apart</p>\n'
                   f'        <canvas id="c-spec{i}" aria-label="Spectrogram with {ms} millisecond frames"></canvas>')

page = (here / "lab-03-beats.template.html").read_text()
page = page.replace("/*SPEC_DATA*/", json.dumps(specs, separators=(",", ":")))
page = page.replace("<!--SPEC_FIGURES-->", "\n        ".join(figures))
(repo / "pages/lab-03-beats.html").write_text(page)
print(f"wrote pages/lab-03-beats.html ({len(page) // 1024} KB)")
