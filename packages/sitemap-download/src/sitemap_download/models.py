"""Data models for sitemap download operations."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class DownloadConfig:
    """Configuration for a download operation."""

    url: str
    destination: Path
    force: bool = False
    connection_timeout: float = 30.0
    read_timeout: float = 300.0
    max_retries: int = 3
    chunk_size: int = 8192

    def __post_init__(self):
        """Validate configuration parameters."""
        if not self.url.startswith(("http://", "https://")):
            raise ValueError(f"Invalid URL scheme: {self.url}")
        if self.connection_timeout <= 0:
            raise ValueError(f"connection_timeout must be > 0, got {self.connection_timeout}")
        if self.read_timeout <= 0:
            raise ValueError(f"read_timeout must be > 0, got {self.read_timeout}")
        if self.max_retries < 0:
            raise ValueError(f"max_retries must be >= 0, got {self.max_retries}")
        if self.chunk_size <= 0:
            raise ValueError(f"chunk_size must be > 0, got {self.chunk_size}")


@dataclass
class DownloadProgress:
    """Tracks real-time download progress."""

    total_bytes: int
    downloaded_bytes: int
    start_time: datetime
    last_update_time: datetime
    bytes_per_second: float

    @property
    def percentage(self) -> float:
        """Progress as percentage (0-100)."""
        if self.total_bytes == 0:
            return 0.0
        return (self.downloaded_bytes / self.total_bytes) * 100

    @property
    def eta_seconds(self) -> float:
        """Estimated time to completion in seconds."""
        if self.bytes_per_second == 0:
            return float("inf")
        remaining = self.total_bytes - self.downloaded_bytes
        return remaining / self.bytes_per_second

    @property
    def elapsed_seconds(self) -> float:
        """Time elapsed since start in seconds."""
        return (datetime.now() - self.start_time).total_seconds()


@dataclass
class DownloadResult:
    """Final outcome of a download operation."""

    success: bool
    file_path: Path | None
    file_size: int | None
    duration_seconds: float
    error_message: str | None
    retry_count: int
    skipped: bool
    remote_modified: datetime | None = None
    local_modified: datetime | None = None
    validation_result: "ValidationResult | None" = None

    @staticmethod
    def success_result(
        file_path: Path,
        file_size: int,
        duration: float,
        retry_count: int = 0,
        skipped: bool = False,
        remote_modified: datetime | None = None,
        local_modified: datetime | None = None,
        validation_result: "ValidationResult | None" = None,
    ) -> "DownloadResult":
        """Create a successful download result."""
        return DownloadResult(
            success=True,
            file_path=file_path,
            file_size=file_size,
            duration_seconds=duration,
            error_message=None,
            retry_count=retry_count,
            skipped=skipped,
            remote_modified=remote_modified,
            local_modified=local_modified,
            validation_result=validation_result,
        )

    @staticmethod
    def failure_result(error: str, duration: float, retry_count: int = 0) -> "DownloadResult":
        """Create a failed download result."""
        return DownloadResult(
            success=False,
            file_path=None,
            file_size=None,
            duration_seconds=duration,
            error_message=error,
            retry_count=retry_count,
            skipped=False,
        )


@dataclass
class ValidationResult:
    """Result of XML sitemap validation."""

    valid: bool
    url_count: int | None
    file_size: int
    error_message: str | None
    validation_duration: float

    @staticmethod
    def valid_result(url_count: int, file_size: int, duration: float) -> "ValidationResult":
        """Create a successful validation result."""
        return ValidationResult(
            valid=True,
            url_count=url_count,
            file_size=file_size,
            error_message=None,
            validation_duration=duration,
        )

    @staticmethod
    def invalid_result(error: str, file_size: int, duration: float) -> "ValidationResult":
        """Create a failed validation result."""
        return ValidationResult(
            valid=False,
            url_count=None,
            file_size=file_size,
            error_message=error,
            validation_duration=duration,
        )


@dataclass
class RemoteFileInfo:
    """Metadata about remote file without downloading."""

    url: str
    size: int | None
    last_modified: datetime | None
    etag: str | None
    content_type: str | None

    @property
    def has_size(self) -> bool:
        """Check if size information is available."""
        return self.size is not None

    @property
    def has_last_modified(self) -> bool:
        """Check if last modified date is available."""
        return self.last_modified is not None

    @property
    def has_etag(self) -> bool:
        """Check if ETag is available."""
        return self.etag is not None
