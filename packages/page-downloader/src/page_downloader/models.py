"""Data models for page-downloader package."""

from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter

from .exceptions import ConfigurationError, ValidationError


@dataclass
class DownloadConfig:
    """Configuration for page download operations.

    Attributes:
        output_dir: Base directory for saving downloaded pages
        rate_limit: Delay in seconds between consecutive requests (default: 0.5)
        connection_timeout: Connection timeout in seconds (default: 30)
        read_timeout: Read timeout in seconds (default: 300)
        max_retries: Maximum retry attempts for failed downloads (default: 3)
        max_file_size: Maximum file size in bytes (default: 5MB)
        force: Force re-download even if files exist (default: False)
        dry_run: Preview mode without actual downloads (default: False)
        ignore_robots: Bypass robots.txt checking (default: False)
        verify_ssl: Verify SSL certificates (default: True, disable for dev/testing)
        user_agent: Custom User-Agent header (default: Python/httpx)
    """

    output_dir: Path
    rate_limit: float = 0.5
    connection_timeout: float = 30.0
    read_timeout: float = 300.0
    max_retries: int = 3
    max_file_size: int = 5 * 1024 * 1024  # 5MB in bytes
    force: bool = False
    dry_run: bool = False
    ignore_robots: bool = False
    verify_ssl: bool = True
    user_agent: str = "uv-ayx-rag-page-downloader/0.1.0 (Python/httpx)"

    def __post_init__(self):
        """Validate configuration after initialization."""
        self._validate()

    def _validate(self):
        """Validate configuration values.

        Raises:
            ValidationError: If any configuration value is invalid
            ConfigurationError: If output directory cannot be created
        """
        # Validate rate_limit
        if self.rate_limit < 0:
            raise ValidationError("rate_limit must be non-negative")

        # Validate timeouts
        if self.connection_timeout <= 0:
            raise ValidationError("connection_timeout must be positive")
        if self.read_timeout <= 0:
            raise ValidationError("read_timeout must be positive")

        # Validate max_retries
        if self.max_retries < 0:
            raise ValidationError("max_retries must be non-negative")

        # Validate max_file_size
        if self.max_file_size <= 0:
            raise ValidationError("max_file_size must be positive")

        # Validate output_dir
        if not isinstance(self.output_dir, Path):
            self.output_dir = Path(self.output_dir)

        # Try to create output_dir if it doesn't exist (per FR-027b)
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise ConfigurationError(f"Cannot create output directory {self.output_dir}: {e}")

        # Check write permissions
        if not self.output_dir.exists() or not self.output_dir.is_dir():
            raise ConfigurationError(
                f"Output directory does not exist or is not a directory: {self.output_dir}"
            )


@dataclass
class URLList:
    """Represents a parsed list of URLs from a text file (FR-001, FR-027a).

    Attributes:
        source: Path to the original text file containing URLs
        urls: List of validated http/https URLs (comments/blank lines removed)
        valid_count: Number of valid URLs parsed
        invalid_count: Number of invalid/malformed URL lines skipped

    Parsing Rules:
        - One URL per line
        - Lines starting with '#' are comments and ignored
        - Blank or whitespace-only lines are ignored
        - Leading/trailing whitespace around URLs is stripped
        - Malformed URLs (missing scheme or host) are skipped and counted
        - Only http and https schemes are accepted
    """

    source: Path
    urls: list[str]
    valid_count: int
    invalid_count: int

    @classmethod
    def from_file(cls, path: Path) -> URLList:
        """Parse a text file into a URLList instance.

        Args:
            path: Path to input file containing one URL per line.

        Returns:
            URLList instance with parsed URLs and counts.

        Raises:
            ValidationError: If the path does not exist or is not a file.
        """
        from urllib.parse import urlparse

        if not path.exists() or not path.is_file():
            raise ValidationError(f"URL list file not found: {path}")

        raw_lines = path.read_text(encoding="utf-8").splitlines()
        urls: list[str] = []
        invalid_count = 0

        for _line_number, raw in enumerate(raw_lines, start=1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue  # Skip comments and blank lines

            parsed = urlparse(line)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                # Count invalid/malformed URL per FR-027a
                invalid_count += 1
                continue

            urls.append(line)

        return cls(source=path, urls=urls, valid_count=len(urls), invalid_count=invalid_count)

    def __iter__(self):  # Convenience for iteration in callers
        return iter(self.urls)

    def __len__(self):  # Length passthrough
        return len(self.urls)


@dataclass
class DownloadSession:
    """Accumulates statistics for a batch download session (FR-018).

    Tracks counts and timing to produce summary metrics after processing
    a list of URLs sequentially.

    Usage:
        session = DownloadSession(total=len(urls))
        session.start()
        for url in urls:
            # ... perform download, get result object or status
            session.record(success=True, bytes_downloaded=12345, skipped=False)
        session.finish()

    Attributes:
        total: Total URLs intended for processing
        started_at: Monotonic timestamp when session started
        finished_at: Monotonic timestamp when session finished
        success_count: Number of successful downloads
        failure_count: Number of failed downloads
        skipped_count: Number of skipped URLs (unchanged or invalid type)
        bytes_downloaded: Total bytes successfully written
    """

    total: int
    started_at: float | None = None
    finished_at: float | None = None
    success_count: int = 0
    failure_count: int = 0
    skipped_count: int = 0
    bytes_downloaded: int = 0
    _in_progress: bool = field(default=False, repr=False)

    def start(self) -> None:
        if self._in_progress:
            return
        self.started_at = perf_counter()
        self._in_progress = True

    def record(self, *, success: bool, skipped: bool = False, bytes_downloaded: int = 0) -> None:
        """Record outcome of a single URL processing operation.

        Args:
            success: True if download succeeded.
            skipped: True if URL was intentionally skipped.
            bytes_downloaded: Number of bytes written for this URL (only counted when success True).
        """
        if skipped:
            self.skipped_count += 1
            return

        if success:
            self.success_count += 1
            if bytes_downloaded > 0:
                self.bytes_downloaded += bytes_downloaded
        else:
            self.failure_count += 1

    def finish(self) -> None:
        if not self._in_progress:
            return
        self.finished_at = perf_counter()
        self._in_progress = False

    # Derived metrics -------------------------------------------------
    @property
    def duration(self) -> float:
        if self.started_at is None:
            return 0.0
        end = self.finished_at if self.finished_at is not None else perf_counter()
        return end - self.started_at

    @property
    def processed(self) -> int:
        return self.success_count + self.failure_count + self.skipped_count

    @property
    def remaining(self) -> int:
        return max(self.total - self.processed, 0)

    @property
    def success_rate(self) -> float:
        if self.processed == 0:
            return 0.0
        return self.success_count / self.processed

    @property
    def average_bytes_per_second(self) -> float:
        d = self.duration
        if d <= 0:
            return 0.0
        return self.bytes_downloaded / d

    def summary(self) -> dict:
        """Return dictionary summary for reporting/logging (FR-018)."""
        return {
            "total": self.total,
            "processed": self.processed,
            "success": self.success_count,
            "failed": self.failure_count,
            "skipped": self.skipped_count,
            "bytes_downloaded": self.bytes_downloaded,
            "duration_sec": round(self.duration, 3),
            "avg_bytes_per_sec": round(self.average_bytes_per_second, 2),
            "success_rate": round(self.success_rate, 3),
            "remaining": self.remaining,
        }
