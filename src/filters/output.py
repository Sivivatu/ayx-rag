"""Output formatting functionality for filtered sitemap URLs."""

import xml.etree.ElementTree as ET
from typing import List, Dict, Any
from loguru import logger

from src.filters.parser import URLEntry


def format_json(entries: List[URLEntry], total_count: int) -> Dict[str, Any]:
    """Format URL entries as JSON structure.
    
    Args:
        entries: List of filtered URLEntry objects
        total_count: Total number of URLs before filtering
        
    Returns:
        Dictionary with total_urls, filtered_urls, and results array
        
    Example:
        >>> entries = [URLEntry(...)]
        >>> format_json(entries, 100)
        {
            "total_urls": 100,
            "filtered_urls": 1,
            "results": [
                {"url": "https://...", "lastmod": "2025-10-23"}
            ]
        }
    """
    logger.debug(f"Formatting {len(entries)} entries as JSON")
    
    return {
        "total_urls": total_count,
        "filtered_urls": len(entries),
        "results": [
            {
                "url": entry.loc,
                "lastmod": entry.lastmod
            }
            for entry in entries
        ]
    }


def format_txt(entries: List[URLEntry]) -> str:
    """Format URL entries as plain text (one URL per line).
    
    Args:
        entries: List of filtered URLEntry objects
        
    Returns:
        String with one URL per line, newline-terminated
        
    Example:
        >>> entries = [URLEntry("https://example.com", ...)]
        >>> format_txt(entries)
        'https://example.com\\n'
    """
    logger.debug(f"Formatting {len(entries)} entries as plain text")
    
    if not entries:
        return ""
    
    return '\n'.join(entry.loc for entry in entries) + '\n'


def format_xml(entries: List[URLEntry]) -> str:
    """Format URL entries as XML sitemap.
    
    Args:
        entries: List of filtered URLEntry objects
        
    Returns:
        Valid XML sitemap string with declaration
        
    Example:
        >>> entries = [URLEntry(...)]
        >>> format_xml(entries)
        '<?xml version="1.0" encoding="UTF-8"?>\\n<urlset ...>...</urlset>'
    """
    logger.debug(f"Formatting {len(entries)} entries as XML sitemap")
    
    # Create root element with sitemap namespace
    namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
    ET.register_namespace('', namespace)
    
    urlset = ET.Element("{%s}urlset" % namespace)
    
    # Add URL entries
    for entry in entries:
        url_elem = ET.SubElement(urlset, "{%s}url" % namespace)
        
        loc_elem = ET.SubElement(url_elem, "{%s}loc" % namespace)
        loc_elem.text = entry.loc
        
        lastmod_elem = ET.SubElement(url_elem, "{%s}lastmod" % namespace)
        lastmod_elem.text = entry.lastmod
    
    # Convert to string with XML declaration
    xml_str = ET.tostring(urlset, encoding='unicode', method='xml')
    
    return f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_str}'
