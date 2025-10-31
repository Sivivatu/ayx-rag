"""Product filtering functionality for sitemap URLs."""

import re
from typing import List
from loguru import logger

from sitemap_filter.filters.parser import URLEntry


# Known Alteryx products from documentation structure
KNOWN_PRODUCTS = {
    'designer', 'server', 'connect', 'predictive-tools',
    'gallery', 'schedules', 'admin', 'data-sources',
    'intelligence', 'auto-insights', 'promote', 'cloud'
}


def extract_products(url: str) -> List[str]:
    """Extract product path segments from URL.
    
    Pattern: help.alteryx.com/current/{locale}/{product}/{sub-pages...}
    The first segment after locale is the main product.
    
    Args:
        url: The URL to analyze
        
    Returns:
        List containing the product name if recognized, empty list otherwise
        
    Examples:
        >>> extract_products("https://help.alteryx.com/current/en/designer.html")
        ['designer']
        >>> extract_products("https://help.alteryx.com/current/de/server/config.html")
        ['server']
        >>> extract_products("https://help.alteryx.com/current/en/release-notes.html")
        []
    """
    # Extract path after /current/{locale}/
    match = re.search(r'/current/[a-z]{2}(?:-[A-Z]{3})?/(.+)', url)
    if not match:
        return []
    
    path = match.group(1)
    
    # Split into segments and remove .html extension
    segments = [s.replace('.html', '') for s in path.split('/') if s]
    
    # First segment is typically the main product
    if segments and segments[0] in KNOWN_PRODUCTS:
        logger.debug(f"Extracted product '{segments[0]}' from URL: {url}")
        return [segments[0]]
    
    logger.debug(f"No recognized product found in URL: {url}")
    return []


def filter_by_product(entries: List[URLEntry], products: List[str]) -> List[URLEntry]:
    """Filter URL entries by product path segments.
    
    Uses OR logic: entry matches if it contains ANY of the specified products.
    Empty product list returns all entries.
    
    Args:
        entries: List of URLEntry objects to filter
        products: List of product names to filter by
        
    Returns:
        Filtered list of URLEntry objects
        
    Examples:
        >>> entries = [URLEntry(..., products=["designer"]), URLEntry(..., products=["server"])]
        >>> filter_by_product(entries, ["designer"])
        [URLEntry(..., products=["designer"])]
        >>> filter_by_product(entries, ["designer", "server"])
        [URLEntry(...), URLEntry(...)]  # Both entries
        >>> filter_by_product(entries, [])
        [URLEntry(...), URLEntry(...)]  # All entries
    """
    # Empty product list returns all entries
    if not products:
        logger.debug("No product filter specified - returning all entries")
        return entries
    
    # Filter entries that have at least one matching product (OR logic)
    filtered = [
        entry for entry in entries
        if any(product in entry.products for product in products)
    ]
    
    logger.info(f"Filtered {len(filtered)} of {len(entries)} entries for products: {products}")
    return filtered
