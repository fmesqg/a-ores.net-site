from scrapers.ao import (
    DEFAULT_EXCLUDE,
    _clean,
    build_summary,
    first_sentence,
    load_config,
)

# --- _clean ---


def test_clean_normalizes_whitespace():
    assert _clean("foo  bar\t baz") == "foo bar baz"


def test_clean_removes_nbsp():
    assert _clean("foo\xa0bar") == "foo bar"


# --- first_sentence ---


def test_first_sentence_stops_at_period():
    text = "Uma frase suficientemente longa termina aqui. E segue outra."
    assert (
        first_sentence(text) == "Uma frase suficientemente longa termina aqui."
    )


def test_first_sentence_truncates_when_no_period():
    text = "palavra " * 60
    result = first_sentence(text)
    assert len(result) <= 203
    assert result.endswith("...")


# --- build_summary ---


def test_build_summary_labels_sections_and_lists_articles():
    sections_data = {
        "primeira-hora": [
            {
                "title": "Título",
                "page": "1",
                "author": "Autor",
                "excerpt": "",
                "body": "Corpo do artigo com uma frase completa. Mais.",
            }
        ],
        "vazia": [],
    }
    summary = build_summary("2026-03-14", sections_data)
    assert "## Primeira Hora" in summary
    assert "**Título** (p.1) *Autor*" in summary
    assert "## Vazia" not in summary


# --- load_config ---


def test_no_sections_excluded_by_default():
    """Every section the edition lists is scraped."""
    assert DEFAULT_EXCLUDE == []


def test_config_exclude_is_still_honoured(tmp_path, monkeypatch):
    config = tmp_path / ".ao_config"
    config.write_text(
        "[credentials]\nemail = a@b.c\npassword = x\n"
        "[sections]\nexclude = desporto, opiniao\n"
    )
    monkeypatch.setattr("scrapers.ao.CONFIG_PATH", config)
    _, _, include, exclude = load_config()
    assert include == []
    assert exclude == ["desporto", "opiniao"]


def test_config_without_sections_block_excludes_nothing(tmp_path, monkeypatch):
    config = tmp_path / ".ao_config"
    config.write_text("[credentials]\nemail = a@b.c\npassword = x\n")
    monkeypatch.setattr("scrapers.ao.CONFIG_PATH", config)
    _, _, include, exclude = load_config()
    assert include == []
    assert exclude == []
