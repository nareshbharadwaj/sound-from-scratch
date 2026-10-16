"""Build pages/code-02-fourier.html from its template and the real source file.

Run from the repo root after changing src/sfs/fourier.py:
    python pages/src/build_code_02.py
It re-runs the timings, so their numbers change a little each build.
"""
import ast, html, re, sys, time
from pathlib import Path

import numpy as np

repo = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo / "src"))
from sfs.fourier import dft, fft  # noqa: E402

here = Path(__file__).parent
src = (repo / "src/sfs/fourier.py").read_text()
tree = ast.parse(src)
lines = src.splitlines()
KW = r"\b(def|return|if|or|import|as|for|in|else)\b"


def render(name):
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
    body = lines[fn.lineno - 1 : fn.end_lineno]
    doc = fn.body[0]
    if isinstance(doc, ast.Expr) and isinstance(doc.value, ast.Constant):
        cut = set(range(doc.lineno - fn.lineno, doc.end_lineno - fn.lineno + 1))
        body = [l for i, l in enumerate(body) if i not in cut]
    out = []
    for l in body:
        indent = len(l) - len(l.lstrip())
        text = html.escape(l.strip())
        if "#" in text:
            code, _, comment = text.partition("#")
            text = code + f'<span class="cm">#{comment}</span>'
        else:
            code = text
        hl = re.sub(KW, r'<span class="kw">\1</span>', code)
        hl = re.sub(r"(?<=def </span>)(\w+)", r'<span class="fn">\1</span>', hl)
        text = hl + text[len(code):]
        cls = "ln blank" if not l.strip() else "ln"
        out.append(f'<span class="{cls}" style="--i:{indent}">{text}</span>')
    return '  <div class="code">' + "".join(out) + "</div>"


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

page = (here / "code-02-fourier.template.html").read_text()
page = re.sub(r"<!--CODE:(\w+)-->", lambda m: render(m.group(1)), page)
page = page.replace("<!--TIMINGS-->", "\n".join(rows))
(repo / "pages/code-02-fourier.html").write_text(page)
print("\n".join(rows))
