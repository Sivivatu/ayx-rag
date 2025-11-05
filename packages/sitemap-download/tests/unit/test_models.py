"""Tests for data models."""

from datetime import datetime
from pathlib import Path

import pytest
from sitemap_download.models import (
    DownloadConfig,
    DownloadProgress,
    DownloadResult,
    RemoteFileInfo,
    ValidationResult,
)


class TestDownloadConfig:
    """Tests for DownloadConfig dataclass."""

    def test_valid_config(self):
        """Test creating a valid configuration."""
        config = DownloadConfig(
            url="https://example.com/sitemap.xml",
            destination=Path("/tmp/sitemap.xml"),
        )
        assert config.url == "https://example.com/sitemap.xml"
        assert config.destination == Path("/tmp/sitemap.xml")
        assert config.force is False
        assert config.connection_timeout == 30.0
        assert config.read_timeout == 300.0
        assert config.max_retries == 3
        assert config.chunk_size == 8192

    def test_invalid_url_scheme(self):
        """Test that invalid URL scheme raises ValueError."""
        with pytest.raises(ValueError, match="Invalid URL scheme"):
            DownloadConfig(
                url="ftp://example.com/sitemap.xml",
                destination=Path("/tmp/sitemap.xml"),
            )

    def test_invalid_connection_timeout(self):
        """Test that zero or negative connection timeout raises ValueError."""
        with pytest.raises(ValueError, match="connection_timeout must be > 0"):
            DownloadConfig(
                url="https://example.com/sitemap.xml",
                destination=Path("/tmp/sitemap.xml"),
                connection_timeout=0,
            )

    def test_invalid_read_timeout(self):
        """Test that zero or negative read timeout raises ValueError."""
        with pytest.raises(ValueError, match="read_timeout must be > 0"):
            DownloadConfig(
                url="https://example.com/sitemap.xml",
                destination=Path("/tmp/sitemap.xml"),
                read_timeout=-1,
            )

    def test_invalid_max_retries(self):
        """Test that negative max_retries raises ValueError."""
        with pytest.raises(ValueError, match="max_retries must be >= 0"):
            DownloadConfig(
                url="https://example.com/sitemap.xml",
                destination=Path("/tmp/sitemap.xml"),
                max_retries=-1,
            )

    def test_invalid_chunk_size(self):
        """Test that zero or negative chunk size raises ValueError."""
        with pytest.raises(ValueError, match="chunk_size must be > 0"):
            DownloadConfig(
                url="https://example.com/sitemap.xml",
                destination=Path("/tmp/sitemap.xml"),
                chunk_size=0,
            )


class TestDownloadProgress:
    """Tests for DownloadProgress dataclass."""

    def test_percentage_calculation(self):
        """Test progress percentage calculation."""
        progress = DownloadProgress(
            total_bytes=1000,
            downloaded_bytes=250,
            start_time=datetime.now(),
            last_update_time=datetime.now(),
            bytes_per_second=100.0,
        )
        assert progress.percentage == 25.0

    def test_percentage_with_zero_total(self):
        """Test percentage calculation with zero total bytes."""
        progress = DownloadProgress(
            total_bytes=0,
            downloaded_bytes=0,
            start_time=datetime.now(),
            last_update_time=datetime.now(),
            bytes_per_second=0.0,
        )
        assert progress.percentage == 0.0

    def test_eta_calculation(self):
        """Test ETA calculation."""
        progress = DownloadProgress(
            total_bytes=1000,
            downloaded_bytes=250,
            start_time=datetime.now(),
            last_update_time=datetime.now(),
            bytes_per_second=100.0,
        )
        # Remaining: 750 bytes at 100 bytes/sec = 7.5 seconds
        assert progress.eta_seconds == 7.5

    def test_eta_with_zero_speed(self):
        """Test ETA calculation with zero download speed."""
        progress = DownloadProgress(
            total_bytes=1000,
            downloaded_bytes=0,
            start_time=datetime.now(),
            last_update_time=datetime.now(),
            bytes_per_second=0.0,
        )
        assert progress.eta_seconds == float("inf")


