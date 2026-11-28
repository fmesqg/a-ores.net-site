import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

import pytest

from scrapers import ao_pages
from scrapers.ao_pages import (
    _rss_pubdate,
    _xml_safe,
    build_entries,
    build_feed_item,
    build_link_list,
    day_slug,
    section_label,
    write_daily_feed,
    write_day_page,
)

URL = "https://www.acorianooriental.pt/x?seccao="


def _article(title="Título", section="politica", body="Corpo.", **kw):
    article = {
        "id": "100",
        "title": title,
        "section": section,
        "page": "3",
        "excerpt": "Resumo.",
        "author": "Autor",
        "body": body,
        "url": f"{URL}{section}",
    }
    article.update(kw)
    return article


@pytest.fixture
def pages_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "_ao"
        with patch.object(ao_pages, "PAGES_DIR", path):
            yield path


# --- helpers ---


def test_xml_safe_removes_control_chars():
    assert _xml_safe("hello\x07world") == "helloworld"
    assert _xml_safe("foo\x00bar") == "foobar"


def test_xml_safe_keeps_valid_chars():
    text = 'Açores: económico & "cultural"\nLinha 2'
    assert _xml_safe(text) == text


def test_xml_safe_keeps_tab_and_newline():
    assert _xml_safe("a\tb\nc") == "a\tb\nc"


def test_rss_pubdate_format():
    assert _rss_pubdate("2026-03-14") == "Sat, 14 Mar 2026 00:00:00 +0000"
    assert _rss_pubdate("2026-03-05") == "Thu, 05 Mar 2026 00:00:00 +0000"


def test_section_label():
    assert section_label("primeira-hora") == "Primeira Hora"


def test_day_slug():
    assert day_slug("2026-08-25") == "20260825"


# --- build_entries ---


def test_entries_keep_order_and_link_to_the_original():
    sections_data = {
        "primeira-hora": [_article(title="A"), _article(title="B")],
        "sociedade": [_article(title="C")],
    }
    entries = build_entries(sections_data, "2026-08-25")
    # Newspaper section order is preserved
    assert [e["title"] for e in entries] == ["A", "B", "C"]
    assert (
        entries[0]["url"]
        == "https://www.acorianooriental.pt/x?seccao=politica"
    )
    assert "body" not in entries[0]


def test_entries_skip_articles_without_text():
    empty = _article(title="Vazio", body="", excerpt="")
    sections_data = {
        "politica": [_article(title="A"), empty, _article(title="C")]
    }
    entries = build_entries(sections_data, "2026-08-25")
    assert [e["title"] for e in entries] == ["A", "C"]


def test_sections_ordered_by_first_page():
    sections_data = {
        "sociedade": [
            _article(title="S1", page="4"),
            _article(title="S2", page="6"),
        ],
        "primeira-hora": [_article(title="P1", page="2")],
        "9-ilhas": [_article(title="I1", page="28")],
    }
    entries = build_entries(sections_data, "2026-08-25")
    assert [e["title"] for e in entries] == ["P1", "S1", "S2", "I1"]


def test_articles_sorted_by_page_within_section():
    sections_data = {
        "cultura": [
            _article(title="C", page="13"),
            _article(title="A", page="8"),
            _article(title="B", page="11"),
        ]
    }
    entries = build_entries(sections_data, "2026-08-25")
    assert [e["title"] for e in entries] == ["A", "B", "C"]


def test_same_page_keeps_the_papers_order():
    sections_data = {
        "cultura": [
            _article(title="primeiro", page="13"),
            _article(title="segundo", page="13"),
        ]
    }
    entries = build_entries(sections_data, "2026-08-25")
    assert [e["title"] for e in entries] == ["primeiro", "segundo"]


def test_pages_sort_numerically_not_lexically():
    sections_data = {
        "cultura": [
            _article(title="B", page="11"),
            _article(title="A", page="9"),
        ]
    }
    entries = build_entries(sections_data, "2026-08-25")
    assert [e["title"] for e in entries] == ["A", "B"]


