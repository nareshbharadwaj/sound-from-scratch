"""Shared pieces for the code walkthrough pages (pages/code-*.html).

`render(source, name)` turns one function from a source file into wrapped,
line-numbered HTML, leaving out its docstring. `build(template, out, source)`
fills a template's <!--STYLE--> and <!--CODE:name--> markers.
"""
import ast
import html
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
KW = r"\b(def|return|if|or|is|None|import|as|for|in|else)\b"


def render(source, name):
    src = Path(source).read_text()
    tree, lines = ast.parse(src), src.splitlines()
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
        code, hash_, comment = text.partition("#")
        hl = re.sub(KW, r'<span class="kw">\1</span>', code)
        hl = re.sub(r"(?<=def </span>)(\w+)", r'<span class="fn">\1</span>', hl)
        if hash_:
            hl += f'<span class="cm">#{comment}</span>'
        cls = "ln blank" if not l.strip() else "ln"
        out.append(f'<span class="{cls}" style="--i:{indent}">{hl}</span>')
    return '  <div class="code">' + "".join(out) + "</div>"


def build(template, out, source, extra=None):
    page = (HERE / template).read_text()
    page = page.replace("<!--STYLE-->", (HERE / "code-page.css").read_text())
    page = re.sub(r"<!--CODE:(\w+)-->", lambda m: render(REPO / source, m.group(1)), page)
    for marker, value in (extra or {}).items():
        assert page.count(marker) == 1, marker
        page = page.replace(marker, value)
    (REPO / "pages" / out).write_text(page)
    print(f"wrote pages/{out}")
