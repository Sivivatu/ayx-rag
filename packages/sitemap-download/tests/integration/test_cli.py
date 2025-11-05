"""Integration tests for sitemap-download CLI."""

import pytest
from pathlib import Path
import subprocess
import sys


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