def test_articles_without_a_page_sort_last():
    sections_data = {
        "cultura": [
            _article(title="sem pagina", page=""),
            _article(title="com pagina", page="20"),
        ]
    }
    entries = build_entries(sections_data, "2026-08-25")
    assert [e["title"] for e in entries] == ["com pagina", "sem pagina"]


def test_section_without_any_page_sorts_last():
    sections_data = {
        "desconhecida": [_article(title="X", page="")],
        "sociedade": [_article(title="S", page="30")],
    }
    entries = build_entries(sections_data, "2026-08-25")
    assert [e["title"] for e in entries] == ["S", "X"]


def test_entries_skip_front_page_teasers():
    sections_data = {
        "politica": [
            _article(title="Lead", page="0"),
            _article(title="Teaser", page="1"),
            _article(title="Real", page="7"),
        ]
    }
    entries = build_entries(sections_data, "2026-08-25")
    assert [e["title"] for e in entries] == ["Real"]


def test_entries_keep_articles_without_a_page():
    """Backfilled entries have no page number and must survive."""
    sections_data = {"politica": [_article(title="Antigo", page="")]}
    entries = build_entries(sections_data, "2026-08-25")
    assert [e["title"] for e in entries] == ["Antigo"]


def test_entries_keep_page_ten_and_eleven():
    """The filter matches exact page numbers, not prefixes."""
    sections_data = {
        "politica": [
            _article(title="A", page="10"),
            _article(title="B", page="11"),
        ]
    }
    entries = build_entries(sections_data, "2026-08-25")
    assert [e["title"] for e in entries] == ["A", "B"]


def test_entries_fall_back_to_excerpt():
    sections_data = {"politica": [_article(body="", excerpt="Só o resumo.")]}
    entries = build_entries(sections_data, "2026-08-25")
    assert len(entries) == 1


# --- link list ---


def test_link_list_groups_by_section_with_page_and_author():
    sections_data = {
        "sociedade": [_article(title="A", page="6", author="Nuno")],
    }
    html = build_link_list(build_entries(sections_data, "2026-08-25"))
    assert "<h2>Sociedade</h2>" in html
    assert f'<a href="{URL}politica">A (p.6) — Nuno</a>' in html


def test_link_list_omits_missing_page_and_author():
    sections_data = {"sociedade": [_article(title="A", page="", author="")]}
    html = build_link_list(build_entries(sections_data, "2026-08-25"))
    assert f'<a href="{URL}politica">A</a>' in html
    assert "(p.)" not in html
    assert "—" not in html


# --- pages ---


def test_write_day_page(pages_dir):
    sections_data = {"sociedade": [_article(title="A"), _article(title="B")]}
    entries = build_entries(sections_data, "2026-08-25")
    path = write_day_page(entries, "2026-08-25")

    assert path.name == "20260825.md"
    text = path.read_text(encoding="utf-8")
    assert "layout: ao_day" in text
    assert "kind: day" in text
    assert "article_count: 2" in text
    assert "<h2>Sociedade</h2>" in text
    assert f'<a href="{URL}politica">' in text


def test_link_list_without_url_is_plain_text():
    sections_data = {"sociedade": [_article(title="A", url="")]}
    html = build_link_list(build_entries(sections_data, "2026-08-25"))
    assert "<li>A (p.3) — Autor</li>" in html


def test_day_page_neutralises_liquid(pages_dir):
    sections_data = {"politica": [_article(title="{% x %}")]}
    path = write_day_page(
        build_entries(sections_data, "2026-08-25"), "2026-08-25"
    )
    assert "&#123;% x %&#125;" in path.read_text(encoding="utf-8")


def test_day_page_removes_old_article_pages(pages_dir):
    pages_dir.mkdir(parents=True)
    (pages_dir / "20260825-01.md").write_text("texto")
    (pages_dir / "20260824-01.md").write_text("texto")
    write_day_page(_feed_entries("2026-08-25"), "2026-08-25")
    assert not (pages_dir / "20260825-01.md").exists()
    assert (pages_dir / "20260824-01.md").exists()


