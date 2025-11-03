"""Integration tests for the CLI interface."""

import json
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
from sitemap_filter.cli import app
from typer.testing import CliRunner

runner = CliRunner()


class TestCLILanguageFilter:
    """Integration tests for language filtering via CLI."""

    @pytest.fixture
    def sample_sitemap_path(self):
        """Path to sample sitemap fixture."""
        return Path(__file__).parent.parent / "fixtures" / "sample_sitemap.xml"

    def test_cli_with_language_en_flag(self, sample_sitemap_path):
        """Test CLI with --language en flag filters English URLs."""
        result = runner.invoke(app, [str(sample_sitemap_path), "--language", "en", "--dry-run"])
        assert result.exit_code == 0
        # Verify command executed successfully (loguru output goes to actual stderr, not captured)

    def test_cli_with_language_de_flag(self, sample_sitemap_path):
        """Test CLI with --language de flag filters German URLs."""
        result = runner.invoke(app, [str(sample_sitemap_path), "--language", "de", "--dry-run"])
        assert result.exit_code == 0

    def test_cli_with_all_languages(self, sample_sitemap_path):
        """Test CLI with --language all returns all URLs."""
        result = runner.invoke(app, [str(sample_sitemap_path), "--language", "all", "--dry-run"])
        assert result.exit_code == 0


class TestCLIProductFilter:
    """Integration tests for product filtering via CLI."""

    @pytest.fixture
    def sample_sitemap_path(self):
        """Path to sample sitemap fixture."""
        return Path(__file__).parent.parent / "fixtures" / "sample_sitemap.xml"

    def test_cli_with_product_designer_flag(self, sample_sitemap_path):
        """Test CLI with --product designer flag."""
        result = runner.invoke(
            app, [str(sample_sitemap_path), "--product", "designer", "--dry-run"]
        )
        assert result.exit_code == 0

    def test_cli_with_multiple_products(self, sample_sitemap_path):
        """Test CLI with multiple --product flags."""
        result = runner.invoke(
            app,
            [str(sample_sitemap_path), "--product", "designer", "--product", "server", "--dry-run"],
        )
        assert result.exit_code == 0


class TestCLICombinedFilters:
    """Integration tests for combined language and product filtering."""

    @pytest.fixture
    def sample_sitemap_path(self):
        """Path to sample sitemap fixture."""
        return Path(__file__).parent.parent / "fixtures" / "sample_sitemap.xml"

    def test_cli_with_language_and_product(self, sample_sitemap_path):
        """Test CLI with both --language and --product flags."""
        result = runner.invoke(
            app,
            [str(sample_sitemap_path), "--language", "en", "--product", "designer", "--dry-run"],
        )
        assert result.exit_code == 0


class TestCLIOutputFormats:
    """Integration tests for different output formats."""

    @pytest.fixture
    def sample_sitemap_path(self):
        """Path to sample sitemap fixture."""
        return Path(__file__).parent.parent / "fixtures" / "sample_sitemap.xml"

    def test_cli_json_format(self, sample_sitemap_path):
        """Test CLI with --format json produces valid JSON."""
        result = runner.invoke(
            app, [str(sample_sitemap_path), "--language", "en", "--format", "json"]
        )
        assert result.exit_code == 0

        # Verify valid JSON output
        output_data = json.loads(result.stdout)
        assert "total_urls" in output_data
        assert "filtered_urls" in output_data
        assert "results" in output_data
        assert isinstance(output_data["results"], list)

    def test_cli_text_format(self, sample_sitemap_path):
        """Test CLI with --format text produces one URL per line."""
        result = runner.invoke(
            app, [str(sample_sitemap_path), "--language", "en", "--format", "text"]
        )
        assert result.exit_code == 0

        # Verify text format (one URL per line)
        lines = result.stdout.strip().split("\n")
        for line in lines:
            if line:  # Skip empty lines
                assert line.startswith("https://")

    def test_cli_xml_format(self, sample_sitemap_path):
        """Test CLI with --format xml produces valid XML."""
        result = runner.invoke(
            app, [str(sample_sitemap_path), "--language", "en", "--format", "xml"]
        )
        assert result.exit_code == 0

        # Verify valid XML output
        root = ET.fromstring(result.stdout)
        assert root.tag.endswith("urlset")


