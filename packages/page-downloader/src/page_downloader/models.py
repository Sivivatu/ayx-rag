"""Data models for page-downloader package."""

from dataclasses import dataclass
from pathlib import Path

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
