"""XML sitemap parser module."""

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import List
from loguru import logger


@dataclass
class URLEntry:
    """Represents a single URL entry from the sitemap.
    
    Attributes:
        loc: Full URL string
        lastmod: Last modification date in ISO format (YYYY-MM-DD)
        language: Detected language code (e.g., 'en', 'de')
        products: List of detected product path segments
    """
    loc: str
    lastmod: str
    language: str = ""
    products: List[str] = field(default_factory=list)


def detect_language(url: str) -> str:
    """Detect language from URL path.
    
    Pattern: help.alteryx.com/current/{locale}/path
    If no locale found, default to 'en'
    
    Args:
        url: The URL to analyze
        
    Returns:
        Language code (e.g., 'en', 'de')
    """
    match = re.search(r'/current/([a-z]{2})/', url)
    return match.group(1) if match else 'en'


def extract_products(url: str) -> List[str]:
    """Extract product path segments from URL.
    
    Pattern: help.alteryx.com/current/{locale?}/{product}/{sub-product?}/...
    Returns list of product segments.
    
    Args:
        url: The URL to analyze
        
    Returns:
        List of product path segments
    """
    # Known product names from Alteryx documentation structure
    KNOWN_PRODUCTS = {
        'designer', 'server', 'connect', 'predictive-tools',
        'gallery', 'schedules', 'admin', 'data-sources'
    }
    
    # Remove base URL and extract path
    path = url.split('/current/')[-1]
    
    # Split into segments and filter
    segments = [s for s in path.split('/') if s and s.endswith('.html') == False]
    
    # Remove known locale codes
    KNOWN_LOCALES = {'en', 'de', 'fr', 'es', 'ja', 'pt'}
    segments = [s for s in segments if s not in KNOWN_LOCALES]
    
    # Filter to known product names
    products = [s for s in segments if s in KNOWN_PRODUCTS]
    
    return products


def parse_sitemap(file_path: Path) -> List[URLEntry]:
    """Parse XML sitemap and return list of URL entries.
    
    Args:
        file_path: Path to the XML sitemap file
        
    Returns:
        List of URLEntry objects
        
    Raises:
        FileNotFoundError: If sitemap file doesn't exist
        ET.ParseError: If XML is malformed
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Sitemap file not found: {file_path}")
    
    logger.info(f"Parsing sitemap: {file_path}")
    
    # Parse XML
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # Handle namespace
    namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    
    entries = []
    url_elements = root.findall('ns:url', namespace)
    
    logger.debug(f"Found {len(url_elements)} URL elements in sitemap")
    
    for url_elem in url_elements:
        # Extract loc and lastmod
        loc_elem = url_elem.find('ns:loc', namespace)
        lastmod_elem = url_elem.find('ns:lastmod', namespace)
        
        # Skip if loc is missing or empty
        if loc_elem is None or not loc_elem.text:
            logger.warning("Skipping URL entry with missing or empty <loc> tag")
            continue
        
        loc = loc_elem.text
        lastmod = lastmod_elem.text if lastmod_elem is not None and lastmod_elem.text else ""
        
        # Detect language and extract products
        language = detect_language(loc)
        products = extract_products(loc)
        
        entry = URLEntry(
            loc=loc,
            lastmod=lastmod,
            language=language,
            products=products
        )
        entries.append(entry)
    
    logger.info(f"Parsed {len(entries)} URL entries from sitemap")
    
    return entries
