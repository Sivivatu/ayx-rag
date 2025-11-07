"""Unit tests for URLList parsing from text files."""

from pathlib import Path

import pytest

try:
    from page_downloader.models import URLList
except Exception:  # pragma: no cover - will exist after implementation
    URLList = None  # type: ignore


@pytest.fixture()
def fixtures_dir() -> Path:
    # tests/unit -> parent is tests
    return Path(__file__).resolve().parents[1] / "fixtures" / "url_lists"


@pytest.mark.skipif(URLList is None, reason="URLList not implemented yet")
class TestURLListParsing:
    def test_parse_plain_file_returns_all_urls(self, fixtures_dir: Path):
        src = fixtures_dir / "batch.txt"
        url_list = URLList.from_file(src)

        assert url_list.source == src
        assert len(url_list.urls) == 10
        assert url_list.valid_count == 10
        assert url_list.invalid_count == 0
        assert all(u.startswith("http") for u in url_list.urls)

    def test_parse_comments_and_blanks_ignored(self, fixtures_dir: Path):
        src_plain = fixtures_dir / "batch.txt"
        src_comments = fixtures_dir / "batch_with_comments.txt"

        plain = URLList.from_file(src_plain)
        commented = URLList.from_file(src_comments)

        assert len(plain.urls) == 10
        assert len(commented.urls) == 10
        assert set(plain.urls) == set(commented.urls)

    def test_parse_mixed_urls_skips_invalid(self, fixtures_dir: Path):
        src = fixtures_dir / "mixed_urls.txt"
        url_list = URLList.from_file(src)

        # From fixture: 8 valid http(s) URLs, 4 invalid lines. Comments/blank lines ignored.
        assert url_list.valid_count == 8
        assert url_list.invalid_count == 4
        assert len(url_list.urls) == 8
        # Ensure whitespace around URLs is trimmed
        assert any(u.endswith("/whitespace.html") for u in url_list.urls)
        # Ensure malformed entries are excluded
        assert not any(u.startswith("htp://") for u in url_list.urls)