class TestDownloadResult:
    """Tests for DownloadResult dataclass."""

    def test_success_result_factory(self):
        """Test creating a successful result."""
        result = DownloadResult.success_result(
            file_path=Path("/tmp/sitemap.xml"),
            file_size=1024,
            duration=5.0,
            retry_count=1,
        )
        assert result.success is True
        assert result.file_path == Path("/tmp/sitemap.xml")
        assert result.file_size == 1024
        assert result.duration_seconds == 5.0
        assert result.error_message is None
        assert result.retry_count == 1
        assert result.skipped is False

    def test_success_result_skipped(self):
        """Test creating a skipped result."""
        result = DownloadResult.success_result(
            file_path=Path("/tmp/sitemap.xml"),
            file_size=1024,
            duration=0.5,
            skipped=True,
        )
        assert result.success is True
        assert result.skipped is True

    def test_failure_result_factory(self):
        """Test creating a failed result."""
        result = DownloadResult.failure_result(
            error="Network timeout",
            duration=30.0,
            retry_count=3,
        )
        assert result.success is False
        assert result.file_path is None
        assert result.file_size is None
        assert result.duration_seconds == 30.0
        assert result.error_message == "Network timeout"
        assert result.retry_count == 3
        assert result.skipped is False


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_valid_result_factory(self):
        """Test creating a valid validation result."""
        result = ValidationResult.valid_result(
            url_count=100,
            file_size=1024,
            duration=0.5,
        )
        assert result.valid is True
        assert result.url_count == 100
        assert result.file_size == 1024
        assert result.error_message is None
        assert result.validation_duration == 0.5

    def test_invalid_result_factory(self):
        """Test creating an invalid validation result."""
        result = ValidationResult.invalid_result(
            error="Not well-formed XML",
            file_size=512,
            duration=0.2,
        )
        assert result.valid is False
        assert result.url_count is None
        assert result.file_size == 512
        assert result.error_message == "Not well-formed XML"
        assert result.validation_duration == 0.2


class TestRemoteFileInfo:
    """Tests for RemoteFileInfo dataclass."""

    def test_remote_file_info_creation(self):
        """Test creating remote file info."""
        info = RemoteFileInfo(
            url="https://example.com/sitemap.xml",
            size=1024,
            last_modified=datetime(2025, 11, 4, 12, 0, 0),
            etag='"abc123"',
            content_type="application/xml",
        )
        assert info.url == "https://example.com/sitemap.xml"
        assert info.size == 1024
        assert info.last_modified == datetime(2025, 11, 4, 12, 0, 0)
        assert info.etag == '"abc123"'
        assert info.content_type == "application/xml"

    def test_remote_file_info_with_none_values(self):
        """Test creating remote file info with None values."""
        info = RemoteFileInfo(
            url="https://example.com/sitemap.xml",
            size=None,
            last_modified=None,
            etag=None,
            content_type=None,
        )
        assert info.url == "https://example.com/sitemap.xml"
        assert info.size is None
        assert info.last_modified is None
        assert info.etag is None
        assert info.content_type is None

    def test_has_size_property(self):
        """Test has_size property."""
        info_with_size = RemoteFileInfo(
            url="https://example.com/sitemap.xml",
            size=1024,
            last_modified=None,
            etag=None,
            content_type=None,
        )
        info_without_size = RemoteFileInfo(
            url="https://example.com/sitemap.xml",
            size=None,
            last_modified=None,
            etag=None,
            content_type=None,
        )
        assert info_with_size.has_size is True
        assert info_without_size.has_size is False

    def test_has_last_modified_property(self):
        """Test has_last_modified property."""
        info_with_date = RemoteFileInfo(
            url="https://example.com/sitemap.xml",
            size=None,
            last_modified=datetime.now(),
            etag=None,
            content_type=None,
        )
        info_without_date = RemoteFileInfo(
            url="https://example.com/sitemap.xml",
            size=None,
            last_modified=None,
            etag=None,
            content_type=None,
        )
        assert info_with_date.has_last_modified is True
        assert info_without_date.has_last_modified is False

    def test_has_etag_property(self):
        """Test has_etag property."""
        info_with_etag = RemoteFileInfo(
            url="https://example.com/sitemap.xml",
            size=None,
            last_modified=None,
            etag='"abc123"',
            content_type=None,
        )
        info_without_etag = RemoteFileInfo(
            url="https://example.com/sitemap.xml",
            size=None,
            last_modified=None,
            etag=None,
            content_type=None,
        )
        assert info_with_etag.has_etag is True
        assert info_without_etag.has_etag is False
