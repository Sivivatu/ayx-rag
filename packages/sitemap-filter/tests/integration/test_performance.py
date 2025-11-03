"""Performance tests for sitemap filter CLI."""

import time
from pathlib import Path

import pytest
from sitemap_filter.cli import app
from typer.testing import CliRunner

runner = CliRunner()


class TestPerformance:
    """Performance tests to verify processing speed requirements."""

    @pytest.fixture
    def large_sitemap_path(self):
        """Path to large sitemap fixture with 1200+ URLs."""
        return Path(__file__).parent.parent / "fixtures" / "large_sitemap.xml"

    def test_large_sitemap_processing_speed(self, large_sitemap_path):
        """Test that filtering 1200+ URLs completes in under 3 seconds (T074)."""
        start_time = time.time()

        result = runner.invoke(
            app, [str(large_sitemap_path), "--language", "en", "--product", "designer", "--dry-run"]
        )

        elapsed_time = time.time() - start_time

        assert result.exit_code == 0
        assert elapsed_time < 3.0, (
            f"Processing took {elapsed_time:.3f} seconds, expected < 3.0 seconds"
        )

    def test_json_output_performance(self, large_sitemap_path):
        """Test JSON output formatting performance with large dataset."""
        start_time = time.time()

        result = runner.invoke(
            app, [str(large_sitemap_path), "--language", "en", "--format", "json"]
        )

        elapsed_time = time.time() - start_time

        assert result.exit_code == 0
        assert elapsed_time < 5.0, (
            f"JSON output took {elapsed_time:.3f} seconds, expected < 5.0 seconds"
        )
        assert '"total_urls"' in result.stdout

    def test_text_output_performance(self, large_sitemap_path):
        """Test text output formatting performance with large dataset."""
        start_time = time.time()

        result = runner.invoke(
            app, [str(large_sitemap_path), "--language", "de", "--format", "text"]
        )

        elapsed_time = time.time() - start_time

        assert result.exit_code == 0
        assert elapsed_time < 5.0, (
            f"Text output took {elapsed_time:.3f} seconds, expected < 5.0 seconds"
        )
        assert "https://help.alteryx.com" in result.stdout

    def test_xml_output_performance(self, large_sitemap_path):
        """Test XML output formatting performance with large dataset."""
        start_time = time.time()

        result = runner.invoke(
            app, [str(large_sitemap_path), "--language", "es", "--format", "xml"]
        )

        elapsed_time = time.time() - start_time

        assert result.exit_code == 0
        assert elapsed_time < 5.0, (
            f"XML output took {elapsed_time:.3f} seconds, expected < 5.0 seconds"
        )
        assert "<?xml version" in result.stdout

    def test_multiple_product_filters_performance(self, large_sitemap_path):
        """Test performance with multiple product filters."""
        start_time = time.time()

        result = runner.invoke(
            app,
            [
                str(large_sitemap_path),
                "--language",
                "en",
                "--product",
                "designer",
                "--product",
                "server",
                "--product",
                "connect",
                "--dry-run",
            ],
        )

        elapsed_time = time.time() - start_time

        assert result.exit_code == 0
        assert elapsed_time < 3.0, (
            f"Multi-product filtering took {elapsed_time:.3f} seconds, expected < 3.0 seconds"
        )
