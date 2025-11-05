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
from .cli import app

__version__ = "0.1.0"

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
    # CLI
    "app",
]
