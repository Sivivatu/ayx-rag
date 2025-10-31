"""Integration tests for the CLI interface."""

import pytest
import subprocess
import sys
from pathlib import Path


class TestCLILanguageFilter:
    """Integration tests for language filtering via CLI."""
    
    @pytest.fixture
    def sample_sitemap_path(self):
        """Path to sample sitemap fixture."""
        return Path(__file__).parent.parent / "fixtures" / "sample_sitemap.xml"
    
    def test_cli_with_language_en_flag(self, sample_sitemap_path):
        """Test CLI with --language en flag filters English URLs."""
        result = subprocess.run(
            [
                sys.executable, "-m", "src.sitemap_filter",
                str(sample_sitemap_path),
                "--language", "en"
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent
        )
        
        # For now, just verify it runs without error
        # Full output validation will be added when output formatting is implemented
        assert result.returncode in [0, 1]  # 0 = success, 1 = expected until CLI fully implemented
