# CLI Interface Contract

**Feature**: 002-sitemap-download  
**Date**: 2025-11-03  
**Version**: 1.0.0

## Overview

This contract defines the command-line interface for the sitemap download feature. The CLI follows the project's main entry point pattern and uses typer for consistent UX.

---

## Command Structure

### Main Command

```bash
python main.py sitemap-download [OPTIONS]
```

**Description**: Download the Alteryx help sitemap from a remote URL

**Integration**: Registered in `main.py` via:
```python
from sitemap_download import app as sitemap_download_app
app.add_typer(sitemap_download_app, name="sitemap-download", help="Download Alteryx sitemap")
```

---

## Options

### `--url` (Optional)
- **Type**: `str`
- **Default**: `https://help.alteryx.com/current/sitemap.xml`
- **Description**: URL of the sitemap to download
- **Example**: `--url https://example.com/sitemap.xml`

### `--output` / `-o` (Optional)
- **Type**: `Path`
- **Default**: `alteryx-help-current-sitemap.xml` (in current directory)
- **Description**: Path where the sitemap should be saved
- **Example**: `--output data/sitemap.xml`

### `--force` / `-f` (Flag)
- **Type**: `bool`
- **Default**: `False`
- **Description**: Force download even if local file is up-to-date
- **Example**: `--force`

### `--connection-timeout` (Optional)
- **Type**: `float`
- **Default**: `30.0`
- **Description**: Connection timeout in seconds
- **Example**: `--connection-timeout 60.0`

### `--read-timeout` (Optional)
- **Type**: `float`
- **Default**: `300.0`
- **Description**: Read timeout in seconds
- **Example**: `--read-timeout 600.0`

### `--max-retries` (Optional)
- **Type**: `int`
- **Default**: `3`
- **Description**: Maximum number of retry attempts
- **Example**: `--max-retries 5`

### `--quiet` / `-q` (Flag)
- **Type**: `bool`
- **Default**: `False`
- **Description**: Suppress progress output (errors still shown)
- **Example**: `--quiet`

---

## Exit Codes

| Code | Meaning | When |
|------|---------|------|
| 0 | Success | Download and validation succeeded |
| 1 | Download Failed | Network error, timeout, or server error |
| 2 | Validation Failed | Downloaded file is not valid XML or empty |
| 3 | Configuration Error | Invalid options (bad URL, unwritable path) |

---

## Output Format

### Progress Display (Normal Mode)

```
Checking remote sitemap...
Remote file: 45.2 MB, last modified: 2025-11-03 10:30:00
Local file: 44.8 MB, last modified: 2025-11-02 15:20:00
Remote is newer, downloading...

Downloading sitemap...
[████████████████████░░░░] 78% | 35.3 MB / 45.2 MB | 5.2 MB/s | ETA: 2s

Download complete: 45.2 MB in 8.7s (5.2 MB/s)
Validating XML structure...
✓ Valid sitemap: 35,460 URLs found

Sitemap saved to: /workspaces/uv-ayx-rag/alteryx-help-current-sitemap.xml
```

### Skipped Download (Up-to-date)

```
Checking remote sitemap...
Remote file: 45.2 MB, last modified: 2025-11-02 15:20:00
Local file: 45.2 MB, last modified: 2025-11-02 15:20:00
✓ Local sitemap is up-to-date (use --force to re-download)
```

### Quiet Mode

```
✓ Sitemap downloaded: 35,460 URLs (45.2 MB)
```

### Error Display

```
✗ Download failed: Connection timeout after 30.0s
  Retried 3 times with exponential backoff
  
  Troubleshooting:
  - Check network connection
  - Try increasing --connection-timeout
  - Verify URL is accessible: https://help.alteryx.com/current/sitemap.xml
```

---

## Usage Examples

### Basic Usage (Default Settings)

```bash
# Download using all defaults
python main.py sitemap-download

# Equivalent to:
python main.py sitemap-download \
  --url https://help.alteryx.com/current/sitemap.xml \
  --output alteryx-help-current-sitemap.xml
```

### Custom Output Location

```bash
# Save to data directory
python main.py sitemap-download --output data/sitemap.xml

# Save to specific path
python main.py sitemap-download -o /tmp/alteryx-sitemap.xml
```

### Force Re-download

```bash
# Download even if local file is up-to-date
python main.py sitemap-download --force

# Short form
python main.py sitemap-download -f
```

### Custom Timeouts

```bash
# Increase timeouts for slow connections
python main.py sitemap-download \
  --connection-timeout 60 \
  --read-timeout 600
```

### Quiet Mode

```bash
# Minimal output for scripts
python main.py sitemap-download --quiet

# Combine with other options
python main.py sitemap-download -q -f -o data/sitemap.xml
```

### Different Source URL

```bash
# Download from alternative URL
python main.py sitemap-download \
  --url https://example.com/other-sitemap.xml \
  --output other-sitemap.xml
```

---

## Help Output

```bash
$ python main.py sitemap-download --help

Usage: main.py sitemap-download [OPTIONS]

  Download the Alteryx help sitemap from a remote URL with progress
  indication, validation, and incremental update support.
  
  By default, checks if the remote sitemap has been modified since the last
  download and skips downloading if unchanged. Use --force to bypass this
  check.

Options:
  --url TEXT                      URL of the sitemap to download
                                  [default: https://help.alteryx.com/current/sitemap.xml]
  --output, -o PATH              Path where the sitemap should be saved
                                  [default: alteryx-help-current-sitemap.xml]
  --force, -f                    Force download even if local file is up-to-date
  --connection-timeout FLOAT     Connection timeout in seconds [default: 30.0]
  --read-timeout FLOAT           Read timeout in seconds [default: 300.0]
  --max-retries INTEGER          Maximum number of retry attempts [default: 3]
  --quiet, -q                    Suppress progress output
  --help                         Show this message and exit.
```

---

## Implementation Signature

```python
import typer
from pathlib import Path
from typing import Optional

app = typer.Typer(name="sitemap-download")

@app.callback(invoke_without_command=True)
def download_sitemap(
    ctx: typer.Context,
    url: str = typer.Option(
        "https://help.alteryx.com/current/sitemap.xml",
        help="URL of the sitemap to download"
    ),
    output: Path = typer.Option(
        Path("alteryx-help-current-sitemap.xml"),
        "--output", "-o",
        help="Path where the sitemap should be saved"
    ),
    force: bool = typer.Option(
        False,
        "--force", "-f",
        help="Force download even if local file is up-to-date"
    ),
    connection_timeout: float = typer.Option(
        30.0,
        help="Connection timeout in seconds"
    ),
    read_timeout: float = typer.Option(
        300.0,
        help="Read timeout in seconds"
    ),
    max_retries: int = typer.Option(
        3,
        help="Maximum number of retry attempts"
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet", "-q",
        help="Suppress progress output"
    )
) -> None:
    """
    Download the Alteryx help sitemap from a remote URL with progress
    indication, validation, and incremental update support.
    
    By default, checks if the remote sitemap has been modified since the last
    download and skips downloading if unchanged. Use --force to bypass this
    check.
    """
    # Implementation delegates to downloader module
    pass
```

---

## Testing Requirements

### Unit Tests
- Verify option parsing
- Test default values
- Validate option combinations

### Integration Tests
- Test complete download workflow
- Test skip logic (up-to-date file)
- Test force download
- Test error handling and exit codes
- Test quiet mode output suppression

### User Acceptance Tests
- User can download sitemap with defaults
- User can specify custom output path
- User can force re-download
- User sees progress indication
- User receives clear error messages
