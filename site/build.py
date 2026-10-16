"""Build the GitHub Pages site from pages/ and notes/.

    python site/build.py            # writes _site/
    python site/build.py --out DIR

Every lesson page, code walkthrough and tool in pages/ is wrapped in a full
HTML document with a navigation bar, and every lesson's notes are rendered
from Markdown. Links to the published artifacts (listed in pages/README.md)
are rewritten to point at the site's own copies, so the site works on its
own. The lesson list below is the only thing to update when a lesson is
added.
"""
import argparse
import html
import re
import shutil
from pathlib import Path

import markdown

REPO = Path(__file__).resolve().parents[1]
SITE_SRC = Path(__file__).resolve().parent

LESSONS = [
    dict(n=1, title="How Sound Becomes Numbers", topic="Sampling and aliasing",
         page="lesson-01-sampling.html", code=None, lab="aliasing-lab.html",
         notes="01-sampling-and-aliasing.md",
         blurb="Where audio's numbers come from, and how a tone too high for the sample rate disguises itself as a lower one."),
    dict(n=2, title="Taking Sound Apart", topic="The Fourier transform",
         page="lesson-02-fourier.html", code="code-02-fourier.html", lab=None,
         notes="02-fourier-transform.md",
         blurb="Splitting a sound into the sine waves it's made of, from the matching trick up to the FFT."),
    dict(n=3, title="Seeing Sound Over Time", topic="Windows, the STFT and spectrograms",
         page="lesson-03-stft.html", code="code-03-stft.html", lab=None,
         notes="03-stft-and-spectrograms.md",
         blurb="Slicing a recording into windowed frames to draw a spectrogram, then reading a real voice in it."),
]

# The artifact skeleton's reset, plus room for the sticky navigation bar.
RESET = """<style>:root{box-sizing:border-box;padding-bottom:env(safe-area-inset-bottom,0px)}
html{scroll-padding-top:110px}body{margin:0;font:14px -apple-system,BlinkMacSystemFont,sans-serif}
img{max-width:100%}[hidden]:not([hidden=until-found i]){display:none!important}</style>"""


def artifact_map():
    """Artifact id -> site file, read from the table in pages/README.md."""
    out = {}
    for line in (REPO / "pages/README.md").read_text().splitlines():
        m = re.match(r"\|\s*`([\w.-]+\.html)`\s*\|\s*https://claude\.ai/artifact/(\w+)", line)
        if m:
            out[m.group(2)] = m.group(1)
    return out


def rewrite_links(text, prefix):
    for art_id, file in artifact_map().items():
        text = text.replace(f"https://claude.ai/artifact/{art_id}", prefix + file)
    return text


def lesson_of(file):
    for les in LESSONS:
        if file in (les["page"], les["code"], les["lab"]) or file == notes_file(les):
            return les
    return None


def notes_file(les):
    return "notes/" + les["notes"].replace(".md", ".html")


def nav(current, prefix):
    """The sticky bar: home link, a lessons menu, and tabs for the current lesson."""
    items = []
    for les in LESSONS:
        links = [f'<a href="{prefix}{les["page"]}">Lesson</a>']
        if les["code"]:
            links.append(f'<a href="{prefix}{les["code"]}">Code</a>')
        if les["lab"]:
            links.append(f'<a href="{prefix}{les["lab"]}">Lab</a>')
        links.append(f'<a href="{prefix}{notes_file(les)}">Notes</a>')
        items.append(f'<li><span class="sfsnav-n">{les["n"]}</span><div><a class="sfsnav-t" href="{prefix}{les["page"]}">'
                     f'{html.escape(les["title"])}</a><span class="sfsnav-sub">{" · ".join(links)}</span></div></li>')
    menu = (f'<details class="sfsnav-menu"><summary>Lessons</summary><div class="sfsnav-pop">'
            f'<ol>{"".join(items)}</ol><a class="sfsnav-log" href="{prefix}notes/log.html">Learning log</a></div></details>')
    tabs = ""
    les = lesson_of(current)
    if les:
        def tab(label, file):
            cur = ' aria-current="page"' if file == current else ""
            return f'<a href="{prefix}{file}"{cur}>{label}</a>'
        parts = [tab("Lesson", les["page"])]
        if les["code"]:
            parts.append(tab("Code", les["code"]))
        if les["lab"]:
            parts.append(tab("Lab", les["lab"]))
        parts.append(tab("Notes", notes_file(les)))
        tabs = f'<div class="sfsnav-tabs"><span class="sfsnav-which">Lesson {les["n"]}</span>{"".join(parts)}</div>'
    return (f'<header class="sfsnav"><div class="sfsnav-in"><div class="sfsnav-bar">'
            f'<a class="sfsnav-home" href="{prefix}index.html">Sound From Scratch</a>{menu}</div>{tabs}</div></header>')


