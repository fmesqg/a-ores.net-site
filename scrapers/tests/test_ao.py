import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

import pytest

from scrapers.ao import (
    _clean,
    _rss_pubdate,
    _xml_safe,
    update_rss_feed,
)


# --- _clean ---

def test_clean_normalizes_whitespace():
    assert _clean("foo  bar\t baz") == "foo bar baz"


def test_clean_removes_nbsp():
    assert _clean("foo\xa0bar") == "foo bar"


# --- _xml_safe ---

def test_xml_safe_removes_control_chars():
    assert _xml_safe("hello\x07world") == "helloworld"
    assert _xml_safe("foo\x00bar") == "foobar"
    assert _xml_safe("a\x1fb") == "ab"


def test_xml_safe_keeps_valid_chars():
    text = "Açores: económico & \"cultural\"\nLinha 2"
    assert _xml_safe(text) == text


def test_xml_safe_keeps_tab_and_newline():
    # \x09 (tab) and \x0a (newline) are valid XML
    assert _xml_safe("a\tb\nc") == "a\tb\nc"


# --- _rss_pubdate ---

def test_rss_pubdate_format():
    result = _rss_pubdate("2026-03-14")
    assert result == "Sat, 14 Mar 2026 00:00:00 +0000"


def test_rss_pubdate_another_day():
    result = _rss_pubdate("2026-03-05")
    assert result == "Thu, 05 Mar 2026 00:00:00 +0000"


# --- update_rss_feed ---

def _make_article(artigo_id, section="politica", title="Título", body="Corpo do artigo."):
    return {
        "id": artigo_id,
        "title": title,
        "section": section,
        "excerpt": "Resumo.",
        "author": "Autor",
        "body": body,
        "url": f"https://www.acorianooriental.pt/pagina/edicao-impressa/2026-03-14?seccao={section}&artigo={artigo_id}",
        "page": "1",
    }


def _parse_feed(path: Path):
    tree = ET.parse(path)
    channel = tree.getroot().find("channel")
    return channel.findall("item")


def test_update_rss_feed_creates_file():
    articles = [_make_article("100"), _make_article("101")]
    with tempfile.TemporaryDirectory() as tmpdir:
        feed_path = Path(tmpdir) / "ao.xml"
        with patch("scrapers.ao.RSS_FEED_PATH", feed_path):
            added = update_rss_feed(articles, "2026-03-14")
        assert added == 2
        assert feed_path.exists()
        items = _parse_feed(feed_path)
        assert len(items) == 2


def test_update_rss_feed_item_fields():
    article = _make_article("200", section="cultura", title="Arte Nova", body="Texto completo.")
    with tempfile.TemporaryDirectory() as tmpdir:
        feed_path = Path(tmpdir) / "ao.xml"
        with patch("scrapers.ao.RSS_FEED_PATH", feed_path):
            update_rss_feed([article], "2026-03-14")
        items = _parse_feed(feed_path)
        item = items[0]
        assert item.find("title").text == "Arte Nova"
        assert item.find("category").text == "cultura"
        assert item.find("description").text == "Texto completo."
        assert item.find("author").text == "Autor"
        assert item.find("pubDate").text == "Sat, 14 Mar 2026 00:00:00 +0000"
        assert "artigo=200" in item.find("guid").text
        assert item.find("guid").get("isPermaLink") == "false"
        assert item.find("link") is None


def test_update_rss_feed_deduplicates():
    articles = [_make_article("300")]
    with tempfile.TemporaryDirectory() as tmpdir:
        feed_path = Path(tmpdir) / "ao.xml"
        with patch("scrapers.ao.RSS_FEED_PATH", feed_path):
            first = update_rss_feed(articles, "2026-03-14")
            second = update_rss_feed(articles, "2026-03-14")
        assert first == 1
        assert second == 0
        assert len(_parse_feed(feed_path)) == 1


def test_update_rss_feed_appends_across_dates():
    day1 = [_make_article("400")]
    day2 = [_make_article("401")]
    with tempfile.TemporaryDirectory() as tmpdir:
        feed_path = Path(tmpdir) / "ao.xml"
        with patch("scrapers.ao.RSS_FEED_PATH", feed_path):
            update_rss_feed(day1, "2026-03-05")
            added = update_rss_feed(day2, "2026-03-14")
        assert added == 1
        items = _parse_feed(feed_path)
        assert len(items) == 2
        guids = {i.find("guid").text for i in items}
        assert any("artigo=400" in g for g in guids)
        assert any("artigo=401" in g for g in guids)


def test_update_rss_feed_newest_first():
    day1 = [_make_article("500")]
    day2 = [_make_article("501")]
    with tempfile.TemporaryDirectory() as tmpdir:
        feed_path = Path(tmpdir) / "ao.xml"
        with patch("scrapers.ao.RSS_FEED_PATH", feed_path):
            update_rss_feed(day1, "2026-03-05")
            update_rss_feed(day2, "2026-03-14")
        items = _parse_feed(feed_path)
        # Newer article (501) should appear first
        assert "artigo=501" in items[0].find("guid").text


def test_update_rss_feed_falls_back_to_excerpt():
    article = _make_article("600", body="")
    article["excerpt"] = "Só o resumo."
    with tempfile.TemporaryDirectory() as tmpdir:
        feed_path = Path(tmpdir) / "ao.xml"
        with patch("scrapers.ao.RSS_FEED_PATH", feed_path):
            update_rss_feed([article], "2026-03-14")
        item = _parse_feed(feed_path)[0]
        assert item.find("description").text == "Só o resumo."


def test_update_rss_feed_strips_control_chars():
    article = _make_article("700", body="texto\x07com bell")
    with tempfile.TemporaryDirectory() as tmpdir:
        feed_path = Path(tmpdir) / "ao.xml"
        with patch("scrapers.ao.RSS_FEED_PATH", feed_path):
            update_rss_feed([article], "2026-03-14")
        # File must parse without error and content must be clean
        items = _parse_feed(feed_path)
        assert items[0].find("description").text == "textocom bell"


def test_update_rss_feed_skips_articles_without_url():
    article = _make_article("800")
    article["url"] = ""
    with tempfile.TemporaryDirectory() as tmpdir:
        feed_path = Path(tmpdir) / "ao.xml"
        with patch("scrapers.ao.RSS_FEED_PATH", feed_path):
            added = update_rss_feed([article], "2026-03-14")
        assert added == 0
        assert len(_parse_feed(feed_path)) == 0
