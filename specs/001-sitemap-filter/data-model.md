# Data Model: Sitemap Filter CLI

**Feature**: 001-sitemap-filter  
**Date**: 2025-10-30  
**Phase**: 1 - Design

## Overview

This document defines the data structures and entities used in the sitemap filter CLI tool. Since this is a stateless CLI utility, there is no persistence layer - all entities exist only in memory during script execution.

---

## Core Entities

### URLEntry

Represents a single URL from the sitemap with associated metadata.

**Attributes**:
- `loc` (str): Full URL string (e.g., `https://help.alteryx.com/current/de/designer.html`)
- `lastmod` (str): Last modification date in ISO format YYYY-MM-DD (e.g., `2025-10-24`)
- `language` (str): Detected language code (e.g., `en`, `de`)
- `products` (list[str]): Detected product path segments (e.g., `['designer']`, `['designer', 'tools']`)

**Validation Rules**:
- `loc` MUST be a valid URL string (non-empty)
- `lastmod` MUST be ISO format or None if missing (warning logged)
- `language` detected from URL path, defaults to `en` if no locale prefix
- `products` extracted from URL path segments, empty list if no product detected

**State Transitions**: N/A (immutable once created)

**Example**:
```python
URLEntry(
    loc="https://help.alteryx.com/current/de/designer/tools.html",
    lastmod="2025-10-22",
    language="de",
    products=["designer", "tools"]
)
```

---

### FilterCriteria

Represents user-specified filtering rules from CLI arguments.

**Attributes**:
- `languages` (set[str] | None): Language codes to include (e.g., `{'en'}`, `{'de'}`)
- `products` (set[str] | None): Product path segments to include (e.g., `{'designer', 'server'}`)

**Combination Logic**:
- **None value**: No filtering on that dimension (include all)
- **AND across types**: If both languages and products specified, entry must match language AND at least one product
- **OR within type**: If multiple products specified, entry matches if it contains ANY of the products

**Validation Rules**:
- `languages` values MUST be 2-letter ISO codes (enforced by argparse choices)
- `products` values are arbitrary strings (user-defined product names)
- Empty sets treated as None (no filtering)

**Example**:
```python
# Filter for English Designer or Server docs
FilterCriteria(
    languages={'en'},
    products={'designer', 'server'}
)
```

---

### Sitemap

Represents the parsed XML sitemap structure.

**Attributes**:
- `entries` (list[URLEntry]): Collection of URL entries from sitemap
- `total_count` (int): Total number of URLs in original sitemap
- `filtered_count` (int): Number of URLs after applying filters

**Validation Rules**:
- `entries` MUST not be None (empty list if no URLs)
- `total_count` MUST equal len(entries) before filtering
- `filtered_count` MUST be <= total_count

**State Transitions**:
1. **Parsed**: Created from XML with all entries, total_count set
2. **Filtered**: After applying filters, filtered_count updated
3. **Formatted**: Converted to output format (JSON/txt/xml)

**Example**:
```python
Sitemap(
    entries=[...],  # 35460 URLEntry objects
    total_count=35460,
    filtered_count=17823  # After filtering for English only
)
```

---

## Data Structures

### OutputFormat (Enum)

Enumeration of supported output formats.

**Values**:
- `JSON`: Structured JSON array with URL and lastmod fields
- `TXT`: Plain text, one URL per line
- `XML`: Valid sitemap XML with filtered entries

**Validation Rules**:
- Enforced by argparse choices: `['json', 'txt', 'xml']`
- Default value: `JSON`

---

## Data Flow

```
1. Parse XML → List[URLEntry]
   ├─ Extract <loc> → URLEntry.loc
   ├─ Extract <lastmod> → URLEntry.lastmod
   ├─ Detect language from URL → URLEntry.language
   └─ Extract products from URL path → URLEntry.products

2. Create FilterCriteria from CLI args
   ├─ --language flags → FilterCriteria.languages
   └─ --product flags → FilterCriteria.products

3. Apply Filters → List[URLEntry]
   ├─ Language filter (if specified)
   ├─ Product filter (if specified)
   └─ Combine with AND logic

4. Format Output
   ├─ JSON: [{url, lastmod}, ...]
   ├─ TXT: url\nurl\nurl...
   └─ XML: <urlset><url><loc>...</loc><lastmod>...</lastmod></url>...</urlset>

5. Write to stdout or file
```

---

## Relationships

```
Sitemap (1) ──contains──> (*) URLEntry

FilterCriteria (1) ──applied to──> (1) Sitemap

URLEntry:
  - loc: str
  - lastmod: str
  - language: str (detected)
  - products: list[str] (extracted)

FilterCriteria:
  - languages: set[str] | None
  - products: set[str] | None

Sitemap:
  - entries: list[URLEntry]
  - total_count: int
  - filtered_count: int
```

---

## Implementation Notes

### Language Detection Logic

```python
def detect_language(url: str) -> str:
    """
    Detect language from URL path.
    Pattern: help.alteryx.com/current/{locale}/path
    If no locale found, default to 'en'
    """
    match = re.search(r'/current/([a-z]{2})/', url)
    return match.group(1) if match else 'en'
```

### Product Extraction Logic

```python
def extract_products(url: str) -> list[str]:
    """
    Extract product path segments from URL.
    Pattern: help.alteryx.com/current/{locale?}/{product}/{sub-product?}/...
    Returns list of unique product segments.
    """
    # Remove base URL and locale if present
    path = url.split('/current/')[-1]
    segments = [s for s in path.split('/') if s and s not in KNOWN_LOCALES]
    
    # Common product names (designer, server, connect, etc.)
    return [s for s in segments if s in KNOWN_PRODUCTS]
```

### Filtering Logic

```python
def apply_filters(entries: list[URLEntry], criteria: FilterCriteria) -> list[URLEntry]:
    """
    Apply filtering criteria with AND across types, OR within type.
    """
    filtered = entries
    
    # Language filter (AND)
    if criteria.languages:
        filtered = [e for e in filtered if e.language in criteria.languages]
    
    # Product filter (OR within type, AND with language)
    if criteria.products:
        filtered = [
            e for e in filtered 
            if any(product in e.products for product in criteria.products)
        ]
    
    return filtered
```

---

## Validation & Error Handling

### XML Parsing Errors
- **Malformed XML**: Exit with error message showing line number if available
- **Missing namespace**: Warning logged, continue parsing
- **Missing <loc> tag**: Skip entry with warning

### Data Validation Errors
- **Invalid lastmod format**: Warning logged, preserve original value
- **Empty URL**: Skip entry with warning
- **Unknown language code**: Use as-is (user may know custom locales)

### Filter Validation
- **No matches found**: Valid scenario, output empty result with message
- **Conflicting filters**: No validation - user may intentionally get zero results

---

## Performance Considerations

- **Memory**: ~200 bytes per URLEntry × 35,460 = ~7MB for full sitemap (well within 500MB limit)
- **Parsing**: O(n) where n = number of URLs
- **Filtering**: O(n × m) where m = average products per URL (typically 1-3)
- **Output formatting**: O(n) for filtered entries

**Estimated Performance**:
- Parse 35k URLs: ~0.5 seconds
- Filter 35k URLs: ~0.3 seconds
- Format output: ~0.2 seconds
- **Total**: ~1 second (well within 3-second requirement)

---

## Next Steps

Proceed to creating CLI interface contracts in `/contracts/` directory.
