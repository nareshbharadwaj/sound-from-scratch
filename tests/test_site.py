"""The GitHub Pages site builds, and every link inside it leads somewhere."""
import re
import sys
from pathlib import Path

import pytest

pytest.importorskip("markdown")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "site"))
import build  # noqa: E402


@pytest.fixture(scope="module")
def site(tmp_path_factory):
    return build.build(tmp_path_factory.mktemp("site") / "_site")


def test_every_lesson_has_its_pages(site):
    for les in build.LESSONS:
        for file in (les["page"], les["code"], les["lab"], build.notes_file(les)):
            if file:
                assert (site / file).exists(), file
    assert (site / "index.html").exists()
    assert (site / "notes/log.html").exists()


def test_every_page_has_navigation_and_no_artifact_links(site):
    for page in site.rglob("*.html"):
        text = page.read_text()
        assert text.startswith("<!doctype html>"), page
        assert 'class="sfsnav"' in text, page
        assert "claude.ai/artifact/" not in text, page


def test_every_internal_link_resolves(site):
    for page in site.rglob("*.html"):
        for href in re.findall(r'href="([^"#]+)', page.read_text()):
            if href.startswith(("http://", "https://", "mailto:", "data:")):
                continue
            assert (page.parent / href).resolve().exists(), f"{page.name} -> {href}"
