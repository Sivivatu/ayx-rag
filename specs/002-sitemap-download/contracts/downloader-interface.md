# Downloader Module Contract

**Feature**: 002-sitemap-download  
**Date**: 2025-11-03  
**Version**: 1.0.0

## Overview

This contract defines the interface for the downloader module, which handles HTTP file downloads with progress tracking, retry logic, and modification date checking.

---

## Module Interface

### Class: `SitemapDownloader`

**Purpose**: Downloads files from HTTP/HTTPS URLs with robust error handling and progress tracking

**Location**: `packages/sitemap-download/src/sitemap_download/downloader.py`

---

## Public API

### `__init__(config: DownloadConfig)`

**Purpose**: Initialize downloader with configuration

**Parameters**:
- `config` (`DownloadConfig`): Download configuration including URL, destination, timeouts

**Raises**:
- `ConfigurationError`: If config is invalid

**Example**:
```python
from sitemap_download.downloader import SitemapDownloader
from sitemap_download.models import DownloadConfig
from pathlib import Path

config = DownloadConfig(
    url="https://help.alteryx.com/current/sitemap.xml",
    destination=Path("sitemap.xml"),
    force=False
)
downloader = SitemapDownloader(config)
```

---

### `check_remote_info() -> RemoteFileInfo`

**Purpose**: Get metadata about remote file without downloading (HTTP HEAD request)

**Returns**: `RemoteFileInfo` with size, last_modified, etag, content_type

**Raises**:
- `NetworkError`: If HEAD request fails
- `TimeoutError`: If request times out

**Example**:
```python
info = downloader.check_remote_info()
print(f"Remote size: {info.size} bytes")
print(f"Last modified: {info.last_modified}")
print(f"Content type: {info.content_type}")
```

---

### `should_download(remote_info: RemoteFileInfo) -> tuple[bool, str]`

**Purpose**: Determine if download is needed based on local file state

**Parameters**:
- `remote_info` (`RemoteFileInfo`): Metadata from remote server

**Returns**: `tuple[bool, str]`
- `bool`: True if download needed, False if local is up-to-date
- `str`: Reason for decision (for logging/display)

