"""Exception classes for sitemap download operations."""


class SitemapDownloadError(Exception):
    """Base exception for all sitemap download errors.
    
    All custom exceptions in the sitemap-download package inherit from this class.
    This allows catching all sitemap-download-specific errors with a single except clause.
    """

    pass


class NetworkError(SitemapDownloadError):
    """Network-related errors (timeouts, connection failures, HTTP errors).
    
    Raised when network operations fail, including:
    - Connection timeouts
    - Connection failures
    - HTTP status errors (4xx, 5xx)
    - DNS resolution failures
    """

    pass


class ValidationError(SitemapDownloadError):
    """XML validation or file integrity errors.
    
    Raised when sitemap content validation fails, including:
    - Invalid XML syntax
    - Missing required elements (urlset, loc)
    - Empty or malformed sitemap files
    """

    pass


class ConfigurationError(SitemapDownloadError):
    """Configuration or setup errors (invalid paths, permissions, etc).
    
    Raised when configuration parameters are invalid, including:
    - Invalid URL schemes
    - Invalid timeout or retry values
    - Invalid file paths or permissions
    - Insufficient disk space
    """

    pass