def test_write_day_page_handles_empty_edition(pages_dir):
    path = write_day_page([], "2026-08-25")
    assert "Sem artigos nesta edição." in path.read_text(encoding="utf-8")


# --- feed ---


def _items(feed_path: Path):
    return ET.parse(feed_path).getroot().find("channel").findall("item")


def _feed_entries(date_str, count=1):
    data = {"politica": [_article(title=f"A{i}") for i in range(count)]}
    return build_entries(data, date_str)


def test_feed_has_one_item_per_day(tmp_path):
    feed = tmp_path / "ao.xml"
    write_daily_feed(_feed_entries("2026-08-24", 3), "2026-08-24", feed)
    total = write_daily_feed(
        _feed_entries("2026-08-25", 2), "2026-08-25", feed
    )

    assert total == 2
    items = _items(feed)
    assert len(items) == 2
    assert items[0].findtext("guid") == "ao-2026-08-25"
    assert items[1].findtext("guid") == "ao-2026-08-24"


def test_feed_item_fields(tmp_path):
    feed = tmp_path / "ao.xml"
    write_daily_feed(_feed_entries("2026-08-25", 2), "2026-08-25", feed)
    item = _items(feed)[0]

    assert (
        item.findtext("title") == "Açoriano Oriental — 2026-08-25 (2 artigos)"
    )
    assert item.findtext("link") == f"{ao_pages.SITE_BASE}/ao/20260825/"
    assert item.find("guid").get("isPermaLink") == "false"
    assert item.findtext("pubDate") == "Tue, 25 Aug 2026 00:00:00 +0000"
    assert f"{URL}politica" in item.findtext("description")


def test_feed_rerun_replaces_the_day(tmp_path):
    feed = tmp_path / "ao.xml"
    write_daily_feed(_feed_entries("2026-08-25", 5), "2026-08-25", feed)
    write_daily_feed(_feed_entries("2026-08-25", 2), "2026-08-25", feed)

    items = _items(feed)
    assert len(items) == 1
    assert "(2 artigos)" in items[0].findtext("title")


def test_feed_retention_cap(tmp_path):
    feed = tmp_path / "ao.xml"
    with patch.object(ao_pages, "FEED_RETENTION_DAYS", 3):
        for day in range(1, 7):
            date_str = f"2026-08-{day:02d}"
            write_daily_feed(_feed_entries(date_str), date_str, feed)

    items = _items(feed)
    assert len(items) == 3
    assert [i.findtext("guid") for i in items] == [
        "ao-2026-08-06",
        "ao-2026-08-05",
        "ao-2026-08-04",
    ]


def test_feed_strips_control_chars(tmp_path):
    feed = tmp_path / "ao.xml"
    data = {"politica": [_article(title="texto\x07com bell")]}
    write_daily_feed(build_entries(data, "2026-08-25"), "2026-08-25", feed)
    assert "textocom bell" in _items(feed)[0].findtext("description")


def test_feed_channel_metadata(tmp_path):
    feed = tmp_path / "ao.xml"
    write_daily_feed(_feed_entries("2026-08-25"), "2026-08-25", feed)
    channel = ET.parse(feed).getroot().find("channel")
    assert channel.findtext("title") == ao_pages.FEED_TITLE
    assert channel.findtext("link") == ao_pages.FEED_LINK


def test_feed_drops_legacy_per_article_items(tmp_path):
    """The old format's items have article guids, not ao-<date> guids."""
    feed = tmp_path / "ao.xml"
    legacy = ET.Element("item")
    ET.SubElement(legacy, "guid").text = (
        "https://www.acorianooriental.pt/x?artigo=1"
    )
    ao_pages.write_feed([legacy], feed)

    write_daily_feed(_feed_entries("2026-08-25"), "2026-08-25", feed)
    items = _items(feed)
    assert len(items) == 1
    assert items[0].findtext("guid") == "ao-2026-08-25"


def test_build_feed_item_is_standalone():
    item = build_feed_item(_feed_entries("2026-08-25"), "2026-08-25")
    assert item.tag == "item"
    assert item.findtext("guid") == "ao-2026-08-25"