def pager(current, prefix):
    """Previous and next lesson, at the bottom of every lesson's pages."""
    les = lesson_of(current)
    if not les:
        return ""
    i = LESSONS.index(les)
    prev = LESSONS[i - 1] if i > 0 else None
    nxt = LESSONS[i + 1] if i + 1 < len(LESSONS) else None
    left = (f'<a href="{prefix}{prev["page"]}"><span>← Lesson {prev["n"]}</span>{html.escape(prev["title"])}</a>'
            if prev else '<a href="' + prefix + 'index.html"><span>←</span>All lessons</a>')
    right = (f'<a class="sfsnav-next" href="{prefix}{nxt["page"]}"><span>Lesson {nxt["n"]} →</span>{html.escape(nxt["title"])}</a>'
             if nxt else '<a class="sfsnav-next" href="' + prefix + 'index.html"><span>→</span>All lessons</a>')
    return f'<nav class="sfsnav-pager" aria-label="Lessons">{left}{right}</nav>'


def document(head, body, current, prefix):
    nav_css = (SITE_SRC / "nav.css").read_text()
    return ("<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1,viewport-fit=cover\">\n"
            f"{RESET}\n{head}\n<style>{nav_css}</style>\n</head>\n<body>\n{nav(current, prefix)}\n{body}\n"
            f"{pager(current, prefix)}\n</body>\n</html>\n")


def wrap_page(file, out):
    """A page from pages/: everything up to its first </style> is head material."""
    text = rewrite_links((REPO / "pages" / file).read_text(), "")
    cut = text.index("</style>") + len("</style>")
    (out / file).write_text(document(text[:cut], text[cut:], file, ""))


def page_title(file):
    m = re.search(r"<title>(.*?)</title>", (REPO / "pages" / file).read_text())
    return m.group(1) if m else file


def link_bare_urls(md_text):
    """Turn a bare artifact address into a Markdown link named after its page."""
    pages = artifact_map()

    def repl(m):
        file = pages.get(m.group(1))
        return f"[{page_title(file)}]({m.group(0)})" if file else m.group(0)
    return re.sub(r"(?<![(<])https://claude\.ai/artifact/(\w+)", repl, md_text)


def render_markdown(md_text, current, out_path, prefix):
    md_text = rewrite_links(link_bare_urls(md_text), prefix)
    body_html = markdown.markdown(md_text, extensions=["tables", "fenced_code", "sane_lists"])
    m = re.search(r"<h1>(.*?)</h1>", body_html)
    title = re.sub("<[^>]+>", "", m.group(1)) if m else "Sound From Scratch"
    head = (f"<title>{html.escape(title)}</title>\n{(SITE_SRC / 'fonts.html').read_text()}"
            f"<style>{(SITE_SRC / 'prose.css').read_text()}</style>")
    body = f'<main class="prose">\n{body_html}\n</main>'
    out_path.write_text(document(head, body, current, prefix))


def home(out):
    readme = (REPO / "README.md").read_text()
    roadmap = readme.split("## Roadmap", 1)[1].split("\n## ", 1)[0]
    cards = []
    for les in LESSONS:
        links = [f'<a class="btn primary" href="{les["page"]}">Start the lesson</a>']
        if les["code"]:
            links.append(f'<a class="btn" href="{les["code"]}">Code</a>')
        if les["lab"]:
            links.append(f'<a class="btn" href="{les["lab"]}">Lab</a>')
        links.append(f'<a class="btn" href="{notes_file(les)}">Notes</a>')
        cards.append(f'<li class="card"><div class="label">Lesson {les["n"]} · {html.escape(les["topic"])}</div>'
                     f'<h3><a href="{les["page"]}">{html.escape(les["title"])}</a></h3><p>{html.escape(les["blurb"])}</p>'
                     f'<div class="links">{"".join(links)}</div></li>')
    md = markdown.markdown(roadmap, extensions=["tables"])
    body = f"""<main class="prose home">
<div class="label">Phase 1 · Sound as numbers</div>
<h1>Sound From Scratch</h1>
<p class="lede">Learning text-to-speech and music generation from first principles: every idea built up from intuition, every piece implemented from scratch, and every result something you can hear.</p>
<h2>Lessons</h2>
<ol class="cards">{"".join(cards)}</ol>
<p class="aside">Each lesson has an interactive page to work through first, a walkthrough of its code with real outputs, and compact notes with derivations and exercises. <a href="notes/log.html">The learning log</a> records progress.</p>
<h2>Roadmap</h2>
<div class="table-wrap">{md}</div>
</main>"""
    head = (f"<title>Sound From Scratch</title>\n{(SITE_SRC / 'fonts.html').read_text()}"
            f"<style>{(SITE_SRC / 'prose.css').read_text()}</style>")
    (out / "index.html").write_text(document(head, body, "index.html", ""))


def build(out):
    if out.exists():
        shutil.rmtree(out)
    (out / "notes").mkdir(parents=True)
    for les in LESSONS:
        for file in (les["page"], les["code"], les["lab"]):
            if file:
                wrap_page(file, out)
        render_markdown((REPO / "notes/lessons" / les["notes"]).read_text(), notes_file(les),
                        out / notes_file(les), "../")
    render_markdown((REPO / "notes/log.md").read_text(), "notes/log.html", out / "notes/log.html", "../")
    home(out)
    (out / ".nojekyll").write_text("")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(REPO / "_site"))
    out = build(Path(ap.parse_args().out))
    print(f"built {sum(1 for _ in out.rglob('*.html'))} pages in {out}")
