# CLI Interface Contract: Page Downloader

**Feature**: 003-page-downloader  
**Date**: 2025-11-05  
**Purpose**: Define command-line interface specification for page-downloader

## Overview

The page-downloader CLI provides commands for downloading HTML pages from Alteryx documentation URLs. It integrates with the main.py dispatcher and follows typer conventions established in sitemap-filter and sitemap-download.

## Command Structure

### Main Command Entry

**Invocation via main.py**:
```bash
python main.py page-downloader [OPTIONS] URL_SOURCE
```

**Alternative** (direct package invocation for testing):
```bash
uv run python -m page_downloader [OPTIONS] URL_SOURCE
```

### Command: `download` (default)

Downloads HTML pages from a URL list file or single URL.

#### Synopsis

```bash
python main.py page-downloader [OPTIONS] URL_SOURCE
```

#### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `URL_SOURCE` | `str` | Yes | Path to URL list file (.txt) or single HTTP/HTTPS URL |

#### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--output-dir` | `-o` | `Path` | `data/html` | Output directory for downloaded HTML files |
| `--delay` | `-d` | `float` | `0.5` | Delay between requests in seconds |
| `--max-file-size` | `-m` | `int` | `5` | Maximum file size in MB |
| `--connect-timeout` | | `float` | `30.0` | Connection timeout in seconds |
| `--read-timeout` | | `float` | `300.0` | Read timeout in seconds |
| `--max-retries` | `-r` | `int` | `3` | Maximum retry attempts for failed downloads |
| `--force` | `-f` | `flag` | `False` | Force re-download all pages (ignore Last-Modified) |
| `--ignore-robots-txt` | | `flag` | `False` | Skip robots.txt checking |
| `--dry-run` | | `flag` | `False` | Preview downloads without executing |
| `--verbose` | `-v` | `flag` | `False` | Enable verbose logging |
| `--quiet` | `-q` | `flag` | `False` | Suppress progress output (logs only) |
| `--output-format` | | `str` | `text` | Summary output format: `text`, `json` |

#### Exit Codes

| Code | Meaning | When |
|------|---------|------|
| `0` | Success | All downloads completed successfully or all skipped |
| `1` | Partial failure | Some downloads failed but others succeeded |
| `2` | Validation failure | Input validation failed (invalid URL, file not found, etc.) |
| `3` | Configuration error | Invalid configuration (negative timeout, bad output dir, etc.) |

## Usage Examples

### Example 1: Download from URL List

Download all pages from a sitemap-filter output file:

```bash
python main.py page-downloader designer-urls.txt \
  --output-dir data/html \
  --delay 0.5
```

**Input file format** (`designer-urls.txt`):
```text
https://help.alteryx.com/current/en/designer.html
https://help.alteryx.com/current/en/designer/tools.html
https://help.alteryx.com/current/en/designer/workflows.html
```

**Expected behavior**:
- Reads URLs from file (one per line)
- Downloads sequentially with 0.5s delay between requests
- Saves to `data/html/en/designer.html`, `data/html/en/designer/tools.html`, etc.
- Shows progress bar with X/Y completed
- Prints summary statistics on completion

### Example 2: Download Single Page

Download a single documentation page:

```bash
python main.py page-downloader \
  https://help.alteryx.com/current/en/designer/tools.html \
  --output-dir data/html
```

**Expected behavior**:
- Detects single URL (no file read)
- Downloads immediately
- Saves to `data/html/en/designer/tools.html`
- Prints single-line success message

### Example 3: Incremental Update

Re-download only changed pages:

```bash
python main.py page-downloader designer-urls.txt \
  --output-dir data/html \
  --delay 0.5
```

**Expected behavior**:
- Checks Last-Modified header for each URL
- Skips pages where local file is newer or same age
- Only downloads changed/new pages
- Reports: "Downloaded: 15, Skipped: 50, Failed: 0"

### Example 4: Force Full Refresh

Force re-download all pages ignoring timestamps:

```bash
python main.py page-downloader designer-urls.txt \
  --output-dir data/html \
  --force
```

**Expected behavior**:
- Skips Last-Modified comparison
- Downloads all pages regardless of local file age
- Overwrites existing files

### Example 5: Dry Run

Preview what would be downloaded:

```bash
python main.py page-downloader designer-urls.txt \
  --dry-run
```

**Expected output**:
```
[DRY RUN] Would download 654 URLs to data/html/
[DRY RUN] https://help.alteryx.com/current/en/designer.html → data/html/en/designer.html
[DRY RUN] https://help.alteryx.com/current/en/designer/tools.html → data/html/en/designer/tools.html
...
[DRY RUN] Summary: 654 URLs, estimated size: ~3.2 GB, estimated time: ~5.5 minutes
```

