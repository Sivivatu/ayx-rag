"""Filter module for sitemap URLs.

Provides FilterCriteria dataclass and apply_filters function for combining
language and product filters with proper AND/OR logic.
"""

from dataclasses import dataclass
from typing import List
from loguru import logger

from sitemap_filter.filters.parser import URLEntry
from sitemap_filter.filters.language import filter_by_language
from sitemap_filter.filters.product import filter_by_product


@dataclass
class FilterCriteria:
    """Criteria for filtering sitemap URLs.
    
    Attributes:
        languages: List of language codes to filter by (OR logic within)
        products: List of product names to filter by (OR logic within)
        
    Logic:
        - Empty lists mean no filter for that dimension
        - AND logic across dimensions (language AND product)
        - OR logic within dimensions (en OR de, designer OR server)
    """
    languages: List[str]
    products: List[str]


def apply_filters(entries: List[URLEntry], criteria: FilterCriteria) -> List[URLEntry]:
    """Apply combined language and product filters to URL entries.
    
    Implements AND logic across filter types and OR logic within types:
    - Language filter: (lang1 OR lang2 OR ...)
    - Product filter: (prod1 OR prod2 OR ...)
    - Combined: (language criteria) AND (product criteria)
    
    Args:
        entries: List of URLEntry objects to filter
        criteria: FilterCriteria with languages and products
        
    Returns:
        Filtered list of URLEntry objects matching all criteria
        
    Examples:
        >>> criteria = FilterCriteria(languages=["en"], products=["designer"])
        >>> apply_filters(entries, criteria)
        [URLEntry(...)]  # Only English Designer entries
        
        >>> criteria = FilterCriteria(languages=["en", "de"], products=["designer", "server"])
        >>> apply_filters(entries, criteria)
        [URLEntry(...), ...]  # (en OR de) AND (designer OR server)
    """
    # Start with all entries
    filtered = entries
    
    # Apply language filter if specified
    if criteria.languages:
        logger.debug(f"Applying language filter: {criteria.languages}")
        filtered = filter_by_language(filtered, criteria.languages)
    
    # Apply product filter if specified (to already language-filtered results)
    if criteria.products:
        logger.debug(f"Applying product filter: {criteria.products}")
        filtered = filter_by_product(filtered, criteria.products)
    
    logger.info(
        f"Combined filters result: {len(filtered)} of {len(entries)} entries "
        f"(languages={criteria.languages or 'all'}, products={criteria.products or 'all'})"
    )
    
    return filtered


__all__ = ["FilterCriteria", "apply_filters"]
