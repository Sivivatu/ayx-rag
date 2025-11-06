"""Custom exceptions for page-downloader package."""


class PageDownloaderError(Exception):
    """Base exception for all page-downloader errors."""

    pass


class DownloadError(PageDownloaderError):
    """Raised when a page download fails (HTTP errors, timeouts, connection issues)."""

    def __init__(self, url: str, message: str):
        """Initialize with URL and error message.
        
        Args:
            url: The URL that failed to download
            message: Description of the error
        """
        self.url = url
        self.message = message
        super().__init__(f"Failed to download {url}: {message}")


class ValidationError(PageDownloaderError):
    """Raised when input validation fails (invalid URLs, file paths, configs)."""

    pass


class RobotsDeniedError(PageDownloaderError):
    """Raised when robots.txt denies access to a URL."""

    def __init__(self, url: str):
        """Initialize with denied URL.
        
        Args:
            url: The URL denied by robots.txt
        """
        self.url = url
        super().__init__(f"Access denied by robots.txt: {url}")


class ConfigurationError(PageDownloaderError):
    """Raised when configuration is invalid or incomplete."""

    pass
