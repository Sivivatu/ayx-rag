"""Exception classes for sitemap download operations."""


class SitemapDownloadError(Exception):
    """Base exception for all sitemap download errors."""

    pass


class NetworkError(SitemapDownloadError):
    """Network-related errors (timeouts, connection failures, HTTP errors)."""

    pass


class ValidationError(SitemapDownloadError):
    """XML validation or file integrity errors."""

    pass


class ConfigurationError(SitemapDownloadError):
    """Configuration or setup errors (invalid paths, permissions, etc)."""

    pass