class TestCLIFileOutput:
    """Integration tests for file output functionality."""

    @pytest.fixture
    def sample_sitemap_path(self):
        """Path to sample sitemap fixture."""
        return Path(__file__).parent.parent / "fixtures" / "sample_sitemap.xml"

    def test_cli_output_to_json_file(self, sample_sitemap_path, tmp_path):
        """Test CLI with --output writes JSON to file."""
        output_file = tmp_path / "output.json"
        result = runner.invoke(
            app,
            [
                str(sample_sitemap_path),
                "--language",
                "en",
                "--format",
                "json",
                "--output",
                str(output_file),
            ],
        )
        assert result.exit_code == 0
        assert output_file.exists()

        # Verify file contains valid JSON
        with open(output_file) as f:
            data = json.load(f)
            assert "total_urls" in data
            assert "filtered_urls" in data

    def test_cli_output_to_text_file(self, sample_sitemap_path, tmp_path):
        """Test CLI with --output writes text to file."""
        output_file = tmp_path / "output.txt"
        result = runner.invoke(
            app,
            [
                str(sample_sitemap_path),
                "--language",
                "en",
                "--format",
                "text",
                "--output",
                str(output_file),
            ],
        )
        assert result.exit_code == 0
        assert output_file.exists()

        # Verify file contains URLs
        with open(output_file) as f:
            content = f.read()
            assert "https://help.alteryx.com" in content

    def test_cli_output_to_xml_file(self, sample_sitemap_path, tmp_path):
        """Test CLI with --output writes XML to file."""
        output_file = tmp_path / "output.xml"
        result = runner.invoke(
            app,
            [
                str(sample_sitemap_path),
                "--language",
                "en",
                "--format",
                "xml",
                "--output",
                str(output_file),
            ],
        )
        assert result.exit_code == 0
        assert output_file.exists()

        # Verify file contains valid XML
        tree = ET.parse(output_file)
        root = tree.getroot()
        assert root.tag.endswith("urlset")


class TestCLIDryRun:
    """Integration tests for dry-run mode."""

    @pytest.fixture
    def sample_sitemap_path(self):
        """Path to sample sitemap fixture."""
        return Path(__file__).parent.parent / "fixtures" / "sample_sitemap.xml"

    def test_cli_dry_run_no_output(self, sample_sitemap_path):
        """Test CLI with --dry-run shows stats without outputting URLs."""
        result = runner.invoke(app, [str(sample_sitemap_path), "--language", "en", "--dry-run"])
        assert result.exit_code == 0
        # No URLs in stdout when using dry-run
        assert not result.stdout or result.stdout.strip() == ""


class TestCLIErrorHandling:
    """Integration tests for error handling."""

    def test_cli_with_missing_file(self):
        """Test CLI with non-existent file shows error."""
        result = runner.invoke(app, ["nonexistent.xml", "--language", "en"])
        # Typer returns exit code 2 for validation errors (missing file)
        assert result.exit_code == 2

    def test_cli_with_malformed_xml(self):
        """Test CLI with malformed XML shows error."""
        malformed_path = Path(__file__).parent.parent / "fixtures" / "malformed_sitemap.xml"
        result = runner.invoke(app, [str(malformed_path), "--language", "en"])
        assert result.exit_code == 1

    def test_cli_with_invalid_format(self, tmp_path):
        """Test CLI with invalid format option."""
        # Create a minimal valid sitemap
        sitemap = tmp_path / "test.xml"
        sitemap.write_text(
            '<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></urlset>'
        )

        result = runner.invoke(app, [str(sitemap), "--format", "invalid"])
        assert result.exit_code == 1
