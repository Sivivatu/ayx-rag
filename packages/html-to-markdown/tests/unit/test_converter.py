"""Unit tests for converter.py."""

from datetime import datetime
from pathlib import Path

import pytest
from html_to_markdown.converter import (
    HtmlConverter,
    convert_html_to_markdown,
    detect_code_language,
)
from html_to_markdown.models import ConversionConfig, ConvertedDocument, SourceDocument


class TestDetectCodeLanguage:
    """Test code language detection from CSS classes."""

    def test_detects_python_from_language_class(self):
        """Should detect Python from language-python class."""
        assert detect_code_language("language-python") == "python"

    def test_detects_javascript_from_lang_class(self):
        """Should detect JavaScript from lang-js class."""
        assert detect_code_language("lang-js") == "javascript"

    def test_detects_bash_from_sh_class(self):
        """Should detect bash from sh class."""
        assert detect_code_language("sh") == "bash"

    def test_returns_none_for_no_class(self):
        """Should return None for missing class."""
        assert detect_code_language("") is None

    def test_returns_none_for_unrecognized_class(self):
        """Should return None for unrecognized class."""
        assert detect_code_language("some-random-class") is None


class TestHtmlConverter:
    """Test HtmlConverter class."""

    @pytest.fixture
    def converter(self):
        """Create converter with default config."""
        config = ConversionConfig()
        return HtmlConverter(config)

    @pytest.fixture
    def html_file(self, tmp_path):
        """Create temporary HTML file."""
        html = """<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
    <meta property="og:url" content="https://example.com/test" />
</head>
<body>
    <h1>Main Title</h1>
    <p>Test content.</p>
</body>
</html>"""
        file_path = tmp_path / "test.html"
        file_path.write_text(html, encoding="utf-8")
        return file_path

    def test_convert_file_creates_converted_document(self, converter, html_file, tmp_path):
        """Should convert HTML file to ConvertedDocument."""
        output_dir = tmp_path / "output"
        result = converter.convert_file(html_file, output_dir)

        assert isinstance(result, ConvertedDocument)
        assert result.source_path == html_file
        assert result.front_matter["title"] == "Main Title"
        assert result.front_matter["original_url"] == "https://example.com/test"
        assert "# Main Title" in result.markdown_content
        assert "Test content" in result.markdown_content

    def test_convert_file_with_front_matter(self, converter, html_file, tmp_path):
        """Should include YAML front matter."""
        output_dir = tmp_path / "output"
        result = converter.convert_file(html_file, output_dir)

        assert result.front_matter is not None
        assert result.front_matter["title"] == "Main Title"
        assert result.front_matter["original_url"] == "https://example.com/test"
        assert "source_path" in result.front_matter
        assert "strategy" in result.front_matter

    def test_extract_title_from_h1(self, converter):
        """Should extract title from H1 tag."""
        html = "<h1>Page Title</h1><p>Content</p>"
        title = converter._extract_title(html)
        assert title == "Page Title"

    def test_extract_title_from_title_tag(self, converter):
        """Should extract title from <title> tag if no H1."""
        html = "<head><title>Page Title</title></head><p>Content</p>"
        title = converter._extract_title(html)
        assert title == "Page Title"

    def test_extract_title_returns_untitled(self, converter):
        """Should return 'Untitled' if no title found."""
        html = "<p>Content without title</p>"
        title = converter._extract_title(html)
        assert title == "Untitled"

    def test_extract_url_from_og_url(self, converter):
        """Should extract URL from og:url meta tag."""
        html = '<meta property="og:url" content="https://example.com/page" />'
        url = converter._extract_original_url(html)
        assert url == "https://example.com/page"

    def test_extract_url_from_canonical_link(self, converter):
        """Should extract URL from canonical link."""
        html = '<link rel="canonical" href="https://example.com/page" />'
        url = converter._extract_original_url(html)
        assert url == "https://example.com/page"

    def test_extract_url_from_html_comment(self, converter):
        """Should extract URL from HTML comment."""
        html = "<!-- Source: https://example.com/page -->"
        url = converter._extract_original_url(html)
        assert url == "https://example.com/page"

    def test_extract_url_returns_none(self, converter):
        """Should return None if no URL found."""
        html = "<p>Content without URL</p>"
        url = converter._extract_original_url(html)
        assert url is None

    def test_generate_front_matter(self, converter):
        """Should generate YAML front matter dictionary."""
        source = SourceDocument(
            path=Path("/test/input.html"),
            size_bytes=1024,
            modified_time=datetime.now(),
            hash="abc123",
            inferred_title="Test Title",
            original_url="https://example.com",
        )
        front_matter = converter._generate_front_matter(source)

        assert front_matter["title"] == "Test Title"
        assert front_matter["original_url"] == "https://example.com"
        assert front_matter["source_path"] == str(source.path)
        assert front_matter["strategy"] == "markdownify"
        assert "converted_at" in front_matter

    def test_combine_front_matter_and_body(self, converter):
        """Should combine YAML front matter with Markdown body."""
        front_matter = {"title": "Test", "url": "https://example.com"}
        body = "# Test\n\nContent"

        result = converter._combine_front_matter_and_body(front_matter, body)

        assert result.startswith("---\n")
        assert "title: Test" in result
        assert "url: https://example.com" in result
        assert result.endswith("---\n\n# Test\n\nContent")


