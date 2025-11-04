# Quickstart: Sitemap Download

**Feature**: 002-sitemap-download  
**Date**: 2025-11-03  
**Version**: 1.0.0

## Overview

The sitemap download feature enables you to download the Alteryx help documentation sitemap with progress tracking, automatic validation, and smart incremental updates. This guide gets you started in under 5 minutes.

---

## Installation

### 1. Ensure uv is Installed

The project uses `uv` for package management.

```bash
# Check if uv is installed
uv --version

# If not installed, install it
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Sync Dependencies

```bash
# From project root
cd /workspaces/uv-ayx-rag
uv sync
```

This installs the sitemap-download package and all its dependencies (httpx, typer, loguru).

---

## Quick Start

### Basic Download

Download the Alteryx sitemap with default settings:

```bash
python main.py sitemap-download
```

**What happens**:
1. Checks if remote sitemap has changed
2. Downloads if newer (or if local doesn't exist)
3. Shows progress bar
4. Validates downloaded XML
5. Reports URL count and file size

**Output**:
```
Checking remote sitemap...
Remote file: 45.2 MB, last modified: 2025-11-03 10:30:00
Downloading...

[████████████████████████] 100% | 45.2 MB / 45.2 MB | 5.2 MB/s | Done

Download complete: 45.2 MB in 8.7s (5.2 MB/s)
Validating XML structure...
✓ Valid sitemap: 35,460 URLs found

Sitemap saved to: /workspaces/uv-ayx-rag/alteryx-help-current-sitemap.xml
```

---

## Common Use Cases

### Download to Custom Location

Save the sitemap to a specific directory:

```bash
# Save to data directory
python main.py sitemap-download --output data/sitemap.xml

# Save with short option
python main.py sitemap-download -o data/my-sitemap.xml
```

### Force Re-download

Download even if the local file is up-to-date:

```bash
python main.py sitemap-download --force

# Short form
python main.py sitemap-download -f
```

**Use when**:
- You suspect the local file is corrupted
- You want to verify the remote content
- You're testing the download feature

### Quiet Mode for Scripts

Suppress progress output (useful in automated scripts):

```bash
python main.py sitemap-download --quiet

# Or use short form
python main.py sitemap-download -q
```

**Output** (quiet mode):
```
✓ Sitemap downloaded: 35,460 URLs (45.2 MB)
```

### Adjust Timeouts for Slow Connections

Increase timeouts if you have a slow or unreliable connection:

```bash
python main.py sitemap-download \
  --connection-timeout 60 \
  --read-timeout 600
```

**Default timeouts**:
- Connection: 30 seconds
- Read: 300 seconds (5 minutes)

---

## Understanding the Output

### Successful Download

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

**Key information**:
- File size and modification dates
- Progress bar with percentage and ETA
- Download speed in MB/s
- Validation result with URL count
- Final file location

### Skipped Download (Up-to-date)

```
Checking remote sitemap...
Remote file: 45.2 MB, last modified: 2025-11-02 15:20:00
Local file: 45.2 MB, last modified: 2025-11-02 15:20:00
✓ Local sitemap is up-to-date (use --force to re-download)
```

**What this means**:
- Your local file has the same modification date as remote
- No download is needed (saves bandwidth and time)
- Use `--force` if you want to download anyway

### Failed Download

```
✗ Download failed: Connection timeout after 30.0s
  Retried 3 times with exponential backoff
  
  Troubleshooting:
  - Check network connection
  - Try increasing --connection-timeout
  - Verify URL is accessible: https://help.alteryx.com/current/sitemap.xml
```

**What to do**:
1. Check your internet connection
2. Try again (temporary network glitch)
3. Increase timeout with `--connection-timeout 60`
4. Check if URL is accessible in browser

---

## Exit Codes

Use exit codes in scripts to handle different outcomes:

| Code | Meaning | Example Use |
|------|---------|-------------|
| 0 | Success | Continue processing sitemap |
| 1 | Download failed | Retry later or alert user |
| 2 | Validation failed | Check file integrity |
| 3 | Configuration error | Fix command options |

**Bash script example**:
```bash
#!/bin/bash

python main.py sitemap-download --quiet
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "Success! Processing sitemap..."
    # Continue with next steps
elif [ $EXIT_CODE -eq 1 ]; then
    echo "Download failed, retrying in 5 minutes..."
    sleep 300
    python main.py sitemap-download --quiet
