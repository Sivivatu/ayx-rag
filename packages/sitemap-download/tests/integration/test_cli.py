"""Integration tests for sitemap-download CLI."""

import pytest
from pathlib import Path
import subprocess
import sys


class TestCLIBasicDownload:
    """Tests for basic CLI download functionality."""

    def test_cli_basic_download(self, tmp_path, valid_sitemap_path):
        """Test basic download command with local file."""
        output_path = tmp_path / "downloaded.xml"

        # For now, this test will fail until we implement the CLI
        # This follows TDD: write failing test first
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "sitemap_download.cli",
                str(valid_sitemap_path),
                "--output",
                str(output_path),
            ],
            capture_output=True,
            text=True,
        )

        # These assertions define our expected behavior
        assert result.returncode == 0
        assert output_path.exists()
        assert output_path.stat().st_size > 0
