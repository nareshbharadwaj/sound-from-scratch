"""Build pages/code-03-stft.html from its template and src/sfs/stft.py.

Run from the repo root: python pages/src/build_code_03.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from codepage import build  # noqa: E402

build("code-03-stft.template.html", "code-03-stft.html", "src/sfs/stft.py")
