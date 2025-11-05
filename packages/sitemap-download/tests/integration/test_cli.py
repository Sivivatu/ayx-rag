"""Integration tests for sitemap-download CLI."""

import subprocess
import sys
from pathlib import Path
from unittest.mock import Mock, patch

from sitemap_download.cli import app
from sitemap_download.models import DownloadResult, ValidationResult
from typer.testing import CliRunner

runner = CliRunner()


class TestCLIBasicDownload:
    """Tests for basic CLI download functionality."""

    def test_cli_help(self):
        """Test that CLI help works."""
        result = subprocess.run(
            [
                sys.executable,
                str(Path(__file__).parent.parent.parent.parent.parent / "main.py"),
                "sitemap-download",
                "--help",
            ],
            capture_output=True,
            text=True,
        )

        # Should succeed and show help
        assert result.returncode == 0, f"CLI help failed: {result.stderr}"
        assert "Download Alteryx sitemap" in result.stdout
        assert "--url" in result.stdout
        assert "--output" in result.stdout
        assert "--force" in result.stdout

    def test_cli_invalid_url(self, tmp_path):
        """Test that CLI rejects invalid URL schemes."""
        output_path = tmp_path / "downloaded.xml"

        result = subprocess.run(
            [
                sys.executable,
                str(Path(__file__).parent.parent.parent.parent.parent / "main.py"),
                "sitemap-download",
                "--url",
                "ftp://example.com/sitemap.xml",
                "--output",
                str(output_path),
            ],
            capture_output=True,
            text=True,
        )

        # Should fail with configuration error
        assert result.returncode == 3, "Should exit with code 3 for configuration error"
        assert "Configuration error" in result.stderr or "Invalid URL scheme" in result.stderr


class TestCLIWithMocks:
    """Tests for CLI with mocked downloader."""

    @patch("sitemap_download.cli.SitemapDownloader")
    def test_successful_download(self, mock_downloader_class, tmp_path):
        """Test successful download flow."""
        output_path = tmp_path / "sitemap.xml"

        # Mock successful download
        mock_downloader = Mock()
        mock_downloader.download.return_value = DownloadResult.success_result(
            file_path=output_path,
            file_size=1000,
            duration=1.0,
            validation_result=ValidationResult.valid_result(
                url_count=100, file_size=1000, duration=0.1
            ),
        )
        mock_downloader_class.return_value = mock_downloader

        result = runner.invoke(
            app, ["--url", "https://example.com/sitemap.xml", "--output", str(output_path)]
        )

        assert result.exit_code == 0

    @patch("sitemap_download.cli.SitemapDownloader")
    def test_download_failure(self, mock_downloader_class, tmp_path):
        """Test download failure flow."""
        output_path = tmp_path / "sitemap.xml"

        # Mock failed download
        mock_downloader = Mock()
        mock_downloader.download.return_value = DownloadResult.failure_result(
            error="Network error",
            duration=1.0,
        )
        mock_downloader_class.return_value = mock_downloader

        result = runner.invoke(
            app, ["--url", "https://example.com/sitemap.xml", "--output", str(output_path)]
        )

        assert result.exit_code == 1

    @patch("sitemap_download.cli.SitemapDownloader")
    def test_validation_failure(self, mock_downloader_class, tmp_path):
        """Test validation failure flow."""
        output_path = tmp_path / "sitemap.xml"

        # Mock download with validation failure
        mock_downloader = Mock()
        mock_downloader.download.return_value = DownloadResult.success_result(
            file_path=output_path,
            file_size=1000,
            duration=1.0,
            validation_result=ValidationResult.invalid_result(
                error="Malformed XML",
                file_size=1000,
                duration=0.1,
            ),
        )
        mock_downloader_class.return_value = mock_downloader

        result = runner.invoke(
            app, ["--url", "https://example.com/sitemap.xml", "--output", str(output_path)]
        )

        assert result.exit_code == 2

    @patch("sitemap_download.cli.SitemapDownloader")
    def test_skipped_download(self, mock_downloader_class, tmp_path):
        """Test skipped download (up-to-date)."""
        output_path = tmp_path / "sitemap.xml"

        # Mock skipped download
        mock_downloader = Mock()
        result_obj = DownloadResult.success_result(
            file_path=output_path,
            file_size=1000,
            duration=0.1,
        )
        result_obj.skipped = True
        mock_downloader.download.return_value = result_obj
        mock_downloader_class.return_value = mock_downloader

        result = runner.invoke(
            app, ["--url", "https://example.com/sitemap.xml", "--output", str(output_path)]
        )

        assert result.exit_code == 0
        assert "up-to-date" in result.stdout.lower()

    @patch("sitemap_download.cli.SitemapDownloader")
    @patch("sitemap_download.cli.archive_file")
    def test_archive_option(self, mock_archive, mock_downloader_class, tmp_path):
        """Test --archive option."""
        output_path = tmp_path / "sitemap.xml"
        output_path.write_text("<sitemap/>")

        mock_archive.return_value = tmp_path / "sitemap_2025_11_05.xml"

        # Mock successful download
        mock_downloader = Mock()
        mock_downloader.download.return_value = DownloadResult.success_result(
            file_path=output_path,
            file_size=1000,
            duration=1.0,
        )
        mock_downloader_class.return_value = mock_downloader

        result = runner.invoke(
            app,
            [
                "--url",
                "https://example.com/sitemap.xml",
                "--output",
                str(output_path),
                "--archive",
            ],
        )

        assert result.exit_code == 0
        assert mock_archive.called

    @patch("sitemap_download.cli.SitemapDownloader")
    def test_quiet_mode(self, mock_downloader_class, tmp_path):
        """Test --quiet option."""
        output_path = tmp_path / "sitemap.xml"

        # Mock successful download
        mock_downloader = Mock()
        mock_downloader.download.return_value = DownloadResult.success_result(
            file_path=output_path,
            file_size=1000,
            duration=1.0,
        )
        mock_downloader_class.return_value = mock_downloader

        result = runner.invoke(
            app,
            [
                "--url",
                "https://example.com/sitemap.xml",
                "--output",
                str(output_path),
                "--quiet",
            ],
        )

        assert result.exit_code == 0
        # Quiet mode should have minimal output
        assert len(result.stdout) < 100