### Example 6: Ignore robots.txt

Download pages even if blocked by robots.txt:

```bash
python main.py page-downloader designer-urls.txt \
  --ignore-robots-txt
```

**Expected behavior**:
- Skips robots.txt checking
- Downloads all URLs without robots.txt validation
- Useful for testing or when explicit permission obtained

### Example 7: Custom File Size Limit

Download with 10MB file size limit:

```bash
python main.py page-downloader designer-urls.txt \
  --max-file-size 10
```

**Expected behavior**:
- Aborts downloads if Content-Length > 10MB
- Logs error for oversized files
- Continues with remaining URLs

### Example 8: JSON Output

Get machine-readable summary:

```bash
python main.py page-downloader designer-urls.txt \
  --output-format json
```

**Expected JSON output**:
```json
{
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "start_time": "2025-11-05T10:30:00Z",
  "end_time": "2025-11-05T10:35:30Z",
  "duration_seconds": 330,
  "total_urls": 654,
  "successful": 650,
  "failed": 2,
  "skipped": 2,
  "total_bytes": 3200000000,
  "average_speed_mbps": 9.7,
  "failed_urls": [
    {
      "url": "https://help.alteryx.com/current/en/missing.html",
      "error": "HTTP 404: Not Found"
    },
    {
      "url": "https://help.alteryx.com/current/en/timeout.html",
      "error": "Connection timeout after 3 retries"
    }
  ]
}
```

## Output Behavior

### Progress Display (Default)

```
Downloading pages: 45/654 [━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━] 7% 0:05:30
Current: https://help.alteryx.com/current/en/designer/tools.html
Status: ✓ 43 successful, ✗ 2 failed, ⊘ 0 skipped
```

### Text Summary (Default)

```
Download Summary
================
Total URLs:      654
Successful:      650 (99.4%)
Failed:          2 (0.3%)
Skipped:         2 (0.3%)
Total Size:      3.2 GB
Duration:        5m 30s
Average Speed:   9.7 MB/s

Failed URLs:
  - https://help.alteryx.com/current/en/missing.html (HTTP 404)
  - https://help.alteryx.com/current/en/timeout.html (Connection timeout)
```

### Quiet Mode

```bash
python main.py page-downloader designer-urls.txt --quiet
```

**Behavior**:
- Suppresses progress bar
- Only logs to stderr (structured JSON logs)
- Prints summary at end

### Verbose Mode

```bash
python main.py page-downloader designer-urls.txt --verbose
```

**Behavior**:
- Shows progress bar
- Logs each download attempt (URL, status, size, duration)
- Shows retry attempts
- Displays robots.txt check results
- Prints detailed summary

## Integration with main.py

### Registration

In `main.py`:
```python
from page_downloader import app as page_downloader_app

main_app = typer.Typer(name="uv-ayx-rag")
main_app.add_typer(page_downloader_app, name="page-downloader")
```

### Help Integration

```bash
$ python main.py --help
Usage: main.py [OPTIONS] COMMAND [ARGS]...

  uv-ayx-rag: RAG system for Alteryx documentation

Commands:
  sitemap-download  Download Alteryx sitemap
  sitemap-filter    Filter sitemap URLs by language/product
  page-downloader   Download HTML pages from URLs
```

```bash
$ python main.py page-downloader --help
Usage: main.py page-downloader [OPTIONS] URL_SOURCE

  Download HTML pages from Alteryx documentation URLs.

  URL_SOURCE can be:
    - Path to text file with one URL per line
    - Single HTTP/HTTPS URL

Arguments:
  URL_SOURCE  [required]  URL list file or single URL

Options:
  -o, --output-dir PATH         Output directory [default: data/html]
  -d, --delay FLOAT             Delay between requests (seconds) [default: 0.5]
  -m, --max-file-size INTEGER   Max file size in MB [default: 5]
  --connect-timeout FLOAT       Connection timeout (seconds) [default: 30.0]
  --read-timeout FLOAT          Read timeout (seconds) [default: 300.0]
  -r, --max-retries INTEGER     Max retry attempts [default: 3]
  -f, --force                   Force re-download all pages
  --ignore-robots-txt           Skip robots.txt checking
  --dry-run                     Preview without downloading
  -v, --verbose                 Enable verbose logging
  -q, --quiet                   Suppress progress output
  --output-format [text|json]   Summary output format [default: text]
  --help                        Show this message and exit
```

## Error Handling

