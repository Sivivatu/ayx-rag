"""Sitemap Download package for Alteryx help documentation."""

from .cli import app
from .downloader import SitemapDownloader
from .exceptions import (
    ConfigurationError,
    NetworkError,
    SitemapDownloadError,
    ValidationError,
)
from .models import (
    DownloadConfig,
    DownloadProgress,
    DownloadResult,
    RemoteFileInfo,
    ValidationResult,
)
from .utils import archive_file, format_bytes
from .validator import SitemapValidator

__version__ = "0.2.0"

__all__ = [
    # Exceptions
    "SitemapDownloadError",
    "NetworkError",
    "ValidationError",
    "ConfigurationError",
    # Models
    "DownloadConfig",
    "DownloadProgress",
    "DownloadResult",
    "ValidationResult",
    "RemoteFileInfo",
    # Downloader
    "SitemapDownloader",
    # Validator
    "SitemapValidator",
    # CLI
    "app",
    # Utils
    "archive_file",
    "format_bytes",
]
