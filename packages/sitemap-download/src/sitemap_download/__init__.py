"""Sitemap Download package for Alteryx help documentation."""

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
from .downloader import SitemapDownloader
from .validator import SitemapValidator
from .cli import app
from .utils import archive_file, format_bytes

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
