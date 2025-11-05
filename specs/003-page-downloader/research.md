# Technical Research: Page Downloader

**Feature**: 003-page-downloader  
**Date**: 2025-11-05  
**Purpose**: Document technology choices, patterns, and best practices for implementation

## Research Areas

### 1. HTTP Client Library

**Decision**: Use `httpx>=0.25.0` (already in sitemap-download)

**Rationale**:
- Already proven in sitemap-download package for sitemap downloads
- Excellent streaming support for large files with memory efficiency
- Built-in retry capabilities and timeout control
- Strong SSL/TLS certificate validation by default
- Clean async/sync API (we'll use sync for sequential processing)
- HTTP/2 support for future optimization
- Comprehensive exception hierarchy for error handling

**Alternatives Considered**:
- `requests`: Mature but lacks HTTP/2, less efficient streaming, no native async
- `urllib3`: Lower-level, more complex API, less user-friendly for our use case
- `aiohttp`: Async-first which complicates sequential processing requirement

**Implementation Notes**:
- Use `httpx.Client()` context manager for connection pooling
- Configure timeouts: `httpx.Timeout(connect=30.0, read=300.0)`
- Enable strict SSL: `verify=True` (default)
- Stream downloads with `client.stream('GET', url)`
- Chunk size: 8192 bytes (same as sitemap-download)

### 2. robots.txt Parsing

**Decision**: Use `urllib.robotparser` (Python stdlib)

**Rationale**:
- Part of Python standard library (no external dependency)
- Simple API: `RobotFileParser.can_fetch(user_agent, url)`
- Handles standard robots.txt directives
- Sufficient for our use case (single domain: help.alteryx.com)
- Zero configuration required

**Alternatives Considered**:
- `robotexclusionrulesparser`: More features (crawl-delay, wildcards) but external dependency
- `reppy`: Fast C++ implementation but overkill for single-domain use case
- Manual parsing: Error-prone and doesn't handle edge cases

**Implementation Notes**:
```python
from urllib.robotparser import RobotFileParser

rp = RobotFileParser()
rp.set_url("https://help.alteryx.com/robots.txt")
rp.read()  # Fetches and parses

if rp.can_fetch("*", url):
    # Proceed with download
else:
    # Skip with warning
```

**Caching Strategy**: Parse robots.txt once per session, cache in memory

### 3. Path Sanitization

**Decision**: Custom sanitization function with `pathlib` and character replacement

**Rationale**:
- Need cross-platform compatibility (Windows, Linux, macOS)
- Preserve URL structure for human readability
- Handle edge cases: query params, fragments, percent-encoding
- Avoid reserved filesystem names (CON, PRN, etc. on Windows)

**Pattern**:
```python
from pathlib import Path
from urllib.parse import urlparse, unquote
import re

def sanitize_url_path(url: str, output_dir: Path) -> Path:
    """Convert URL to filesystem path, sanitizing invalid characters."""
    parsed = urlparse(url)
    
    # Extract path component, remove leading slash
    path = unquote(parsed.path).lstrip('/')
    
    # Replace invalid characters
    # Windows: <>:"|?*
    # Unix: (none strictly, but / is path separator)
    invalid_chars = r'[<>:"|?*]'
    path = re.sub(invalid_chars, '_', path)
    
    # Handle empty path (root URL)
    if not path or path == '/':
        path = 'index.html'
    
    # Ensure .html extension if missing
    if not path.endswith('.html'):
        path += '.html'
    
    return output_dir / path
```

**Edge Cases Handled**:
- Query parameters: `tools.html?id=123` → `tools.html` (ignore params)
- Fragments: `tools.html#section` → `tools.html` (ignore fragments)
- Percent-encoding: `%20` → space
- Reserved names: Check against Windows reserved list (CON, PRN, AUX, etc.)
- Path traversal: Reject paths with `..`

### 4. Progress Tracking

**Decision**: Use `rich.progress` for terminal progress bars

**Rationale**:
- Modern, attractive progress display with minimal code
- Integrates well with loguru for combined progress + logging
- Supports multiple progress bars (current file + overall batch)
- Shows real-time metrics: speed, ETA, percentage
- Doesn't interfere with stderr logging

**Alternatives Considered**:
- `tqdm`: Popular but less visually polished, harder to integrate with loguru
- `click.progressbar`: Too basic, limited customization
- Custom implementation: Reinventing the wheel

**Implementation Pattern**:
```python
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    TaskProgressColumn(),
    TextColumn("{task.completed}/{task.total}"),
) as progress:
    task = progress.add_task("Downloading pages", total=len(urls))
    
    for url in urls:
        # Download logic
        progress.update(task, advance=1, description=f"Downloading {url}")
```

**Dependency**: Add `rich>=13.0.0` to package dependencies

### 5. Atomic Write Implementation

**Decision**: Reuse pattern from sitemap-download (`tempfile` + `os.replace`)

**Rationale**:
- Proven pattern already in codebase (sitemap-download)
- Atomic on POSIX systems (Linux, macOS)
- Crash-safe: incomplete downloads don't corrupt existing files
- Simple implementation with stdlib only

**Pattern** (from sitemap-download):
```python
import tempfile
import os
from pathlib import Path

def atomic_write(content: bytes, dest_path: Path):
    """Write content to dest_path atomically."""
    # Ensure parent directory exists
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write to temp file in same directory (same filesystem)
    with tempfile.NamedTemporaryFile(
        mode='wb',
        dir=dest_path.parent,
        delete=False
    ) as tmp_file:
        tmp_file.write(content)
        tmp_path = Path(tmp_file.name)
    
    # Atomic rename
    os.replace(tmp_path, dest_path)
```

### 6. HTML Validation

**Decision**: Content-Type header check only (per spec assumptions)

**Rationale**:
- Spec FR-012: "validate that downloaded content is HTML (check Content-Type header)"
- Assumptions state: "HTML content validation is based on Content-Type header, not parsing"
- Sufficient for catching misrouted requests (PDFs, JSON, etc.)
- Avoids expensive parsing overhead for 8,864 URLs
- Parsing/cleaning deferred to 004-page-processor feature

**Implementation**:
```python
def is_html_content(response: httpx.Response) -> bool:
    """Check if response contains HTML based on Content-Type header."""
    content_type = response.headers.get('content-type', '').lower()
    return 'text/html' in content_type or 'application/xhtml' in content_type
```

**Note**: If Content-Type is missing or incorrect, log warning but proceed (some servers misconfigure headers)

### 7. CLI Design Patterns

**Decision**: Follow typer patterns from sitemap-filter and sitemap-download

**Consistent Pattern**:
- Required positional argument for URL input (file or single URL)
- Optional flags with `--` prefix and sensible defaults
- Help text for all parameters using typer annotations
- Exit codes: 0 (success), 1 (download failures), 2 (validation failures), 3 (config error)

**CLI Structure**:
```python
import typer
from pathlib import Path
from typing import Optional

app = typer.Typer(
    name="page-downloader",
    help="Download HTML pages from Alteryx documentation URLs",
)

@app.command()
def download(
    url_source: str = typer.Argument(..., help="URL list file or single URL"),
    output_dir: Path = typer.Option("data/html", "--output-dir", "-o", help="Output directory for HTML files"),
    delay: float = typer.Option(0.5, "--delay", help="Delay between requests (seconds)"),
    max_file_size: int = typer.Option(5, "--max-file-size", help="Maximum file size in MB"),
    force: bool = typer.Option(False, "--force", help="Force re-download all pages"),
    ignore_robots: bool = typer.Option(False, "--ignore-robots-txt", help="Skip robots.txt checking"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview downloads without executing"),
):
    """Download pages from URL list or single URL."""
    # Implementation
```

**Integration with main.py**:
```python
# In page_downloader/__init__.py
from .cli import app

__all__ = ["app"]

# In main.py
from page_downloader import app as page_downloader_app

main_app.add_typer(page_downloader_app, name="page-downloader")
```

### 8. Testing Strategy

**Decision**: Use `respx` for httpx mocking

**Rationale**:
- Purpose-built for httpx (better than generic mocking)
- Easy to mock specific URLs, status codes, headers, timeouts
- Supports pattern matching for URL variations
- Clean syntax for test setup

**Test Structure**:
```python
import respx
import httpx
import pytest

@respx.mock
def test_download_single_page():
    # Mock HTTP response
    respx.get("https://help.alteryx.com/current/en/designer.html").mock(
        return_value=httpx.Response(
            200,
            headers={"content-type": "text/html"},
            content=b"<html>...</html>"
        )
    )
    
    # Test download
    result = download_page("https://help.alteryx.com/current/en/designer.html")
    assert result.status == "success"
```

**Fixtures Needed**:
- `fixtures/sample_pages/valid.html`: Well-formed HTML
- `fixtures/sample_pages/large.html`: >5MB for size limit testing
- `fixtures/robots.txt`: Various robots.txt configurations
- `fixtures/url_lists/sample.txt`: Test URL list inputs

**Test Coverage Goals**:
- Unit tests: >95% coverage (matching sitemap-download)
- Integration tests: CLI end-to-end with mocked HTTP
- Contract tests: main.py integration
- Performance tests: Verify rate limiting variance <10%

**Dependency**: Add `respx>=0.20.0` to dev dependencies

### 9. Error Handling Patterns

**Decision**: Reuse retry logic from sitemap-download with enhancements for 429

**Retry Strategy** (from sitemap-download):
```python
import random
import httpx

def calculate_retry_delay(attempt: int, base_delay: float = 1.0) -> float:
    """Calculate exponential backoff with jitter."""
    delay = base_delay * (2 ** attempt)
    jitter = delay * 0.25 * random.random()
    return delay + jitter

def is_retryable(error: Exception) -> bool:
    """Determine if error should trigger retry."""
    if isinstance(error, httpx.TimeoutException):
        return True
    if isinstance(error, httpx.ConnectError):
        return True
    if isinstance(error, httpx.HTTPStatusError):
        status = error.response.status_code
        # 5xx or 429 are retryable
        return status >= 500 or status == 429
    return False

def get_retry_after(response: httpx.Response) -> Optional[float]:
    """Extract Retry-After header value in seconds."""
    retry_after = response.headers.get('retry-after')
    if retry_after:
        try:
            return float(retry_after)
        except ValueError:
            # Could be HTTP date format, parse if needed
            pass
    return None
```

**Enhanced for 429**:
```python
def calculate_429_delay(response: httpx.Response, attempt: int) -> float:
    """Calculate delay for 429 responses, respecting Retry-After."""
    retry_after = get_retry_after(response)
    if retry_after:
        return retry_after
    # No Retry-After: use 2x normal backoff
    return calculate_retry_delay(attempt, base_delay=2.0)
```

**Exception Hierarchy**:
```python
class DownloadError(Exception):
    """Base exception for download errors."""
    pass

class ValidationError(DownloadError):
    """Content validation failed."""
    pass

class RobotsDeniedError(DownloadError):
    """robots.txt denied access to URL."""
    pass

class FileSizeLimitError(DownloadError):
    """Downloaded file exceeded size limit."""
    pass
```

### 10. Configuration Management

**Decision**: Use dataclasses for configuration models

**Rationale**:
- Part of Python stdlib (no external dependency)
- Type hints provide validation and IDE support
- Simpler than Pydantic for this use case
- Matches pattern from sitemap-download

**Models** (detailed in data-model.md):
```python
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass
class DownloadConfig:
    """Configuration for download session."""
    output_dir: Path
    delay: float = 0.5
    max_file_size_mb: int = 5
    connect_timeout: float = 30.0
    read_timeout: float = 300.0
    max_retries: int = 3
    force: bool = False
    ignore_robots: bool = False
    dry_run: bool = False
    user_agent: str = "uv-ayx-rag-page-downloader/0.1.0"
```

**Validation**: Implement `__post_init__` for validation logic

## Dependencies Summary

**Production Dependencies** (add to `packages/page-downloader/pyproject.toml`):
```toml
dependencies = [
    "httpx>=0.25.0",     # HTTP client (already in sitemap-download)
    "rich>=13.0.0",      # Progress bars and terminal UI
]
```

**Workspace-Level Dependencies** (already available):
- `typer>=0.20.0` (CLI framework)
- `loguru>=0.7.3` (structured logging)

**Development Dependencies** (add to dev group):
```toml
[dependency-groups]
dev = [
    "pytest>=8.4.2",
    "pytest-cov>=7.0.0",
    "respx>=0.20.0",     # httpx mocking
]
```

**No Dependencies Needed**:
- `urllib.robotparser` (stdlib)
- `pathlib` (stdlib)
- `tempfile` (stdlib)
- `dataclasses` (stdlib)

## Reusable Patterns from sitemap-download

**To Reuse**:
1. Retry logic with exponential backoff + jitter
2. Atomic write pattern (tempfile + os.replace)
3. Progress tracking structure
4. Error exception hierarchy
5. httpx client configuration
6. Timeout handling
7. Exit code patterns

**To Adapt**:
1. Streaming for HTML files (8KB chunks) vs XML
2. Content-Type validation vs XML schema validation
3. Batch processing of multiple URLs vs single sitemap
4. Path sanitization for nested directories vs single file

## Technical Risks & Mitigation

| Risk | Mitigation |
|------|-----------|
| **Rate limiting by help.alteryx.com** | Configurable delay (default 0.5s conservative), respect 429 + Retry-After, robots.txt compliance |
| **Large memory usage for 8,864 URLs** | Stream downloads (8KB chunks), process sequentially, atomic writes prevent memory bloat |
| **Network instability** | Retry logic (3 attempts default), continue-on-error for batch, progress persistence |
| **Path collisions** | Sanitization prevents conflicts, preserve URL structure reduces collision likelihood |
| **SSL certificate issues** | Strict validation prevents MITM, clear error messages for expired certs |
| **Disk space exhaustion** | 5MB file size limit (configurable), check available space before batch (future enhancement) |

## Performance Considerations

**Expected Performance**:
- Single page: <5s (SC-001)
- 100 pages @ 0.5s delay: ~95s including download time (SC-002 target: <120s)
- Rate limiting variance: <10% (SC-008) - achieved via time.sleep precision

**Optimization Opportunities** (future):
- Concurrent downloads (requires architecture change from clarification Q1)
- HTTP/2 connection pooling (already supported by httpx)
- Compression negotiation (Accept-Encoding: gzip)
- Conditional requests (If-Modified-Since for incremental)

**Not Optimizing Yet**:
- Parallel downloads (clarification decision: sequential only)
- Async I/O (sequential processing simpler)
- Database for progress (filesystem sufficient for MVP)

## Integration Points

**Inputs**:
- URL list from sitemap-filter: Plain text file, one URL per line
- Single URL: Command-line argument for ad-hoc downloads

**Outputs**:
- HTML files: `{output_dir}/{url_path}` (e.g., `data/html/en/designer/tools.html`)
- Log files: Structured JSON logs to stderr (loguru)
- Summary statistics: JSON or text report to stdout

**Integration with 004-page-processor**:
- Page-processor will read HTML files from same `data/html/` directory
- Preserve Last-Modified timestamps as file mtime for incremental processing
- Metadata (URL, download timestamp) in filename or sidecar JSON (TBD in 004)

## Next Steps

1. **Phase 1**: Create data-model.md with entity definitions
2. **Phase 1**: Create contracts/cli-interface.md with CLI specification
3. **Phase 1**: Create quickstart.md with developer guide
4. **Phase 1**: Update agent context with new technologies
5. **Phase 2**: Generate tasks.md with implementation breakdown (via `/speckit.tasks`)
