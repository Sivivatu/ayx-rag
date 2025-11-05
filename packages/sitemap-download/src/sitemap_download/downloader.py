"""HTTP downloader with progress tracking and retry logic."""

import time
import shutil
from pathlib import Path
from datetime import datetime
from typing import Callable, Optional
import httpx
from loguru import logger

from .models import (
    DownloadConfig,
    DownloadProgress,
    DownloadResult,
    RemoteFileInfo,
)
from .exceptions import ConfigurationError, NetworkError


# Type alias for progress callback
ProgressCallback = Callable[[DownloadProgress], None]

# Progress update thresholds
UPDATE_THRESHOLD_BYTES = 256 * 1024  # 256KB
UPDATE_THRESHOLD_SECONDS = 0.5  # 500ms


class SitemapDownloader:
    """Downloads files from HTTP/HTTPS URLs with progress tracking."""

    def __init__(self, config: DownloadConfig):
        """Initialize downloader with configuration.

        Args:
            config: Download configuration

        Raises:
            ConfigurationError: If configuration is invalid
        """
        self.config = config
        logger.debug(f"Initialized downloader for {config.url}")

    def check_disk_space(self, required_bytes: int) -> bool:
        """Check if sufficient disk space is available.

        Args:
            required_bytes: Number of bytes needed

        Returns:
            True if sufficient space available, False otherwise
        """
        try:
            stat = shutil.disk_usage(self.config.destination.parent)
            return stat.free >= required_bytes
        except Exception as e:
            logger.warning(f"Could not check disk space: {e}")
            return True  # Proceed anyway if check fails

    def check_remote_info(self) -> RemoteFileInfo:
        """Get metadata about remote file without downloading.

        Returns:
            RemoteFileInfo with size, last_modified, etag, content_type

        Raises:
            NetworkError: If HEAD request fails
        """
        try:
            with httpx.Client(
                timeout=httpx.Timeout(
                    connect=self.config.connection_timeout,
                    read=self.config.read_timeout,
                    write=None,
                    pool=None,
                ),
                verify=False,
            ) as client:
                response = client.head(self.config.url)
                response.raise_for_status()

                # Parse headers
                size = None
                if "content-length" in response.headers:
                    size = int(response.headers["content-length"])

                last_modified = None
                if "last-modified" in response.headers:
                    # Parse HTTP date format
                    from email.utils import parsedate_to_datetime

                    last_modified = parsedate_to_datetime(
                        response.headers["last-modified"]
                    )

                etag = response.headers.get("etag")
                content_type = response.headers.get("content-type")

                return RemoteFileInfo(
                    url=self.config.url,
                    size=size,
                    last_modified=last_modified,
                    etag=etag,
                    content_type=content_type,
                )

        except httpx.TimeoutException as e:
            raise NetworkError(f"Timeout checking remote file: {e}")
        except httpx.HTTPError as e:
            raise NetworkError(f"HTTP error checking remote file: {e}")
        except Exception as e:
            raise NetworkError(f"Error checking remote file: {e}")

    def should_download(self, remote_info: RemoteFileInfo) -> tuple[bool, str]:
        """Determine if download is needed based on local file state.

        Args:
            remote_info: Metadata from remote server

        Returns:
            Tuple of (should_download, reason)
        """
        if self.config.force:
            return True, "forced"

        if not self.config.destination.exists():
            return True, "file missing"

        if self.config.destination.stat().st_size == 0:
            return True, "local file empty"

        if remote_info.last_modified is None:
            return True, "remote modification date unknown"

        # Get local file modification time
        local_mtime = datetime.fromtimestamp(
            self.config.destination.stat().st_mtime, tz=remote_info.last_modified.tzinfo
        )

        if remote_info.last_modified > local_mtime:
            return True, "remote file is newer"

        return False, "local file is up to date"

    def download(
        self, progress_callback: Optional[ProgressCallback] = None
    ) -> DownloadResult:
        """Download file with progress tracking.

        Args:
            progress_callback: Optional callback for progress updates

        Returns:
            DownloadResult with success status and metadata
        """
        start_time = time.time()

        try:
            # Check if download needed (unless forced)
            if not self.config.force:
                try:
                    remote_info = self.check_remote_info()
                    should_dl, reason = self.should_download(remote_info)

                    if not should_dl:
                        logger.info(f"Skipping download: {reason}")
                        duration = time.time() - start_time
                        return DownloadResult.success_result(
                            file_path=self.config.destination,
                            file_size=self.config.destination.stat().st_size,
                            duration=duration,
                            skipped=True,
                            local_modified=datetime.fromtimestamp(
                                self.config.destination.stat().st_mtime
                            ),
                            remote_modified=remote_info.last_modified,
                        )

                    logger.info(f"Download needed: {reason}")
                except NetworkError as e:
                    logger.warning(f"Could not check remote info: {e}. Proceeding with download.")

            # Perform download
            logger.info(f"Downloading from {self.config.url}")

            with httpx.Client(
                timeout=httpx.Timeout(
                    connect=self.config.connection_timeout,
                    read=self.config.read_timeout,
                    write=None,
                    pool=None,
                ),
                follow_redirects=True,
                verify=False,
            ) as client:
                with client.stream("GET", self.config.url) as response:
                    response.raise_for_status()

                    # Get total size
                    total_bytes = 0
                    if "content-length" in response.headers:
                        total_bytes = int(response.headers["content-length"])

                    # Download to temporary file
                    temp_path = self.config.destination.with_suffix(".tmp")
                    downloaded_bytes = 0
                    last_update_time = time.time()
                    last_update_size = 0
                    download_start = time.time()

                    try:
                        with open(temp_path, "wb") as f:
                            for chunk in response.iter_bytes(
                                chunk_size=self.config.chunk_size
                            ):
                                f.write(chunk)
                                downloaded_bytes += len(chunk)

                                # Check if progress update needed
                                now = time.time()
                                bytes_since = downloaded_bytes - last_update_size
                                time_since = now - last_update_time

                                if (
                                    bytes_since >= UPDATE_THRESHOLD_BYTES
                                    or time_since >= UPDATE_THRESHOLD_SECONDS
                                ):
                                    if progress_callback and total_bytes > 0:
                                        bytes_per_second = (
                                            bytes_since / time_since if time_since > 0 else 0
                                        )
                                        progress = DownloadProgress(
                                            total_bytes=total_bytes,
                                            downloaded_bytes=downloaded_bytes,
                                            start_time=datetime.fromtimestamp(download_start),
                                            last_update_time=datetime.fromtimestamp(now),
                                            bytes_per_second=bytes_per_second,
                                        )
                                        progress_callback(progress)

                                    last_update_time = now
                                    last_update_size = downloaded_bytes

                        # Final progress callback
                        if progress_callback and total_bytes > 0:
                            duration = time.time() - download_start
                            progress = DownloadProgress(
                                total_bytes=total_bytes,
                                downloaded_bytes=downloaded_bytes,
                                start_time=datetime.fromtimestamp(download_start),
                                last_update_time=datetime.fromtimestamp(time.time()),
                                bytes_per_second=downloaded_bytes / duration if duration > 0 else 0,
                            )
                            progress_callback(progress)

                        # Atomic rename (preserves old file until success)
                        temp_path.replace(self.config.destination)
                        logger.info(f"Downloaded {downloaded_bytes} bytes to {self.config.destination}")

                        duration = time.time() - start_time
                        return DownloadResult.success_result(
                            file_path=self.config.destination,
                            file_size=downloaded_bytes,
                            duration=duration,
                        )

                    except Exception as e:
                        # Clean up temp file on error
                        temp_path.unlink(missing_ok=True)
                        raise

        except httpx.TimeoutException as e:
            duration = time.time() - start_time
            error_msg = f"Timeout during download: {e}"
            logger.error(error_msg)
            return DownloadResult.failure_result(error_msg, duration)

        except httpx.HTTPError as e:
            duration = time.time() - start_time
            error_msg = f"HTTP error during download: {e}"
            logger.error(error_msg)
            return DownloadResult.failure_result(error_msg, duration)

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Unexpected error during download: {e}"
            logger.error(error_msg)
            return DownloadResult.failure_result(error_msg, duration)
