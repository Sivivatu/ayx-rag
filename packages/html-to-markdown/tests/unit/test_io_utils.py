"""Unit tests for I/O utilities."""

from pathlib import Path

import pytest
from html_to_markdown.io_utils import (
    compute_hash,
    discover_html_files,
    map_output_path,
    normalize_content,
    read_html,
    write_markdown,
)


class TestDiscoverHtmlFiles:
    """Tests for HTML file discovery."""

    def test_discover_finds_html_files(self, tmp_path: Path):
        """Test discovering HTML files in directory."""
        (tmp_path / "file1.html").write_text("<html></html>")
        (tmp_path / "file2.html").write_text("<html></html>")
        (tmp_path / "file3.txt").write_text("not html")

        files = list(discover_html_files(tmp_path))

        assert len(files) == 2
        assert all(f.suffix == ".html" for f in files)

    def test_discover_recursive(self, tmp_path: Path):
        """Test discovering HTML files recursively."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (tmp_path / "root.html").write_text("<html></html>")
        (subdir / "nested.html").write_text("<html></html>")

        files = list(discover_html_files(tmp_path))

        assert len(files) == 2

    def test_discover_respects_exclusions(self, tmp_path: Path):
        """Test exclusion patterns."""
        excluded = tmp_path / "node_modules"
        excluded.mkdir()
        (tmp_path / "keep.html").write_text("<html></html>")
        (excluded / "exclude.html").write_text("<html></html>")

        files = list(discover_html_files(tmp_path, exclusions=["**/node_modules/**"]))

        assert len(files) == 1
        assert files[0].name == "keep.html"


class TestReadWrite:
    """Tests for read/write operations."""

    def test_read_html(self, tmp_path: Path):
        """Test reading HTML file."""
        html_file = tmp_path / "test.html"
        content = "<html><body>Test</body></html>"
        html_file.write_text(content)

        result = read_html(html_file)

        assert result == content

    def test_read_html_file_not_found(self, tmp_path: Path):
        """Test error when file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            read_html(tmp_path / "missing.html")

    def test_write_markdown(self, tmp_path: Path):
        """Test writing Markdown file."""
        output_file = tmp_path / "output.md"
        content = "# Test\n\nContent"

        write_markdown(output_file, content)

        assert output_file.exists()
        assert output_file.read_text() == content

    def test_write_markdown_creates_dirs(self, tmp_path: Path):
        """Test writing Markdown creates parent directories."""
        output_file = tmp_path / "nested" / "dir" / "output.md"
        content = "# Test"

        write_markdown(output_file, content)

        assert output_file.exists()
        assert output_file.parent.exists()


class TestComputeHash:
    """Tests for hash computation."""

    def test_compute_hash_deterministic(self):
        """Test hash is deterministic."""
        content = "test content"

        hash1 = compute_hash(content)
        hash2 = compute_hash(content)

        assert hash1 == hash2

    def test_compute_hash_different_content(self):
        """Test different content produces different hash."""
        hash1 = compute_hash("content1")
        hash2 = compute_hash("content2")

        assert hash1 != hash2

    def test_compute_hash_format(self):
        """Test hash is hexadecimal SHA-256."""
        result = compute_hash("test")

        assert len(result) == 64  # SHA-256 produces 64 hex characters
        assert all(c in "0123456789abcdef" for c in result)


class TestMapOutputPath:
    """Tests for output path mapping."""

    def test_map_output_path_preserves_structure(self):
        """Test output path preserves directory structure."""
        source = Path("/data/docs/guide/install.html")
        source_dir = Path("/data/docs")
        output_dir = Path("/output")

        result = map_output_path(source, source_dir, output_dir)

        assert result == Path("/output/guide/install.md")

    def test_map_output_path_changes_extension(self):
        """Test output path changes file extension."""
        source = Path("/data/test.html")
        source_dir = Path("/data")
        output_dir = Path("/output")

        result = map_output_path(source, source_dir, output_dir)

        assert result.suffix == ".md"
        assert result.name == "test.md"

    def test_map_output_path_custom_extension(self):
        """Test output path with custom extension."""
        source = Path("/data/test.html")
        source_dir = Path("/data")
        output_dir = Path("/output")

        result = map_output_path(source, source_dir, output_dir, extension=".txt")

        assert result.suffix == ".txt"


class TestNormalizeContent:
    """Tests for content normalization."""

    def test_normalize_strips_trailing_whitespace(self):
        """Test stripping trailing whitespace from lines."""
        content = "line1   \nline2\t\nline3"

        result = normalize_content(content)

        assert result == "line1\nline2\nline3\n"

    def test_normalize_collapses_blank_lines(self):
        """Test collapsing multiple blank lines."""
        content = "line1\n\n\n\nline2\n\nline3"

        result = normalize_content(content)

        assert result == "line1\n\nline2\n\nline3\n"

    def test_normalize_ensures_trailing_newline(self):
        """Test ensuring single trailing newline."""
        content = "line1\nline2"

        result = normalize_content(content)

        assert result.endswith("\n")
        assert not result.endswith("\n\n")

    def test_normalize_empty_string(self):
        """Test normalizing empty string."""
        result = normalize_content("")

        assert result == ""

    def test_normalize_only_whitespace(self):
        """Test normalizing content with only whitespace."""
        content = "   \n\t\n   "

        result = normalize_content(content)

        # Should collapse to empty (all whitespace stripped)
        assert result == ""
