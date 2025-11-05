"""Unit tests for CLI helper functions."""

import pytest
from pathlib import Path
from datetime import datetime
from io import StringIO
import sys
from sitemap_download.utils import archive_file, format_bytes
from sitemap_download.cli import format_progress_bar, display_progress
from sitemap_download.models import DownloadProgress


class TestArchiveFile:
    """Tests for archive_file function."""

    def test_archive_nonexistent_file(self, tmp_path):
        """Test archiving when file doesn't exist returns None."""
        file_path = tmp_path / "nonexistent.xml"
        result = archive_file(file_path)
        assert result is None

    def test_archive_existing_file(self, tmp_path):
        """Test archiving creates timestamped copy."""
        # Create a test file
        file_path = tmp_path / "sitemap.xml"
        file_path.write_text("<sitemap>test</sitemap>")
        
        # Archive it
        archive_path = archive_file(file_path)
        
        # Verify archive was created
        assert archive_path is not None
        assert archive_path.exists()
        assert archive_path.parent == file_path.parent
        assert archive_path.read_text() == "<sitemap>test</sitemap>"
        
        # Verify timestamp format in filename
        stem = archive_path.stem
        assert stem.startswith("sitemap_")
        # Should be like: sitemap_2025_11_05_10_30
        parts = stem.split("_")
        assert len(parts) == 6  # sitemap, year, month, day, hour, minute
        assert parts[1].isdigit() and len(parts[1]) == 4  # year
        assert parts[2].isdigit() and len(parts[2]) == 2  # month
        assert parts[3].isdigit() and len(parts[3]) == 2  # day
        assert parts[4].isdigit() and len(parts[4]) == 2  # hour
        assert parts[5].isdigit() and len(parts[5]) == 2  # minute

    def test_archive_preserves_original(self, tmp_path):
        """Test archiving doesn't delete original file."""
        file_path = tmp_path / "sitemap.xml"
        file_path.write_text("<sitemap>test</sitemap>")
        
        archive_path = archive_file(file_path)
        
        # Original should still exist
        assert file_path.exists()
        assert archive_path.exists()
        
        # Both should have same content
        assert file_path.read_text() == archive_path.read_text()

    def test_archive_with_complex_filename(self, tmp_path):
        """Test archiving file with dots in name."""
        file_path = tmp_path / "alteryx-help-current-sitemap.xml"
        file_path.write_text("<sitemap>test</sitemap>")
        
        archive_path = archive_file(file_path)
        
        assert archive_path is not None
        assert archive_path.suffix == ".xml"
        assert "alteryx-help-current-sitemap" in archive_path.stem


class TestFormatBytes:
    """Tests for format_bytes function."""

    def test_format_bytes(self):
        """Test byte formatting."""
        assert "1.0 B" in format_bytes(1)
        assert "1.0 KB" in format_bytes(1024)
        assert "1.0 MB" in format_bytes(1024 * 1024)
        assert "1.0 GB" in format_bytes(1024 * 1024 * 1024)
        
    def test_format_bytes_fractional(self):
        """Test fractional values."""
        assert "1.5" in format_bytes(1536)  # 1.5 KB
        assert "KB" in format_bytes(1536)


class TestFormatProgressBar:
    """Tests for format_progress_bar function."""

    def test_format_progress_bar_partial(self):
        """Test progress bar formatting at 50%."""
        progress = DownloadProgress(
            total_bytes=1000,
            downloaded_bytes=500,
            start_time=datetime.now(),
            last_update_time=datetime.now(),
            bytes_per_second=100.0,
        )
        
        result = format_progress_bar(progress, width=20)
        
        # Should show 50% progress
        assert "50%" in result
        assert "500" in result  # Downloaded bytes
        assert "1.0 KB" in result or "1000" in result  # Total
        assert "/s" in result  # Speed indicator
        assert "ETA" in result

    def test_format_progress_bar_complete(self):
        """Test progress bar at 100%."""
        progress = DownloadProgress(
            total_bytes=1000,
            downloaded_bytes=1000,
            start_time=datetime.now(),
            last_update_time=datetime.now(),
            bytes_per_second=100.0,
        )
        
        result = format_progress_bar(progress, width=20)
        
        assert "100%" in result
        assert "█" in result  # Filled bar character

    def test_format_progress_bar_no_eta(self):
        """Test progress bar when ETA is not calculable."""
        progress = DownloadProgress(
            total_bytes=1000,
            downloaded_bytes=0,
            start_time=datetime.now(),
            last_update_time=datetime.now(),
            bytes_per_second=0.0,
        )
        
        result = format_progress_bar(progress)
        
        # Should show "--" for ETA when not calculable
        assert "ETA: --" in result or "ETA: 0s" in result


class TestDisplayProgress:
    """Tests for display_progress function."""

    def test_display_progress_quiet_mode(self, capsys):
        """Test that quiet mode suppresses output."""
        progress = DownloadProgress(
            total_bytes=1000,
            downloaded_bytes=500,
            start_time=datetime.now(),
            last_update_time=datetime.now(),
            bytes_per_second=100.0,
        )
        
        display_progress(progress, quiet=True)
        
        captured = capsys.readouterr()
        # Should not output anything in quiet mode
        assert captured.out == ""

    def test_display_progress_normal_mode(self, capsys):
        """Test that normal mode shows progress."""
        progress = DownloadProgress(
            total_bytes=1000,
            downloaded_bytes=500,
            start_time=datetime.now(),
            last_update_time=datetime.now(),
            bytes_per_second=100.0,
        )
        
        display_progress(progress, quiet=False)
        
        captured = capsys.readouterr()
        # Should show progress in normal mode
        assert "50%" in captured.out or len(captured.out) > 0
