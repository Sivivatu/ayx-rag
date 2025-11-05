"""Tests for SitemapDownloader class."""

from unittest.mock import MagicMock, Mock, patch

import httpx
from sitemap_download.downloader import SitemapDownloader
from sitemap_download.models import (
    DownloadConfig,
    DownloadProgress,
)


class TestDownloaderInit:
    """Tests for SitemapDownloader initialization."""

    def test_downloader_init(self, tmp_path):
        """Test that downloader initializes with valid config."""
        config = DownloadConfig(
            url="https://example.com/sitemap.xml",
            destination=tmp_path / "sitemap.xml",
        )
        downloader = SitemapDownloader(config)
        assert downloader.config == config

    def test_downloader_init_with_custom_timeouts(self, tmp_path):
        """Test downloader with custom timeout values."""
        config = DownloadConfig(
            url="https://example.com/sitemap.xml",
            destination=tmp_path / "sitemap.xml",
            connection_timeout=10.0,
            read_timeout=60.0,
        )
        downloader = SitemapDownloader(config)
        assert downloader.config.connection_timeout == 10.0
        assert downloader.config.read_timeout == 60.0


class TestDownloadSuccess:
    """Tests for successful downloads."""

    @patch("httpx.Client")
    def test_download_success(self, mock_client_class, tmp_path):
        """Test successful download with mocked HTTP response."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {
            "content-length": "1024",
            "last-modified": "Mon, 01 Nov 2025 12:00:00 GMT",
        }
        mock_response.iter_bytes = Mock(return_value=[b"test" * 256])  # 1024 bytes
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_response.raise_for_status = Mock()

        mock_client = MagicMock()
        mock_client.stream = Mock(return_value=mock_response)
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client_class.return_value = mock_client

        # Create downloader
        config = DownloadConfig(
            url="https://example.com/sitemap.xml",
            destination=tmp_path / "sitemap.xml",
            force=True,
        )
        downloader = SitemapDownloader(config)

        # Perform download
        result = downloader.download()

        # Verify success
        assert result.success is True
        assert result.file_path == tmp_path / "sitemap.xml"
        assert result.file_size == 1024
        assert result.error_message is None
        assert result.skipped is False


class TestDownloadWithProgressCallback:
    """Tests for download with progress tracking."""

    @patch("httpx.Client")
    def test_download_with_progress_callback(self, mock_client_class, tmp_path):
        """Test that progress callback is invoked during download."""
        # Setup mock response with chunked data
        chunks = [b"x" * 100_000 for _ in range(10)]  # 1MB total in 100KB chunks
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-length": str(sum(len(c) for c in chunks))}
        mock_response.iter_bytes = Mock(return_value=chunks)
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_response.raise_for_status = Mock()

        mock_client = MagicMock()
        mock_client.stream = Mock(return_value=mock_response)
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client_class.return_value = mock_client

        # Create downloader
        config = DownloadConfig(
            url="https://example.com/sitemap.xml",
            destination=tmp_path / "sitemap.xml",
            force=True,
        )
        downloader = SitemapDownloader(config)

        # Track progress callbacks
        progress_calls = []

        def progress_callback(progress: DownloadProgress):
            progress_calls.append(progress)

        # Perform download
        result = downloader.download(progress_callback=progress_callback)

        # Verify callbacks were made
        assert result.success is True
        assert len(progress_calls) > 0
        # First callback should show partial progress
        assert progress_calls[0].percentage < 100
        # Last callback should show completion
        assert progress_calls[-1].percentage == 100


class TestDownloadNetworkError:
    """Tests for network error handling."""

    @patch("httpx.Client")
    def test_download_network_error(self, mock_client_class, tmp_path):
        """Test that network errors are handled gracefully."""
        mock_client = MagicMock()
        mock_client.stream = Mock(side_effect=httpx.ConnectError("Connection refused"))
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client_class.return_value = mock_client

        config = DownloadConfig(
            url="https://example.com/sitemap.xml",
            destination=tmp_path / "sitemap.xml",
            force=True,
        )
        downloader = SitemapDownloader(config)

        result = downloader.download()

        assert result.success is False
        assert result.error_message is not None
        assert "Connection" in result.error_message or "Network" in result.error_message
        assert result.file_path is None


class TestDownloadTimeout:
    """Tests for timeout handling."""

    @patch("httpx.Client")
    def test_download_timeout(self, mock_client_class, tmp_path):
        """Test that timeouts are handled gracefully."""
        mock_client = MagicMock()
        mock_client.stream = Mock(side_effect=httpx.TimeoutException("Read timeout"))
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client_class.return_value = mock_client

        config = DownloadConfig(
            url="https://example.com/sitemap.xml",
            destination=tmp_path / "sitemap.xml",
            connection_timeout=5.0,
            read_timeout=10.0,
            force=True,
        )
        downloader = SitemapDownloader(config)

        result = downloader.download()

        assert result.success is False
        assert result.error_message is not None
        assert "timeout" in result.error_message.lower()


class TestCheckDiskSpace:
    """Tests for disk space checking (optional feature)."""

    def test_check_disk_space_sufficient(self, tmp_path):
        """Test disk space check when sufficient space available."""
        config = DownloadConfig(
            url="https://example.com/sitemap.xml",
            destination=tmp_path / "sitemap.xml",
        )
        downloader = SitemapDownloader(config)

        # Check if enough space for 10MB file
        has_space = downloader.check_disk_space(required_bytes=10 * 1024 * 1024)
        assert has_space is True

    def test_check_disk_space_insufficient(self, tmp_path):
        """Test disk space check when insufficient space."""
        config = DownloadConfig(
            url="https://example.com/sitemap.xml",
            destination=tmp_path / "sitemap.xml",
        )
        downloader = SitemapDownloader(config)

        # Check if enough space for impossibly large file (1PB)
        has_space = downloader.check_disk_space(required_bytes=1024**5)
        assert has_space is False


class TestDownloadRetry:
    """Tests for download retry logic."""

    @patch("httpx.Client")
    @patch("time.sleep")  # Mock sleep to speed up tests
    def test_download_retry_transient_error(self, mock_sleep, mock_client_class, tmp_path):
        """Test that transient errors (5xx, timeouts) trigger retries."""
        # Setup: fail twice with 503, then succeed
        mock_response_fail = MagicMock()
        mock_response_fail.status_code = 503
        mock_response_fail.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Service Unavailable", request=Mock(), response=mock_response_fail
        )

        mock_response_success = MagicMock()
        mock_response_success.status_code = 200
        mock_response_success.headers = {"content-length": "100"}
        mock_response_success.iter_bytes.return_value = [b"<urlset></urlset>"]

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client

        # First two calls fail, third succeeds
        mock_client.stream.side_effect = [
            httpx.HTTPStatusError(
                "Service Unavailable", request=Mock(), response=mock_response_fail
            ),
            httpx.HTTPStatusError(
                "Service Unavailable", request=Mock(), response=mock_response_fail
            ),
            MagicMock(__enter__=lambda self: mock_response_success, __exit__=lambda *args: None),
        ]

        mock_client_class.return_value = mock_client

        config = DownloadConfig(
            url="https://example.com/sitemap.xml",
            destination=tmp_path / "sitemap.xml",
            max_retries=3,
        )
        downloader = SitemapDownloader(config)
        result = downloader.download()

        assert result.success is True
        assert result.retry_count == 2  # Two retries before success
        assert mock_sleep.call_count == 2  # Sleep called between retries

    @patch("httpx.Client")
    @patch("time.sleep")
    def test_download_max_retries_exceeded(self, mock_sleep, mock_client_class, tmp_path):
        """Test that download fails after exceeding max retries."""
        mock_response = MagicMock()
        mock_response.status_code = 503

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.stream.side_effect = httpx.HTTPStatusError(
            "Service Unavailable", request=Mock(), response=mock_response
        )

        mock_client_class.return_value = mock_client

        config = DownloadConfig(
            url="https://example.com/sitemap.xml",
            destination=tmp_path / "sitemap.xml",
            max_retries=2,
        )
        downloader = SitemapDownloader(config)
        result = downloader.download()

        assert result.success is False
        assert result.retry_count == 2
        assert "after 2 retries" in result.error_message.lower() or "503" in result.error_message

    @patch("httpx.Client")
    def test_download_non_retryable_error(self, mock_client_class, tmp_path):
        """Test that 4xx errors don't trigger retries."""
        mock_response = MagicMock()
        mock_response.status_code = 404

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.stream.side_effect = httpx.HTTPStatusError(
            "Not Found", request=Mock(), response=mock_response
        )

        mock_client_class.return_value = mock_client

        config = DownloadConfig(
            url="https://example.com/sitemap.xml",
            destination=tmp_path / "sitemap.xml",
            max_retries=3,
        )
        downloader = SitemapDownloader(config)
        result = downloader.download()

        assert result.success is False
        assert result.retry_count == 0  # No retries for 404
        assert "404" in result.error_message or "not found" in result.error_message.lower()

    @patch("httpx.Client")
    @patch("time.sleep")
    def test_download_preserves_existing_file_on_failure(
        self, mock_sleep, mock_client_class, tmp_path
    ):
        """Test that existing file is not corrupted when download fails after retries."""
        destination = tmp_path / "sitemap.xml"

        # Create existing file
        original_content = b"<urlset><url><loc>https://original.com</loc></url></urlset>"
        destination.write_bytes(original_content)
        original_mtime = destination.stat().st_mtime

        mock_response = MagicMock()
        mock_response.status_code = 500

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.stream.side_effect = httpx.HTTPStatusError(
            "Internal Server Error", request=Mock(), response=mock_response
        )

        mock_client_class.return_value = mock_client

        config = DownloadConfig(
            url="https://example.com/sitemap.xml",
            destination=destination,
            max_retries=2,
            force=True,  # Try to download even though file exists
        )
        downloader = SitemapDownloader(config)
        result = downloader.download()

        assert result.success is False
        assert destination.exists()
        # Original file should be preserved
        assert destination.read_bytes() == original_content
        assert destination.stat().st_mtime == original_mtime