class TestConvertHtmlToMarkdownFunction:
    """Test convenience function."""

    def test_converts_html_file_to_markdown(self, tmp_path):
        """Should convert HTML file to Markdown ConvertedDocument."""
        html = "<h1>Title</h1><p>Content</p>"
        html_file = tmp_path / "test.html"
        html_file.write_text(html, encoding="utf-8")

        result = convert_html_to_markdown(html_file)

        assert isinstance(result, ConvertedDocument)
        assert "# Title" in result.markdown_content
        assert "Content" in result.markdown_content


class TestTableProcessing:
    """Test hybrid table processing."""

    @pytest.fixture
    def converter(self):
        """Create converter with hybrid tables enabled."""
        config = ConversionConfig(hybrid_tables=True)
        return HtmlConverter(config)

    @pytest.fixture
    def converter_no_hybrid(self):
        """Create converter with hybrid tables disabled."""
        config = ConversionConfig(hybrid_tables=False)
        return HtmlConverter(config)

    def test_simple_table_left_for_conversion(self, converter):
        """Should leave simple tables for strategy conversion."""
        html = """
        <table>
            <tr><th>A</th><th>B</th></tr>
            <tr><td>1</td><td>2</td></tr>
        </table>
        """
        result = converter._process_tables(html)
        # Simple table should not be wrapped
        assert '<div class="complex-table">' not in result

    def test_complex_table_with_rowspan_preserved(self, converter):
        """Should preserve complex table with rowspan as HTML."""
        html = """
        <table>
            <tr><th>A</th><th>B</th></tr>
            <tr><td rowspan="2">1</td><td>2</td></tr>
            <tr><td>3</td></tr>
        </table>
        """
        result = converter._process_tables(html)
        # Complex table should be wrapped
        assert '<div class="complex-table">' in result

    def test_complex_table_with_colspan_preserved(self, converter):
        """Should preserve complex table with colspan as HTML."""
        html = """
        <table>
            <tr><th colspan="2">Header</th></tr>
            <tr><td>1</td><td>2</td></tr>
        </table>
        """
        result = converter._process_tables(html)
        # Complex table should be wrapped
        assert '<div class="complex-table">' in result

    def test_hybrid_disabled_leaves_all_tables(self, converter_no_hybrid):
        """Should not process tables when hybrid mode disabled."""
        html = """
        <table>
            <tr><th>A</th><th>B</th></tr>
            <tr><td rowspan="2">1</td><td>2</td></tr>
        </table>
        """
        result = converter_no_hybrid._process_tables(html)
        # Should return original HTML
        assert result == html

    def test_multiple_tables_processed_independently(self, converter):
        """Should process multiple tables independently."""
        html = """
        <table>
            <tr><th>Simple</th></tr>
            <tr><td>1</td></tr>
        </table>
        <p>Text</p>
        <table>
            <tr><th colspan="2">Complex</th></tr>
            <tr><td>1</td><td>2</td></tr>
        </table>
        """
        result = converter._process_tables(html)
        # Only complex table should be wrapped
        assert result.count('<div class="complex-table">') == 1

    def test_no_tables_returns_unchanged(self, converter):
        """Should return unchanged HTML when no tables present."""
        html = "<h1>Title</h1><p>Content</p>"
        result = converter._process_tables(html)
        assert result == html
