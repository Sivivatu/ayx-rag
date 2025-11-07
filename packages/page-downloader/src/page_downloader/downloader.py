"""HTTP downloader for fetching HTML pages."""

import contextlib
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

import certifi
import httpx
from loguru import logger

from .models import DownloadConfig
from .path_utils import sanitize_url_path
from .validator import is_html_content


@dataclass
class DownloadResult:
    """Result of a download operation.

    Attributes:
        url: Source URL
        success: Whether download succeeded
        skipped: Whether download was skipped (e.g., non-HTML)
        file_path: Path to downloaded file (None if failed/skipped)
        bytes_downloaded: Number of bytes downloaded
        error_message: Error description if failed
        status_code: HTTP status code
    """

    url: str
    success: bool
    skipped: bool = False
    file_path: str | None = None
    bytes_downloaded: int = 0
    error_message: str = ""
    status_code: int | None = None


class HTTPDownloader:
    """HTTP downloader with streaming, retry logic, and atomic writes."""

    def __init__(self, config: DownloadConfig):
        """Initialize downloader with configuration.

        Args:
            config: Download configuration settings
        """
        self.config = config

        # Create httpx client with configured timeouts per FR-007, FR-008
        # Use certifi CA bundle if SSL verification enabled, otherwise disable verification
        ssl_verify = certifi.where() if config.verify_ssl else False

        self.client = httpx.Client(
            timeout=httpx.Timeout(
                connect=config.connection_timeout,
                read=config.read_timeout,
                write=config.connection_timeout,
                pool=config.connection_timeout,
            ),
            follow_redirects=True,  # FR-023: Follow redirects
            verify=ssl_verify,  # FR-022a: Use certifi's CA bundle or disable for dev/testing
            headers={
                "User-Agent": config.user_agent,
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Encoding": "gzip, deflate",
            },
        )

    def download_page(self, url: str) -> DownloadResult:
        """Download a single page from URL.

        Implements FR-003, FR-011, FR-012, FR-017, FR-020, FR-021, FR-023.

        Args:
            url: URL to download

        Returns:
            DownloadResult with outcome details
        """
        logger.info(f"Starting download: {url}")

        # Attempt download with retry logic
        for attempt in range(self.config.max_retries + 1):
            try:
                result = self._attempt_download(url)

                # Log successful download per FR-017
                if result.success:
                    logger.info(
                        f"Downloaded {url} -> {result.file_path} ({result.bytes_downloaded} bytes)"
                    )
                elif result.skipped:
                    logger.warning(f"Skipped {url}: {result.error_message}")

                return result

            except httpx.TimeoutException as e:
                # Retryable error per FR-011
                if attempt < self.config.max_retries:
                    backoff = self._calculate_backoff(attempt)
                    logger.warning(
                        f"Timeout downloading {url}, retrying in {backoff:.1f}s "
                        f"(attempt {attempt + 1}/{self.config.max_retries})"
                    )
                    time.sleep(backoff)
                    continue
                else:
                    logger.error(f"Failed to download {url} after {attempt + 1} attempts: {e}")
                    return DownloadResult(
                        url=url,
                        success=False,
                        error_message=f"Timeout after {attempt + 1} attempts: {e}",
                    )

            except httpx.ConnectError as e:
                # Retryable error per FR-011
                if attempt < self.config.max_retries:
                    backoff = self._calculate_backoff(attempt)
                    logger.warning(
                        f"Connection error downloading {url}, retrying in {backoff:.1f}s "
                        f"(attempt {attempt + 1}/{self.config.max_retries})"
                    )
                    time.sleep(backoff)
                    continue
                else:
                    logger.error(f"Failed to download {url} after {attempt + 1} attempts: {e}")
                    return DownloadResult(
                        url=url,
                        success=False,
                        error_message=f"Connection error after {attempt + 1} attempts: {e}",
                    )

            except httpx.HTTPStatusError as e:
                # Check if retryable (5xx) or not (4xx) per FR-011
                if 500 <= e.response.status_code < 600 and attempt < self.config.max_retries:
                    backoff = self._calculate_backoff(attempt)
                    logger.warning(
                        f"HTTP {e.response.status_code} for {url}, retrying in {backoff:.1f}s "
                        f"(attempt {attempt + 1}/{self.config.max_retries})"
                    )
                    time.sleep(backoff)
                    continue
                else:
                    # 4xx errors are non-retryable
                    logger.error(f"HTTP error downloading {url}: {e.response.status_code}")
                    return DownloadResult(
                        url=url,
                        success=False,
                        status_code=e.response.status_code,
                        error_message=f"HTTP {e.response.status_code}",
                    )

            except Exception as e:
                logger.error(f"Unexpected error downloading {url}: {e}")
                return DownloadResult(
                    url=url,
                    success=False,
                    error_message=f"Unexpected error: {e}",
                )

        # Should not reach here
        return DownloadResult(
            url=url,
            success=False,
            error_message="Max retries exceeded",
        )

    def _attempt_download(self, url: str) -> DownloadResult:
        """Attempt to download URL once (no retries).

        Args:
            url: URL to download

        Returns:
            DownloadResult with outcome
        """
        # Send GET request
        response = self.client.get(url)
        response.raise_for_status()

        # Validate HTML content per FR-012
        if not is_html_content(response):
            content_type = response.headers.get("content-type", "unknown")
            return DownloadResult(
                url=url,
                success=False,
                skipped=True,
                status_code=response.status_code,
                error_message=f"Non-HTML content type: {content_type}",
            )

        # Get final URL after redirects per FR-023
        final_url = str(response.url)

        # Check content size before downloading per FR-008a
        content_length = response.headers.get("content-length")
        if content_length and int(content_length) > self.config.max_file_size:
            size_mb = int(content_length) / (1024 * 1024)
            return DownloadResult(
                url=url,
                success=False,
                status_code=response.status_code,
                error_message=f"File size ({size_mb:.1f} MB) exceeds limit",
            )

        # Stream download content
        content = b""
        for chunk in response.iter_bytes(chunk_size=8192):
            content += chunk
            # Check size during streaming per FR-008a
            if len(content) > self.config.max_file_size:
                size_mb = len(content) / (1024 * 1024)
                return DownloadResult(
                    url=url,
                    success=False,
                    status_code=response.status_code,
                    error_message=f"File size ({size_mb:.1f} MB) exceeds limit during download",
                )

        # Determine file path using final URL (after redirects) per FR-023
        sanitized_path = sanitize_url_path(final_url)
        file_path = self.config.output_dir / sanitized_path

        # Write file atomically per FR-021
        self._atomic_write(file_path, content)

        return DownloadResult(
            url=url,
            success=True,
            file_path=str(file_path),
            bytes_downloaded=len(content),
            status_code=response.status_code,
        )

    def _atomic_write(self, file_path: Path, content: bytes) -> None:
        """Write content to file atomically using temp file + rename.

        Implements FR-021: atomic writes to prevent corruption.
        Implements FR-027b: auto-create parent directories.
        Implements FR-020: preserve existing files on failure.

        Args:
            file_path: Destination file path
            content: Content to write

        Raises:
            IOError: If write fails
        """
        # Create parent directories per FR-027b
        file_path.parent.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured directory exists: {file_path.parent}")

        # Write to temporary file first
        temp_fd, temp_path = tempfile.mkstemp(
            dir=file_path.parent,
            prefix=f".{file_path.name}.",
            suffix=".tmp",
        )

        try:
            # Write content to temp file
            with open(temp_fd, "wb") as f:
                f.write(content)

            # Atomically rename temp file to final destination
            Path(temp_path).replace(file_path)

        except Exception:
            # Clean up temp file on failure
            with contextlib.suppress(Exception):
                Path(temp_path).unlink(missing_ok=True)
            raise

    def _calculate_backoff(self, attempt: int) -> float:
        """Calculate exponential backoff with jitter per FR-009.

        Args:
            attempt: Attempt number (0-indexed)

        Returns:
            Backoff duration in seconds
        """
        # Exponential backoff: 1s, 2s, 4s, 8s, ...
        import random

        base_delay = 1.0
        max_delay = 32.0
        delay = min(base_delay * (2**attempt), max_delay)

        # Add jitter (±25%)
        jitter = delay * 0.25 * (random.random() * 2 - 1)
        return delay + jitter

    def close(self) -> None:
        """Close HTTP client and release resources."""
        self.client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
