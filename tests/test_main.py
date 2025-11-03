"""Tests for main.py CLI entry point."""

import subprocess
import sys
from pathlib import Path


class TestMainCLI:
    """Test the main.py CLI entry point."""

    def test_main_help_shows_description(self):
        """Test that main.py --help shows the CLI description."""
        result = subprocess.run(
            [sys.executable, "main.py", "--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        assert result.returncode == 0
        assert "RAG system for Alteryx help documentation" in result.stdout
        assert "sitemap-filter" in result.stdout

    def test_main_version_flag(self):
        """Test that main.py --version shows the version."""
        result = subprocess.run(
            [sys.executable, "main.py", "--version"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        assert result.returncode == 0
        assert "0.1.0" in result.stdout

    def test_main_no_args_shows_help(self):
        """Test that main.py with no arguments shows help with available commands."""
        result = subprocess.run(
            [sys.executable, "main.py"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Typer exits with code 2 when no command provided but no_args_is_help=True
        assert result.returncode == 2
        assert "Commands" in result.stdout
        assert "sitemap-filter" in result.stdout

    def test_main_sitemap_filter_command_exists(self):
        """Test that sitemap-filter command is registered."""
        result = subprocess.run(
            [sys.executable, "main.py", "--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        assert result.returncode == 0
        assert "sitemap-filter" in result.stdout
        assert "Filter Alteryx sitemap URLs by language and product" in result.stdout

    def test_main_sitemap_filter_requires_file_argument(self):
        """Test that sitemap-filter command requires sitemap file argument."""
        result = subprocess.run(
            [sys.executable, "main.py", "sitemap-filter"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Should show error about missing argument
        assert result.returncode != 0
        assert "SITEMAP_FILE" in result.stderr or "Missing argument" in result.stderr

    def test_main_sitemap_filter_with_valid_file(self):
        """Test that sitemap-filter command works with valid sitemap file."""
        sitemap_path = (
            Path(__file__).parent.parent
            / "packages"
            / "sitemap-filter"
            / "tests"
            / "fixtures"
            / "sample_sitemap.xml"
        )

        result = subprocess.run(
            [sys.executable, "main.py", "sitemap-filter", str(sitemap_path), "--dry-run"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        assert result.returncode == 0
        # Should see logging output in stderr
        assert "Total URLs" in result.stderr or "Filtered URLs" in result.stderr

    def test_main_sitemap_filter_with_nonexistent_file(self):
        """Test that sitemap-filter command fails gracefully with nonexistent file."""
        result = subprocess.run(
            [sys.executable, "main.py", "sitemap-filter", "nonexistent.xml"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        assert result.returncode != 0
        # Should show error about file not existing
        assert "does not exist" in result.stderr or "does not exist" in result.stdout

    def test_main_sitemap_filter_language_option(self):
        """Test that sitemap-filter command accepts --language option."""
        sitemap_path = (
            Path(__file__).parent.parent
            / "packages"
            / "sitemap-filter"
            / "tests"
            / "fixtures"
            / "sample_sitemap.xml"
        )

        result = subprocess.run(
            [
                sys.executable,
                "main.py",
                "sitemap-filter",
                str(sitemap_path),
                "--language",
                "de",
                "--dry-run",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        assert result.returncode == 0
        assert "Language: de" in result.stderr or "de" in result.stderr

    def test_main_sitemap_filter_product_option(self):
        """Test that sitemap-filter command accepts --product option."""
        sitemap_path = (
            Path(__file__).parent.parent
            / "packages"
            / "sitemap-filter"
            / "tests"
            / "fixtures"
            / "sample_sitemap.xml"
        )

        result = subprocess.run(
            [
                sys.executable,
                "main.py",
                "sitemap-filter",
                str(sitemap_path),
                "--product",
                "designer",
                "--dry-run",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        assert result.returncode == 0
        assert "designer" in result.stderr.lower()

    def test_main_sitemap_filter_format_option(self):
        """Test that sitemap-filter command accepts --format option."""
        sitemap_path = (
            Path(__file__).parent.parent
            / "packages"
            / "sitemap-filter"
            / "tests"
            / "fixtures"
            / "sample_sitemap.xml"
        )

        result = subprocess.run(
            [
                sys.executable,
                "main.py",
                "sitemap-filter",
                str(sitemap_path),
                "--format",
                "json",
                "--dry-run",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        assert result.returncode == 0

    def test_main_delegates_to_sitemap_filter_module(self):
        """Test that main.py delegates to the sitemap_filter.cli module."""
        sitemap_path = (
            Path(__file__).parent.parent
            / "packages"
            / "sitemap-filter"
            / "tests"
            / "fixtures"
            / "sample_sitemap.xml"
        )

        result = subprocess.run(
            [sys.executable, "main.py", "sitemap-filter", str(sitemap_path), "--dry-run"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Should see sitemap_filter module logging output
        assert result.returncode == 0
        assert "sitemap_filter" in result.stderr or "Processing sitemap" in result.stderr
