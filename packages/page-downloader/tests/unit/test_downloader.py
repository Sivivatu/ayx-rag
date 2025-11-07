"""Unit tests for downloader module - HTTP download functionality."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import respx
from httpx import ConnectError, ReadTimeout, Response
from page_downloader.downloader import HTTPDownloader
from page_downloader.models import DownloadConfig


class TestHTTPDownloaderInit:
    """Test HTTPDownloader initialization."""

    def test_downloader_init_with_config(self, sample_config):
        """Test that downloader initializes with valid config."""
        downloader = HTTPDownloader(sample_config)
        assert downloader.config == sample_config
        assert downloader.client is not None

    def test_downloader_creates_httpx_client(self, sample_config):
        """Test that downloader creates httpx.Client with correct settings."""
        downloader = HTTPDownloader(sample_config)
        # Verify client has proper timeouts
        assert downloader.client.timeout.connect == sample_config.connection_timeout
        assert downloader.client.timeout.read == sample_config.read_timeout


class TestAtomicWrite:
    """Test atomic file write functionality per FR-021."""

    def test_atomic_write_creates_file(self, temp_output_dir):
        """Test that atomic write creates file successfully."""
        config = DownloadConfig(output_dir=temp_output_dir)
        downloader = HTTPDownloader(config)

        file_path = temp_output_dir / "test.html"
        content = b"<html><body>test</body></html>"

        downloader._atomic_write(file_path, content)

        assert file_path.exists()
        assert file_path.read_bytes() == content

    def test_atomic_write_creates_parent_directories(self, temp_output_dir):
        """Test that atomic write creates parent directories per FR-027b."""
        config = DownloadConfig(output_dir=temp_output_dir)
        downloader = HTTPDownloader(config)

        file_path = temp_output_dir / "nested" / "deep" / "path" / "test.html"
        content = b"<html><body>test</body></html>"

        downloader._atomic_write(file_path, content)

        assert file_path.exists()
        assert file_path.parent.exists()
        assert file_path.read_bytes() == content

    def test_atomic_write_preserves_existing_on_failure(self, temp_output_dir):
        """Test that atomic write preserves existing file if write fails per FR-020."""
        config = DownloadConfig(output_dir=temp_output_dir)
        downloader = HTTPDownloader(config)

        file_path = temp_output_dir / "test.html"
        original_content = b"<html><body>original</body></html>"
        file_path.write_bytes(original_content)

        # Simulate write failure by making temp file creation fail
        with patch("tempfile.mkstemp", side_effect=OSError("Disk full")), pytest.raises(
            OSError
        ):
            downloader._atomic_write(file_path, b"new content")

        # Original file should still exist with original content
        assert file_path.exists()
        assert file_path.read_bytes() == original_content

    def test_atomic_write_uses_temp_file(self, temp_output_dir):
        """Test that atomic write uses temporary file pattern."""
        config = DownloadConfig(output_dir=temp_output_dir)
        downloader = HTTPDownloader(config)

        file_path = temp_output_dir / "test.html"
        content = b"<html><body>test</body></html>"

        # Track if temp file was created during write
        temp_files_created = []
        original_mkstemp = tempfile.mkstemp

        def track_mkstemp(*args, **kwargs):
            fd, path = original_mkstemp(*args, **kwargs)
            temp_files_created.append(path)
            return fd, path

        with patch("tempfile.mkstemp", side_effect=track_mkstemp):
            downloader._atomic_write(file_path, content)

        # Should have used mkstemp to create a temp file
        assert len(temp_files_created) > 0
        # Temp file should not exist after completion (renamed to final path)
        for temp_file in temp_files_created:
            assert not Path(temp_file).exists()
        # Final file should exist
        assert file_path.exists()


class TestDownloadSinglePage:
    """Test downloading a single page per FR-003."""

    @respx.mock
    def test_download_success_html(self, sample_config, temp_output_dir, mock_html_response):
        """Test successful download of HTML content."""
        config = DownloadConfig(output_dir=temp_output_dir)
        downloader = HTTPDownloader(config)

        url = "https://help.alteryx.com/current/en/designer/tools.html"
        respx.get(url).mock(return_value=mock_html_response)

        result = downloader.download_page(url)

        assert result.success is True
        assert result.url == url
        assert result.file_path is not None
        assert Path(result.file_path).exists()
        assert result.bytes_downloaded > 0

    @respx.mock
    def test_download_skips_non_html_content(self, sample_config, mock_non_html_response):
        """Test that non-HTML content is skipped per FR-012."""
        downloader = HTTPDownloader(sample_config)

        url = "https://help.alteryx.com/current/en/document.pdf"
        respx.get(url).mock(return_value=mock_non_html_response)

        result = downloader.download_page(url)

        assert result.success is False
        assert result.skipped is True
        assert "non-HTML" in result.error_message or "application/pdf" in result.error_message

    @respx.mock
    def test_download_enforces_max_file_size(self, sample_config, mock_large_response):
        """Test that downloads exceeding max file size are aborted per FR-008a."""
        downloader = HTTPDownloader(sample_config)

        url = "https://help.alteryx.com/current/en/large.html"
        respx.get(url).mock(return_value=mock_large_response)

        result = downloader.download_page(url)

        assert result.success is False
        assert "size" in result.error_message.lower()

    @respx.mock
    def test_download_uses_sanitized_path(self, sample_config, temp_output_dir, mock_html_response):
        """Test that downloaded files use sanitized path per FR-005."""
        config = DownloadConfig(output_dir=temp_output_dir)
        downloader = HTTPDownloader(config)

        # URL with invalid characters and query params
        url = "https://help.alteryx.com/current/en/file:name.html?version=2024#section"
        respx.get(url).mock(return_value=mock_html_response)

        result = downloader.download_page(url)

        assert result.success is True
        # Path should be sanitized (no : or ? or #)
        assert ":" not in str(result.file_path)
        assert "?" not in str(result.file_path)
        assert "#" not in str(result.file_path)

    @respx.mock
    def test_download_follows_redirects(self, sample_config, temp_output_dir, mock_html_response):
        """Test that downloader follows redirects per FR-023."""
        config = DownloadConfig(output_dir=temp_output_dir)
        downloader = HTTPDownloader(config)

        original_url = "https://help.alteryx.com/old/path.html"
        final_url = "https://help.alteryx.com/current/en/designer/tools.html"

        # Mock redirect chain
        redirect_response = Response(
            status_code=301,
            headers={"location": final_url},
        )
        respx.get(original_url).mock(return_value=redirect_response)
        respx.get(final_url).mock(return_value=mock_html_response)

        result = downloader.download_page(original_url)

        assert result.success is True
        # File path should be based on final URL per FR-023
        assert "current/en/designer" in str(result.file_path)


class TestDownloadErrorHandling:
    """Test error handling during downloads."""

    @respx.mock
    def test_download_handles_connection_error(self, sample_config):
        """Test handling of connection errors."""
        downloader = HTTPDownloader(sample_config)

        url = "https://help.alteryx.com/current/en/designer/tools.html"
        respx.get(url).mock(side_effect=ConnectError("Connection refused"))

        result = downloader.download_page(url)

        assert result.success is False
        assert result.skipped is False
        assert "connection" in result.error_message.lower()

    @respx.mock
    def test_download_handles_timeout(self, sample_config):
        """Test handling of read timeout per FR-008."""
        downloader = HTTPDownloader(sample_config)

        url = "https://help.alteryx.com/current/en/designer/tools.html"
        respx.get(url).mock(side_effect=ReadTimeout("Read timeout"))

        result = downloader.download_page(url)

        assert result.success is False
        assert "timeout" in result.error_message.lower()

    @respx.mock
    def test_download_handles_404_error(self, sample_config):
        """Test handling of 404 errors (non-retryable per FR-011)."""
        downloader = HTTPDownloader(sample_config)

        url = "https://help.alteryx.com/current/en/missing.html"
        response_404 = Response(status_code=404, content=b"Not Found")
        respx.get(url).mock(return_value=response_404)

        result = downloader.download_page(url)

        assert result.success is False
        assert "404" in result.error_message

    @respx.mock
    def test_download_handles_500_error(self, sample_config):
        """Test handling of 500 errors (retryable per FR-011)."""
        downloader = HTTPDownloader(sample_config)

        url = "https://help.alteryx.com/current/en/designer/tools.html"
        response_500 = Response(status_code=500, content=b"Internal Server Error")
        respx.get(url).mock(return_value=response_500)

        result = downloader.download_page(url)

        assert result.success is False
        assert "500" in result.error_message


class TestDownloadRetryLogic:
    """Test retry logic with exponential backoff per FR-009."""

    @respx.mock
    def test_download_retries_on_timeout(self, sample_config):
        """Test that timeouts trigger retry logic per FR-011."""
        downloader = HTTPDownloader(sample_config)

        url = "https://help.alteryx.com/current/en/designer/tools.html"

        # Track number of attempts
        attempt_count = 0

        def timeout_then_success(*args, **kwargs):
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                raise ReadTimeout("Timeout")
            return Response(
                status_code=200,
                headers={"content-type": "text/html"},
                content=b"<html><body>success</body></html>",
            )

        respx.get(url).mock(side_effect=timeout_then_success)

        result = downloader.download_page(url)

        assert result.success is True
        assert attempt_count == 2  # First attempt failed, second succeeded

    @respx.mock
    def test_download_respects_max_retries(self, sample_config):
        """Test that max retries is respected per FR-010."""
        downloader = HTTPDownloader(sample_config)

        url = "https://help.alteryx.com/current/en/designer/tools.html"

        # Always timeout
        respx.get(url).mock(side_effect=ReadTimeout("Timeout"))

        result = downloader.download_page(url)

        assert result.success is False
        # Should have attempted: 1 initial + max_retries (2) = 3 total
        assert respx.calls.call_count == sample_config.max_retries + 1

    @respx.mock
    def test_download_no_retry_on_404(self, sample_config):
        """Test that 4xx errors don't trigger retries per FR-011."""
        downloader = HTTPDownloader(sample_config)

        url = "https://help.alteryx.com/current/en/missing.html"
        response_404 = Response(status_code=404, content=b"Not Found")
        respx.get(url).mock(return_value=response_404)

        result = downloader.download_page(url)

        assert result.success is False
        # Should only attempt once (no retries for 4xx)
        assert respx.calls.call_count == 1