**Logic**:
1. If `config.force` is True → download
2. If destination doesn't exist → download
3. If destination exists but is empty → download
4. If remote_info.last_modified is None → download (can't compare)
5. If remote_info.last_modified > local_modified → download
6. Otherwise → skip

**Example**:
```python
remote_info = downloader.check_remote_info()
should_dl, reason = downloader.should_download(remote_info)
if should_dl:
    print(f"Downloading: {reason}")
else:
    print(f"Skipping: {reason}")
```

---

### `download(progress_callback: ProgressCallback | None = None) -> DownloadResult`

**Purpose**: Download file with progress tracking and retry logic

**Parameters**:
- `progress_callback` (`ProgressCallback | None`): Optional callback for progress updates

**Returns**: `DownloadResult` with success status, file path, size, duration, etc.

**Behavior**:
1. Check if download needed (unless forced)
2. If skip, return success result with `skipped=True`
3. Perform download with streaming and progress callbacks
4. Retry on transient failures (5xx, timeouts, connection errors)
5. Save to temporary file first, rename on success
6. Preserve existing file if download fails
7. Return result with metadata

**Progress Callbacks**:
- Called every 256KB or 500ms (whichever comes first)
- Called with `DownloadProgress` object
- Not called in quiet mode

**Raises**: Never raises (errors captured in DownloadResult)

**Example**:
```python
def show_progress(progress: DownloadProgress):
    print(f"Progress: {progress.percentage:.1f}% | "
          f"{progress.downloaded_bytes}/{progress.total_bytes} bytes | "
          f"{progress.bytes_per_second/1024/1024:.1f} MB/s")

result = downloader.download(progress_callback=show_progress)
if result.success:
    print(f"Downloaded to: {result.file_path}")
    print(f"File size: {result.file_size} bytes")
    print(f"Duration: {result.duration_seconds:.1f}s")
else:
    print(f"Failed: {result.error_message}")
```

---

## Implementation Details

### Retry Strategy

**Retryable Errors**:
- HTTP 500, 502, 503, 504 (server errors)
- HTTP 429 (rate limit)
- Connection errors (DNS, network failures)
- Timeout errors (connection or read timeout)

**Non-Retryable Errors**:
- HTTP 4xx (except 429) - client errors
- SSL/TLS errors
- Invalid URL
- File system errors (permissions, disk full)

**Retry Logic**:
```python
for attempt in range(max_retries + 1):
    try:
        # Attempt download
        response = client.get(url, ...)
        
        if response.status_code in RETRY_CODES:
            if attempt < max_retries:
                delay = calculate_backoff(attempt)
                time.sleep(delay)
                continue
        
        response.raise_for_status()
        # Process successful response
        return success_result(...)
        
    except (TimeoutError, ConnectionError) as e:
        if attempt < max_retries:
            delay = calculate_backoff(attempt)
            time.sleep(delay)
        else:
            return failure_result(str(e), ...)
```

**Backoff Calculation**:
- Base delay: 1 second
- Exponential: `1s, 2s, 4s`
- Jitter: ±25% random variation
- Formula: `delay = base * (2^attempt) * (1 + random(-0.25, 0.25))`

---

### File Safety

**Atomic Writes**:
```python
temp_path = destination.with_suffix('.tmp')
try:
    # Download to temp file
    with open(temp_path, 'wb') as f:
        for chunk in response.iter_bytes():
            f.write(chunk)
    
    # Rename on success (atomic on POSIX)
    temp_path.replace(destination)
    
except Exception as e:
    # Clean up temp file
    temp_path.unlink(missing_ok=True)
    raise
```

**Preservation**:
- Existing file never modified until new download completes successfully
- If download fails, existing file remains untouched
- If validation fails, downloaded file is deleted and old file restored

---

### Progress Tracking

**Update Logic**:
```python
UPDATE_THRESHOLD_BYTES = 256 * 1024  # 256KB
UPDATE_THRESHOLD_SECONDS = 0.5

last_update_time = time.time()
last_update_size = 0

for chunk in response.iter_bytes(chunk_size=8192):
    f.write(chunk)
    downloaded += len(chunk)
    
    now = time.time()
    bytes_since = downloaded - last_update_size
    time_since = now - last_update_time
    
    if bytes_since >= UPDATE_THRESHOLD_BYTES or time_since >= UPDATE_THRESHOLD_SECONDS:
        if progress_callback:
            progress = DownloadProgress(
                total_bytes=total,
                downloaded_bytes=downloaded,
                start_time=start,
                last_update_time=now,
                bytes_per_second=bytes_since / time_since
            )
            progress_callback(progress)
        
        last_update_time = now
        last_update_size = downloaded
```

---

## Testing Requirements

### Unit Tests

**Test: `test_check_remote_info_success`**
- Mock HTTP HEAD request
- Verify RemoteFileInfo extracted correctly
- Check all headers parsed (Content-Length, Last-Modified, ETag, Content-Type)

**Test: `test_check_remote_info_timeout`**
- Mock timeout on HEAD request
- Verify NetworkError raised

**Test: `test_should_download_force_true`**
- Set config.force = True
- Verify returns (True, "forced")

**Test: `test_should_download_file_missing`**
- Destination doesn't exist
- Verify returns (True, "file missing")

**Test: `test_should_download_remote_newer`**
- Local file older than remote
- Verify returns (True, "remote newer")

**Test: `test_should_download_up_to_date`**
- Local file same age as remote
- Verify returns (False, "up to date")

**Test: `test_download_success`**
- Mock successful GET request
- Verify DownloadResult.success = True
- Check file saved correctly
- Verify progress callbacks called

**Test: `test_download_retry_transient_error`**
- Mock 503 error on first attempt, success on second
- Verify retry_count = 1
- Verify final success

**Test: `test_download_max_retries_exceeded`**
- Mock 503 error on all attempts
- Verify DownloadResult.success = False
- Check retry_count = max_retries

**Test: `test_download_non_retryable_error`**
- Mock 404 error
- Verify no retry attempted
- Verify failure result

**Test: `test_download_preserves_existing_file_on_failure`**
- Create existing destination file
- Mock download failure
- Verify existing file unchanged

**Test: `test_progress_callback_frequency`**
- Mock download with known size
- Count callback invocations
- Verify called at appropriate intervals (256KB or 500ms)

---

## Dependencies

```python
import httpx
from pathlib import Path
from datetime import datetime
import time
import random
from typing import Optional, Callable
from loguru import logger

from .models import (
    DownloadConfig,
    DownloadProgress,
    DownloadResult,
    RemoteFileInfo,
    NetworkError,
    ConfigurationError
)
```

---

## Error Messages

All error messages should be user-friendly and actionable:

```python
ERROR_MESSAGES = {
    'connection_timeout': 'Connection timeout after {timeout}s. Check network connection.',
    'read_timeout': 'Read timeout after {timeout}s. File may be too large or connection too slow.',
    'ssl_error': 'SSL/TLS error: {details}. Check system certificates.',
    'dns_error': 'DNS resolution failed for {url}. Check hostname.',
    'http_4xx': 'HTTP {code}: {reason}. Check URL and permissions.',
    'http_5xx': 'Server error {code}: {reason}. Retrying...',
    'disk_full': 'Insufficient disk space to save file.',
    'permission_denied': 'Permission denied: {path}. Check file permissions.',
}
```
