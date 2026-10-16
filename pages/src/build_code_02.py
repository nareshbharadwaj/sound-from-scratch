"""Build pages/code-02-fourier.html from its template and the real source file.

Run from the repo root after changing src/sfs/fourier.py:
    python pages/src/build_code_02.py
It re-runs the timings, so their numbers change a little each build.
"""
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from codepage import REPO, build  # noqa: E402

sys.path.insert(0, str(REPO / "src"))
from sfs.fourier import dft, fft  # noqa: E402


def ms(f, x, reps):
    f(x)
    t = time.perf_counter()
    for _ in range(reps):
        f(x)
    return (time.perf_counter() - t) / reps * 1000


def fmt(v):
    return f"{v:,.0f} ms" if v >= 10 else f"{v:.1f} ms" if v >= 0.1 else f"{v * 1000:.0f} µs"


rows = []
rng = np.random.default_rng(1)
for N in (256, 1024, 4096):
    x = rng.standard_normal(N)
    d = ms(dft, x, 2 if N == 4096 else 5)
    f = ms(fft, x, 5)
    n = ms(np.fft.fft, x, 2000)
    rows.append(f"            <tr><td>{N:,}</td><td>{fmt(d)}</td><td>{fmt(f)}</td><td>{fmt(n)}</td></tr>")

build("code-02-fourier.template.html", "code-02-fourier.html", "src/sfs/fourier.py",
      {"<!--TIMINGS-->": "\n".join(rows)})
print("\n".join(rows))