class TestDownloadStreaming:
    """Test streaming download functionality."""

    @respx.mock
    def test_download_streams_response(self, sample_config, temp_output_dir, mock_html_response):
        """Test that downloads use streaming to handle large files."""
        config = DownloadConfig(output_dir=temp_output_dir)
        downloader = HTTPDownloader(config)

        url = "https://help.alteryx.com/current/en/designer/tools.html"
        respx.get(url).mock(return_value=mock_html_response)

        result = downloader.download_page(url)

        assert result.success is True
        # Content should be written to disk
        assert Path(result.file_path).exists()

    @respx.mock
    def test_download_aborts_on_size_exceeded_during_stream(self, sample_config, temp_output_dir):
        """Test that download aborts if size exceeds limit during streaming per FR-008a."""
        config = DownloadConfig(
            output_dir=temp_output_dir,
            max_file_size=100,  # Very small limit
        )
        downloader = HTTPDownloader(config)

        url = "https://help.alteryx.com/current/en/designer/tools.html"

        # Create response with content larger than limit
        large_content = b"x" * 200
        response = Response(
            status_code=200,
            headers={"content-type": "text/html"},
            content=large_content,
        )
        respx.get(url).mock(return_value=response)

        result = downloader.download_page(url)

        assert result.success is False
        assert "size" in result.error_message.lower()
