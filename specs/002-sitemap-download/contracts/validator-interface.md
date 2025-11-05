# Validator Module Contract

**Feature**: 002-sitemap-download  
**Date**: 2025-11-03  
**Version**: 1.0.0

## Overview

This contract defines the interface for the validator module, which validates XML sitemap files to ensure they are well-formed and contain expected data.

---

## Module Interface

### Class: `SitemapValidator`

**Purpose**: Validates XML sitemap files using streaming SAX parser for memory efficiency

**Location**: `packages/sitemap-download/src/sitemap_download/validator.py`

---

## Public API

### `__init__()`

**Purpose**: Initialize validator (stateless, no configuration needed)

**Example**:
```python
from sitemap_download.validator import SitemapValidator

validator = SitemapValidator()
```

---

### `validate(file_path: Path) -> ValidationResult`

**Purpose**: Validate a sitemap file and count URLs

**Parameters**:
- `file_path` (`Path`): Path to sitemap XML file to validate

**Returns**: `ValidationResult` with validation status, URL count, file size, and any errors

**Validation Checks**:
1. File exists and size > 0
2. File is well-formed XML (parseable)
3. Root element is `<urlset>` or `<sitemapindex>` with proper namespace
4. Contains at least one `<url>` or `<sitemap>` entry
5. All required URL elements present (`<loc>`)

**Behavior**:
- Uses streaming SAX parser (constant memory)
- Does not load entire file into memory
- Collects validation errors with context
- Returns detailed error messages on failure

**Example**:
```python
from pathlib import Path

result = validator.validate(Path("sitemap.xml"))

if result.valid:
    print(f"✓ Valid sitemap: {result.url_count} URLs")
    print(f"  File size: {result.file_size} bytes")
    print(f"  Validation time: {result.validation_duration:.2f}s")
else:
    print(f"✗ Invalid sitemap: {result.error_message}")
```

---

### `validate_content(content: str) -> ValidationResult`

**Purpose**: Validate XML content from string (for testing)

**Parameters**:
- `content` (`str`): XML content to validate

**Returns**: `ValidationResult` with validation status and details

**Example**:
```python
xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://example.com/page1</loc>
        <lastmod>2025-11-03</lastmod>
    </url>
</urlset>"""

result = validator.validate_content(xml_content)
assert result.valid
assert result.url_count == 1
```

---

## Implementation Details

### SAX Handler

**Purpose**: Stream-process XML without loading into memory

**Implementation**:
```python
import xml.sax
from xml.sax.handler import ContentHandler

class SitemapContentHandler(ContentHandler):
    """SAX handler for streaming sitemap validation."""
    
    def __init__(self):
        super().__init__()
        self.url_count = 0
        self.sitemap_count = 0
        self.current_element = []
        self.has_urlset = False
        self.has_sitemapindex = False
        self.errors = []
        self.in_url = False
        self.current_url_has_loc = False
    
    def startElement(self, name, attrs):
        self.current_element.append(name)
        
        if name == 'urlset':
            self.has_urlset = True
            # Check namespace
            if 'xmlns' not in attrs:
                self.errors.append("Missing xmlns attribute on <urlset>")
        
        elif name == 'sitemapindex':
            self.has_sitemapindex = True
            if 'xmlns' not in attrs:
                self.errors.append("Missing xmlns attribute on <sitemapindex>")
        
        elif name == 'url':
            self.in_url = True
            self.current_url_has_loc = False
        
        elif name == 'sitemap':
            self.sitemap_count += 1
        
        elif name == 'loc' and self.in_url:
            self.current_url_has_loc = True
    
    def endElement(self, name):
        if name == 'url':
            if self.current_url_has_loc:
                self.url_count += 1
            else:
                self.errors.append(f"URL #{self.url_count + 1} missing <loc> element")
            self.in_url = False
        
        self.current_element.pop()
    
    def get_result(self, file_size: int, duration: float) -> ValidationResult:
        """Generate validation result from parsed data."""
        
        # Check root element
        if not self.has_urlset and not self.has_sitemapindex:
            return ValidationResult.invalid_result(
                "Root element must be <urlset> or <sitemapindex>",
                file_size,
                duration
            )
        
        # Check for content
        total_entries = self.url_count + self.sitemap_count
        if total_entries == 0:
            return ValidationResult.invalid_result(
                "Sitemap contains no URL or sitemap entries",
                file_size,
                duration
            )
        
        # Check for errors
        if self.errors:
            return ValidationResult.invalid_result(
                f"Validation errors: {'; '.join(self.errors[:3])}",
                file_size,
                duration
            )
        
        # Success
        return ValidationResult.valid_result(
            url_count=self.url_count,
            file_size=file_size,
            duration=duration
        )
```

---

### Validation Flow