### Input Validation Errors

**File not found**:
```
Error: URL list file not found: designer-urls.txt
Exit code: 2
```

**Invalid URL in file**:
```
Error: Invalid URL on line 45: htp://invalid-url
Exit code: 2
```

**Empty URL list**:
```
Error: URL list file is empty: designer-urls.txt
Exit code: 2
```

### Network Errors

**Connection timeout**:
```
[ERROR] https://help.alteryx.com/current/en/page.html
  Connection timeout after 30.0s (attempt 1/3)
  Retrying in 1.5s...
```

**HTTP errors**:
```
[ERROR] https://help.alteryx.com/current/en/missing.html
  HTTP 404: Not Found (non-retryable)
  Skipping to next URL
```

**Rate limiting**:
```
[WARN] https://help.alteryx.com/current/en/page.html
  HTTP 429: Too Many Requests
  Retry-After: 30s (attempt 1/3)
  Waiting 30.0s before retry...
```

### Validation Errors

**robots.txt denied**:
```
[WARN] https://help.alteryx.com/restricted/page.html
  Blocked by robots.txt
  Status: Skipped
```

**File too large**:
```
[ERROR] https://help.alteryx.com/current/en/huge.html
  File size 12.5 MB exceeds limit of 5.0 MB
  Status: Failed
```

**Non-HTML content**:
```
[ERROR] https://help.alteryx.com/current/en/document.pdf
  Content-Type: application/pdf (expected text/html)
  Status: Skipped
```

### Configuration Errors

**Invalid output directory**:
```
Error: Output directory is not writable: /invalid/path
Exit code: 3
```

**Invalid timeout**:
```
Error: connect_timeout must be > 0, got: -5.0
Exit code: 3
```

## Logging

### Structured Logs (stderr)

All operational logs go to stderr in JSON format via loguru:

```json
{"timestamp": "2025-11-05T10:30:15Z", "level": "INFO", "module": "downloader", "message": "Starting download session", "session_id": "a1b2c3d4", "total_urls": 654}
{"timestamp": "2025-11-05T10:30:16Z", "level": "INFO", "module": "downloader", "message": "Downloaded page", "url": "https://help.alteryx.com/current/en/designer.html", "status": 200, "size_bytes": 45678, "duration_ms": 234}
{"timestamp": "2025-11-05T10:30:18Z", "level": "ERROR", "module": "downloader", "message": "Download failed", "url": "https://help.alteryx.com/current/en/missing.html", "error": "HTTP 404", "retry_count": 0}
```

### Log Levels

- **DEBUG** (`--verbose`): Individual HTTP requests, retry attempts, robots.txt checks
- **INFO** (default): Download progress, summaries, successful completions
- **WARN**: Skipped URLs, robots.txt blocks, retries
- **ERROR**: Failed downloads, validation failures, timeouts

## Testing Contract

### Unit Test Example

```python
def test_cli_single_url(tmp_path):
    """Test downloading a single URL."""
    result = runner.invoke(app, [
        "https://example.com/page.html",
        "--output-dir", str(tmp_path),
        "--dry-run"
    ])
    assert result.exit_code == 0
    assert "Would download 1 URL" in result.stdout
```

### Integration Test Example

```python
@respx.mock
def test_cli_batch_download(tmp_path, url_list_file):
    """Test batch download from URL list."""
    # Mock HTTP responses
    respx.get("https://example.com/page1.html").mock(
        return_value=httpx.Response(200, content=b"<html>Page 1</html>")
    )
    
    result = runner.invoke(app, [
        str(url_list_file),
        "--output-dir", str(tmp_path),
    ])
    
    assert result.exit_code == 0
    assert (tmp_path / "page1.html").exists()
```

## Performance Guarantees

| Metric | Target | Contract |
|--------|--------|----------|
| Single page download | <5s | SC-001 from spec |
| 100 pages @ 0.5s delay | <2 minutes | SC-002 from spec |
| Rate limiting variance | <10% | SC-008 from spec |
| Incremental savings | >80% time reduction | SC-004 from spec |

## Backward Compatibility

**Version 0.1.0** (initial release):
- Initial CLI interface
- No backward compatibility concerns

**Future versions**:
- New optional flags may be added without breaking changes
- Required arguments will not change position
- Exit codes will remain stable
- JSON output schema will use versioning if changed

## Summary

The page-downloader CLI provides a consistent, user-friendly interface for downloading Alteryx documentation HTML pages. It follows project conventions, integrates seamlessly with main.py, provides comprehensive error handling, and supports both interactive and scripted workflows through flexible output options.
