"""Path utilities for URL path sanitization."""

import re
from urllib.parse import urlparse


def sanitize_url_path(url: str) -> str:
    """Sanitize URL path for filesystem storage.

    Converts a full URL to a filesystem-safe path by:
    1. Stripping protocol and domain
    2. Removing query parameters and fragments (FR-027d)
    3. Replacing filesystem-invalid characters with underscores (FR-005)
    4. Preserving forward slashes for directory structure
    5. Preserving Unicode characters
    6. Using 'index.html' as default for root URLs

    Args:
        url: Full URL to sanitize (e.g., "https://help.alteryx.com/current/en/tools.html")

    Returns:
        Filesystem-safe path (e.g., "current/en/tools.html")

    Examples:
        >>> sanitize_url_path("https://help.alteryx.com/current/en/designer/tools.html")
        'current/en/designer/tools.html'

        >>> sanitize_url_path("https://example.com/path/file.html?version=2024#section")
        'path/file.html'

        >>> sanitize_url_path("https://example.com/path/file:name*.html")
        'path/file_name_.html'
    """
    # Parse URL to extract path component
    try:
        parsed = urlparse(url)
        path = parsed.path
    except Exception:
        # If parsing fails, try to extract path manually
        # Remove protocol if present
        if "://" in url:
            url = url.split("://", 1)[1]
        # Remove domain (everything before first /)
        path = url.split("/", 1)[1] if "/" in url else ""

    # Remove leading slash
    if path.startswith("/"):
        path = path[1:]

    # Replace filesystem-invalid characters with underscores
    # Windows: <>:"|?*
    # Unix: \0 (null byte)
    # Note: We preserve / for directory structure
    invalid_chars = r'[<>:"|?*\x00]'
    sanitized = re.sub(invalid_chars, "_", path)

    # Use 'index.html' as default for root URLs to prevent IsADirectoryError
    if not sanitized:
        sanitized = "index.html"

    return sanitized