else
    echo "Error: Check configuration"
    exit 1
fi
```

---

## Integration Examples

### Daily Automated Update

Cron job to check for sitemap updates daily:

```bash
# crontab -e
# Run at 2 AM every day
0 2 * * * cd /workspaces/uv-ayx-rag && python main.py sitemap-download -q
```

### Python Script Integration

Use programmatically in Python:

```python
from pathlib import Path
from sitemap_download.downloader import SitemapDownloader
from sitemap_download.validator import SitemapValidator
from sitemap_download.models import DownloadConfig

# Configure download
config = DownloadConfig(
    url="https://help.alteryx.com/current/sitemap.xml",
    destination=Path("data/sitemap.xml"),
    force=False
)

# Download
downloader = SitemapDownloader(config)
result = downloader.download()

if result.success:
    print(f"Downloaded: {result.file_path}")
    
    # Validate
    validator = SitemapValidator()
    validation = validator.validate(result.file_path)
    
    if validation.valid:
        print(f"Valid sitemap with {validation.url_count} URLs")
    else:
        print(f"Validation failed: {validation.error_message}")
else:
    print(f"Download failed: {result.error_message}")
```

### Pipeline Integration

Combine with sitemap-filter for targeted downloads:

```bash
# 1. Download latest sitemap
python main.py sitemap-download -q

# 2. Filter for English documentation
python main.py sitemap-filter \
  alteryx-help-current-sitemap.xml \
  --language en \
  --output en-urls.txt \
  --format text

# 3. Process filtered URLs
# ... (future scraper feature)
```

---

## Troubleshooting

### Problem: "Connection timeout after 30.0s"

**Cause**: Network is slow or unreliable

**Solution**:
```bash
python main.py sitemap-download --connection-timeout 60
```

### Problem: "Read timeout after 300.0s"

**Cause**: File is large and download is slow

**Solution**:
```bash
python main.py sitemap-download --read-timeout 600
```

### Problem: "Validation failed: XML parse error"

**Cause**: Downloaded file is corrupted

**Solution**:
1. Delete the local file: `rm alteryx-help-current-sitemap.xml`
2. Try downloading again: `python main.py sitemap-download --force`

### Problem: "Permission denied"

**Cause**: No write permission to destination

**Solution**:
```bash
# Save to writable location
python main.py sitemap-download --output ~/data/sitemap.xml

# Or fix permissions
chmod +w alteryx-help-current-sitemap.xml
```

### Problem: Downloads every time despite no changes

**Cause**: Remote server doesn't provide Last-Modified header

**Solution**: This is expected behavior for safety. If you want to skip repeated downloads, check the file age yourself:

```bash
# Only download if file is older than 1 day
if [ ! -f sitemap.xml ] || [ $(find sitemap.xml -mtime +1) ]; then
    python main.py sitemap-download
else
    echo "Sitemap is recent, skipping"
fi
```

---

## Next Steps

After downloading the sitemap:

1. **Filter URLs**: Use `sitemap-filter` to extract specific languages or products
   ```bash
   python main.py sitemap-filter sitemap.xml --language en --format text
   ```

2. **Inspect the sitemap**: View URL structure and metadata
   ```bash
   head -n 50 alteryx-help-current-sitemap.xml
   ```

3. **Count URLs**: Quick check of sitemap size
   ```bash
   grep -c "<loc>" alteryx-help-current-sitemap.xml
   ```

4. **Future features**: Web scraping, content extraction, embedding generation

---

## Command Reference

```bash
# Help
python main.py sitemap-download --help

# Basic download
python main.py sitemap-download

# Custom output
python main.py sitemap-download --output PATH

# Force re-download
python main.py sitemap-download --force

# Quiet mode
python main.py sitemap-download --quiet

# Custom timeouts
python main.py sitemap-download \
  --connection-timeout SECONDS \
  --read-timeout SECONDS

# Custom retry count
python main.py sitemap-download --max-retries N

# All options
python main.py sitemap-download \
  --url URL \
  --output PATH \
  --force \
  --connection-timeout 60 \
  --read-timeout 600 \
  --max-retries 5 \
  --quiet
```

---

## Getting Help

- **Command help**: `python main.py sitemap-download --help`
- **Project docs**: See `/specs/002-sitemap-download/spec.md`
- **Issues**: Check if local file exists and has proper permissions
- **Validation**: Manually check XML with `xmllint sitemap.xml`
