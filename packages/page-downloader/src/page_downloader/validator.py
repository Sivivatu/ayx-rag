"""Content validation utilities for page-downloader."""

from httpx import Response


def is_html_content(response: Response) -> bool:
    """Check if HTTP response contains HTML content.
    
    Validates content type per FR-012 by checking the Content-Type header.
    Only accepts:
    - text/html (with optional charset and other parameters)
    - application/xhtml+xml (with optional parameters)
    
    Args:
        response: httpx.Response object to validate
        
    Returns:
        True if response contains HTML content, False otherwise
        
    Examples:
        >>> response = Response(200, headers={"content-type": "text/html"})
        >>> is_html_content(response)
        True
        
        >>> response = Response(200, headers={"content-type": "application/pdf"})
        >>> is_html_content(response)
        False
    """
    # Get Content-Type header (case-insensitive)
    content_type = response.headers.get("content-type", "")
    
    if not content_type:
        return False
    
    # Extract media type (part before semicolon) and normalize
    # Example: "text/html; charset=utf-8" -> "text/html"
    media_type = content_type.split(";")[0].strip().lower()
    
    # Check if media type is HTML
    # Accept: text/html or application/xhtml+xml
    return media_type in ("text/html", "application/xhtml+xml")
