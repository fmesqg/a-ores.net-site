import os
from unittest.mock import MagicMock, patch

from bot.summarize import (
    _build_daily_markdown,
    _strip_frontmatter,
    post_to_telegram,
    summarize,
    summarize_and_post,
)


class TestStripFrontmatter:
    def test_removes_frontmatter(self):
        text = "---\ndate: 2026-03-13\ntitle: X\n---\n## JORAA\ncontent"
        assert _strip_frontmatter(text) == "## JORAA\ncontent"

    def test_no_frontmatter(self):
        text = "## JORAA\ncontent"
        assert _strip_frontmatter(text) == text


class TestBuildDailyMarkdown:
    def test_reads_and_concatenates(self, tmp_path):
        from datetime import date

        d = date(2026, 3, 13)
        (tmp_path / "bot").mkdir()
        docs = tmp_path / "docs"
        for folder in [
            "_alra_updates",
            "_joraa_updates",
            "_base_updates",
            "_portal_updates",
        ]:
            (docs / folder).mkdir(parents=True)

        (docs / "_joraa_updates" / "2026-03-13.md").write_text(
            "---\ndate: 2026-03-13\ntitle: T\n---\n## JORAA\nentry1",
            encoding="utf-8",
        )
        (docs / "_base_updates" / "2026-03-13.md").write_text(
            "---\ndate: 2026-03-13\ntitle: T\n---\n## BASE\nentry2",
            encoding="utf-8",
        )

        with patch(
            "bot.summarize.os.path.dirname",
            return_value=str(tmp_path / "bot"),
        ):
            result = _build_daily_markdown(d)

        assert "## JORAA" in result
        assert "## BASE" in result
        assert "entry1" in result
        assert "entry2" in result

    def test_empty_when_no_files(self, tmp_path):
        from datetime import date

        d = date(2026, 3, 13)
        with patch(
            "bot.summarize.os.path.dirname",
            return_value=str(tmp_path / "bot"),
        ):
            result = _build_daily_markdown(d)
        assert result == ""


class TestSummarize:
    def test_returns_text(self):
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="- Resumo aqui")]

        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            with patch(
                "bot.summarize.anthropic.Anthropic",
                return_value=mock_client,
            ):
                result = summarize("## JORAA\nsome content")

        assert result == "- Resumo aqui"
        call_kwargs = mock_client.messages.create.call_args.kwargs
        assert call_kwargs["model"] == "claude-haiku-4-5-20251001"
        assert "JORAA" in call_kwargs["messages"][0]["content"]

    def test_custom_model(self):
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="ok")]
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response

        with patch.dict(
            os.environ,
            {
                "ANTHROPIC_API_KEY": "k",
                "ANTHROPIC_MODEL": "claude-sonnet-4-5-20250514",
            },
        ):
            with patch(
                "bot.summarize.anthropic.Anthropic",
                return_value=mock_client,
            ):
                summarize("content")

        assert (
            mock_client.messages.create.call_args.kwargs["model"]
            == "claude-sonnet-4-5-20250514"
        )

    def test_api_failure_returns_none(self):
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = RuntimeError("API down")

        with patch(
            "bot.summarize.anthropic.Anthropic",
            return_value=mock_client,
        ):
            result = summarize("content")

        assert result is None


class TestPostToTelegram:
    def test_success(self):
        mock_resp = MagicMock(ok=True)
        with patch.dict(
            os.environ,
            {"TELEGRAM_BOT_TOKEN": "tok", "TELEGRAM_CHAT_ID": "123"},
        ):
            with patch(
                "bot.summarize.requests.post", return_value=mock_resp
            ) as mock_post:
                assert post_to_telegram("hello") is True

        call_kwargs = mock_post.call_args
        assert "tok" in call_kwargs.args[0]
        assert call_kwargs.kwargs["json"]["chat_id"] == "123"
        assert call_kwargs.kwargs["json"]["text"] == "hello"

    def test_failure_returns_false(self):
        mock_resp = MagicMock(ok=False, status_code=400, text="Bad Request")
        with patch.dict(
            os.environ,
            {"TELEGRAM_BOT_TOKEN": "tok", "TELEGRAM_CHAT_ID": "123"},
        ):
            with patch("bot.summarize.requests.post", return_value=mock_resp):
                assert post_to_telegram("hello") is False

    def test_missing_creds_returns_false(self):
        with patch.dict(os.environ, {}, clear=True):
            assert post_to_telegram("hello") is False


class TestSummarizeAndPost:
    def test_skips_when_no_keys(self):
        with patch.dict(os.environ, {}, clear=True):
            summarize_and_post()  # should not raise

    def test_skips_when_empty_markdown(self):
        with patch.dict(
            os.environ,
            {"ANTHROPIC_API_KEY": "k", "TELEGRAM_BOT_TOKEN": "t"},
        ):
            with patch("bot.summarize._build_daily_markdown", return_value=""):
                summarize_and_post()  # no LLM call

    def test_end_to_end(self):
        with patch.dict(
            os.environ,
            {
                "ANTHROPIC_API_KEY": "k",
                "TELEGRAM_BOT_TOKEN": "t",
                "TELEGRAM_CHAT_ID": "c",
            },
        ):
            with (
                patch(
                    "bot.summarize._build_daily_markdown",
                    return_value="## JORAA\ncontent",
                ) as mock_build,
                patch(
                    "bot.summarize.summarize",
                    return_value="- Resumo",
                ) as mock_sum,
                patch(
                    "bot.summarize.post_to_telegram",
                    return_value=True,
                ) as mock_post,
            ):
                summarize_and_post()

        mock_build.assert_called_once()
        mock_sum.assert_called_once_with("## JORAA\ncontent")
        mock_post.assert_called_once_with("- Resumo")

    def test_llm_failure_does_not_post(self):
        with patch.dict(
            os.environ,
            {
                "ANTHROPIC_API_KEY": "k",
                "TELEGRAM_BOT_TOKEN": "t",
                "TELEGRAM_CHAT_ID": "c",
            },
        ):
            with (
                patch(
                    "bot.summarize._build_daily_markdown",
                    return_value="content",
                ),
                patch(
                    "bot.summarize.summarize",
                    return_value=None,
                ),
                patch(
                    "bot.summarize.post_to_telegram",
                ) as mock_post,
            ):
                summarize_and_post()

        mock_post.assert_not_called()
