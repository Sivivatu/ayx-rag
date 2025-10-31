"""Language filtering functionality for sitemap URLs."""

import re
from typing import List
from loguru import logger
from src.filters.parser import URLEntry


def detect_language(url: str) -> str:
    """Detect language from URL path.
    
    Pattern: help.alteryx.com/current/{locale}/path
    Handles both 2-letter codes (en, de) and multi-character codes (zh-CHS).
    
    Args:
        url: The URL to analyze
        
    Returns:
        Language code (e.g., 'en', 'de', 'zh-CHS')
        
    Examples:
        >>> detect_language("https://help.alteryx.com/current/en/designer.html")
        'en'
        >>> detect_language("https://help.alteryx.com/current/de/designer.html")
        'de'
        >>> detect_language("https://help.alteryx.com/current/zh-CHS/designer.html")
        'zh-CHS'
    """
    match = re.search(r'/current/([a-z]{2}(?:-[A-Z]{3})?)/', url)
    if match:
        language = match.group(1)
        logger.debug(f"Detected language '{language}' from URL: {url}")
        return language
    
    # If no locale pattern found, log warning and return empty string
    logger.warning(f"Could not detect language from URL: {url}")
    return ""


def filter_by_language(entries: List[URLEntry], languages: List[str]) -> List[URLEntry]:
    """Filter URL entries by language codes.
    
    Args:
        entries: List of URLEntry objects to filter
        languages: List of language codes to include (OR logic). Empty list returns all entries.
        
    Returns:
        Filtered list of URLEntry objects matching any of the specified languages
        
    Examples:
        >>> entries = [
        ...     URLEntry("https://help.alteryx.com/current/designer.html", "2025-10-23", "en", []),
        ...     URLEntry("https://help.alteryx.com/current/de/designer.html", "2025-10-22", "de", [])
        ... ]
        >>> filter_by_language(entries, ["en"])
        [URLEntry(..., language='en', ...)]
    """
    # If no languages specified, return all entries
    if not languages:
        logger.debug("No language filter specified, returning all entries")
        return entries
    
    # Filter entries where language matches any of the specified languages
    filtered = [entry for entry in entries if entry.language in languages]
    
    logger.info(f"Filtered {len(filtered)} of {len(entries)} entries for languages: {languages}")
    
    return filtered