```python
def validate(self, file_path: Path) -> ValidationResult:
    """Validate sitemap file."""
    start_time = time.time()
    
    try:
        # Check file exists
        if not file_path.exists():
            return ValidationResult.invalid_result(
                f"File not found: {file_path}",
                0,
                time.time() - start_time
            )
        
        # Check file size
        file_size = file_path.stat().st_size
        if file_size == 0:
            return ValidationResult.invalid_result(
                "File is empty",
                0,
                time.time() - start_time
            )
        
        # Parse with SAX (streaming)
        handler = SitemapContentHandler()
        parser = xml.sax.make_parser()
        parser.setContentHandler(handler)
        
        try:
            parser.parse(str(file_path))
        except xml.sax.SAXParseException as e:
            return ValidationResult.invalid_result(
                f"XML parse error at line {e.getLineNumber()}: {e.getMessage()}",
                file_size,
                time.time() - start_time
            )
        
        # Generate result from handler
        duration = time.time() - start_time
        return handler.get_result(file_size, duration)
        
    except Exception as e:
        return ValidationResult.invalid_result(
            f"Validation error: {str(e)}",
            file_path.stat().st_size if file_path.exists() else 0,
            time.time() - start_time
        )
```

---

## Validation Rules

### 1. File Structure
- File must exist and be readable
- File size must be > 0 bytes
- File must be well-formed XML

### 2. Root Element
- Must be `<urlset>` OR `<sitemapindex>`
- Must include `xmlns` attribute with sitemap namespace
- Valid namespace: `http://www.sitemaps.org/schemas/sitemap/0.9`

### 3. URL Entries
- Each `<url>` must contain `<loc>` element
- `<loc>` must be non-empty
- Optional: `<lastmod>`, `<changefreq>`, `<priority>`

### 4. Sitemap Index Entries
- Each `<sitemap>` must contain `<loc>` element
- Optional: `<lastmod>`

### 5. Content
- Must contain at least one `<url>` or `<sitemap>` entry
- Empty sitemaps are invalid

---

## Error Messages

### File Errors
- `"File not found: {path}"` - File doesn't exist
- `"File is empty"` - File size is 0 bytes
- `"Permission denied: {path}"` - Can't read file

### XML Errors
- `"XML parse error at line {line}: {message}"` - Malformed XML
- `"Root element must be <urlset> or <sitemapindex>"` - Invalid root
- `"Missing xmlns attribute on <{element}>"` - Missing namespace

### Content Errors
- `"Sitemap contains no URL or sitemap entries"` - Empty sitemap
- `"URL #{n} missing <loc> element"` - Invalid URL entry
- `"Sitemap #{n} missing <loc> element"` - Invalid sitemap entry

---

## Testing Requirements

### Unit Tests

**Test: `test_validate_valid_urlset`**
- Create valid sitemap with URLs
- Verify result.valid = True
- Check url_count matches expected

**Test: `test_validate_valid_sitemapindex`**
- Create valid sitemap index
- Verify result.valid = True
- Check sitemap_count matches expected

**Test: `test_validate_empty_file`**
- Create 0-byte file
- Verify result.valid = False
- Check error message mentions empty file

**Test: `test_validate_malformed_xml`**
- Create file with unclosed tags
- Verify result.valid = False
- Check error mentions parse error with line number

**Test: `test_validate_missing_namespace`**
- Create sitemap without xmlns
- Verify result.valid = False
- Check error mentions missing xmlns

**Test: `test_validate_invalid_root_element`**
- Create XML with wrong root element
- Verify result.valid = False
- Check error mentions root element

**Test: `test_validate_no_urls`**
- Create sitemap with valid structure but no URLs
- Verify result.valid = False
- Check error mentions no entries

**Test: `test_validate_url_missing_loc`**
- Create URL entry without <loc>
- Verify result.valid = False
- Check error mentions missing loc

**Test: `test_validate_file_not_found`**
- Pass non-existent file path
- Verify result.valid = False
- Check error mentions file not found

**Test: `test_validate_large_file_memory_usage`**
- Create sitemap with 100k+ URLs
- Validate and monitor memory usage
- Verify memory stays under 10MB threshold

**Test: `test_validate_content_string`**
- Pass XML as string
- Verify validation works correctly
- Useful for testing without file I/O

### Integration Tests

**Test: `test_validate_real_alteryx_sitemap`**
- Download actual Alteryx sitemap
- Validate it
- Verify passes validation
- Check URL count is reasonable (30k-40k)

---

## Performance Targets

| File Size | URL Count | Validation Time | Memory Usage |
|-----------|-----------|-----------------|--------------|
| 1 MB | 1,000 | <0.5s | <5 MB |
| 10 MB | 10,000 | <2s | <8 MB |
| 50 MB | 50,000 | <8s | <10 MB |
| 100 MB | 100,000 | <15s | <10 MB |

**Note**: Times are approximate and depend on CPU speed. Memory should remain constant regardless of file size due to streaming parser.

---

## Dependencies

```python
import xml.sax
from xml.sax.handler import ContentHandler
from xml.sax import SAXParseException
from pathlib import Path
import time
from typing import Optional
from loguru import logger

from .models import ValidationResult, ValidationError
```

---

## Logging

All validation operations should be logged:

```python
# Success
logger.info(
    "Sitemap validation successful",
    file_path=str(file_path),
    url_count=result.url_count,
    file_size=result.file_size,
    duration_seconds=result.validation_duration
)

# Failure
logger.warning(
    "Sitemap validation failed",
    file_path=str(file_path),
    error=result.error_message,
    file_size=result.file_size,
    duration_seconds=result.validation_duration
)
```
