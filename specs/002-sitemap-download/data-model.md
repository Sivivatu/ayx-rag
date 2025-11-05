# Data Model: Sitemap Download

**Feature**: 002-sitemap-download  
**Date**: 2025-11-03  
**Status**: Complete

## Overview

This document defines the data structures used in the sitemap download feature. All entities are implemented as Python dataclasses with type hints for clarity and validation.

---

## Entities

### 1. DownloadConfig

**Purpose**: Configuration for a download operation

**Fields**:
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `url` | `str` | ✅ | - | Source URL to download from |
| `destination` | `Path` | ✅ | - | Local file path to save to |
| `force` | `bool` | ❌ | `False` | Skip modification date check |
| `connection_timeout` | `float` | ❌ | `30.0` | Connection timeout in seconds |
| `read_timeout` | `float` | ❌ | `300.0` | Read timeout in seconds |
| `max_retries` | `int` | ❌ | `3` | Maximum retry attempts |
| `chunk_size` | `int` | ❌ | `8192` | Download chunk size in bytes |

**Validation Rules**:
- `url` must be valid HTTP/HTTPS URL
- `destination` parent directory must exist or be creatable
- `connection_timeout` > 0
- `read_timeout` > 0
- `max_retries` >= 0
- `chunk_size` > 0

**Example**:
```python
@dataclass
class DownloadConfig:
    url: str
    destination: Path
    force: bool = False
    connection_timeout: float = 30.0
    read_timeout: float = 300.0
    max_retries: int = 3
    chunk_size: int = 8192
    
    def __post_init__(self):
        if not self.url.startswith(('http://', 'https://')):
            raise ValueError(f"Invalid URL scheme: {self.url}")
        if self.connection_timeout <= 0:
            raise ValueError(f"connection_timeout must be > 0, got {self.connection_timeout}")
        # ... additional validations
```

---

### 2. DownloadProgress

**Purpose**: Tracks real-time download progress

**Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `total_bytes` | `int` | ✅ | Total file size in bytes |
| `downloaded_bytes` | `int` | ✅ | Bytes downloaded so far |
| `start_time` | `datetime` | ✅ | Download start timestamp |
| `last_update_time` | `datetime` | ✅ | Last progress update timestamp |
| `bytes_per_second` | `float` | ✅ | Current download speed |

**Computed Properties**:
- `percentage: float` - Progress as percentage (0-100)
- `eta_seconds: float` - Estimated time to completion
- `elapsed_seconds: float` - Time elapsed since start

**State Transitions**:
```
Created (0%) → Downloading (1-99%) → Complete (100%)
                    ↓
              Failed (any %)
```

**Example**:
```python
@dataclass
class DownloadProgress:
    total_bytes: int
    downloaded_bytes: int
    start_time: datetime
    last_update_time: datetime
    bytes_per_second: float
    
    @property
    def percentage(self) -> float:
        if self.total_bytes == 0:
            return 0.0
        return (self.downloaded_bytes / self.total_bytes) * 100
    
    @property
    def eta_seconds(self) -> float:
        if self.bytes_per_second == 0:
            return float('inf')
        remaining = self.total_bytes - self.downloaded_bytes
        return remaining / self.bytes_per_second
    
    @property
    def elapsed_seconds(self) -> float:
        return (datetime.now() - self.start_time).total_seconds()
```

---

### 3. DownloadResult

**Purpose**: Final outcome of a download operation

**Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `success` | `bool` | ✅ | Whether download succeeded |
| `file_path` | `Path \| None` | ✅ | Path to downloaded file (if success) |
| `file_size` | `int \| None` | ✅ | Size of downloaded file in bytes |
| `duration_seconds` | `float` | ✅ | Total operation duration |
| `error_message` | `str \| None` | ✅ | Error description (if failed) |
| `retry_count` | `int` | ✅ | Number of retries attempted |
| `skipped` | `bool` | ✅ | Whether download was skipped (up-to-date) |
| `remote_modified` | `datetime \| None` | ❌ | Remote file modification date |
| `local_modified` | `datetime \| None` | ❌ | Local file modification date |

**Invariants**:
- If `success` is `True`, `file_path` and `file_size` must not be `None`
- If `success` is `False`, `error_message` must not be `None`
- If `skipped` is `True`, `success` must also be `True`
- `retry_count` <= `max_retries` from config

**Example**:
```python
@dataclass
class DownloadResult:
    success: bool
    file_path: Path | None
    file_size: int | None
    duration_seconds: float
    error_message: str | None
    retry_count: int
    skipped: bool
    remote_modified: datetime | None = None
    local_modified: datetime | None = None
    
    @staticmethod
    def success_result(
        file_path: Path,
        file_size: int,
        duration: float,
        retry_count: int = 0,
        skipped: bool = False
    ) -> 'DownloadResult':
        return DownloadResult(
            success=True,
            file_path=file_path,
            file_size=file_size,
            duration_seconds=duration,
            error_message=None,
            retry_count=retry_count,
            skipped=skipped
        )
    
    @staticmethod
    def failure_result(
        error: str,
        duration: float,
        retry_count: int = 0
    ) -> 'DownloadResult':
        return DownloadResult(
            success=False,
            file_path=None,
            file_size=None,
            duration_seconds=duration,
            error_message=error,
            retry_count=retry_count,
            skipped=False
        )
```

---

### 4. ValidationResult

**Purpose**: Result of XML sitemap validation

**Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `valid` | `bool` | ✅ | Whether validation passed |
| `url_count` | `int \| None` | ✅ | Number of URLs found (if valid) |
| `file_size` | `int` | ✅ | Size of validated file in bytes |
| `error_message` | `str \| None` | ✅ | Validation error (if invalid) |
| `validation_duration` | `float` | ✅ | Time taken to validate (seconds) |

**Validation Checks**:
1. File is well-formed XML
2. Root element is `<urlset>` or `<sitemapindex>`
3. Contains at least one `<url>` or `<sitemap>` entry
4. File size > 0 bytes

**Example**:
```python
@dataclass
class ValidationResult:
    valid: bool
    url_count: int | None
    file_size: int
    error_message: str | None
    validation_duration: float
    
    @staticmethod
    def valid_result(url_count: int, file_size: int, duration: float) -> 'ValidationResult':
        return ValidationResult(
            valid=True,
            url_count=url_count,
            file_size=file_size,
            error_message=None,
            validation_duration=duration
        )
    
    @staticmethod
    def invalid_result(error: str, file_size: int, duration: float) -> 'ValidationResult':
        return ValidationResult(
            valid=False,
            url_count=None,
            file_size=file_size,
            error_message=error,
            validation_duration=duration
        )
```

---

### 5. RemoteFileInfo

**Purpose**: Metadata about remote file without downloading

**Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `url` | `str` | ✅ | Remote file URL |
| `size` | `int \| None` | ✅ | Content-Length header value |
| `last_modified` | `datetime \| None` | ✅ | Last-Modified header value |
| `etag` | `str \| None` | ✅ | ETag header value |
| `content_type` | `str \| None` | ✅ | Content-Type header value |

**Usage**: Obtained via HTTP HEAD request to check if download is needed

**Example**:
```python
@dataclass
class RemoteFileInfo:
    url: str
    size: int | None
    last_modified: datetime | None
    etag: str | None
    content_type: str | None
    
    def is_newer_than(self, local_modified: datetime) -> bool:
        """Check if remote file is newer than local file."""
        if self.last_modified is None:
            return True  # Unknown, assume newer
        return self.last_modified > local_modified
    
    def is_xml(self) -> bool:
        """Check if content type indicates XML."""
        if self.content_type is None:
            return False
        return 'xml' in self.content_type.lower()
```

---

## Relationships

```
DownloadConfig
    ↓ (used by)
Downloader.download()
    ↓ (emits)
DownloadProgress (0..N during download)
    ↓ (produces)
DownloadResult
    ↓ (if success)
Validator.validate()
    ↓ (produces)
ValidationResult
```

**Flow**:
1. User provides `DownloadConfig`
2. Downloader checks `RemoteFileInfo` (if not forced)
3. Downloader emits `DownloadProgress` events during download
4. Downloader returns `DownloadResult`
5. If successful, Validator produces `ValidationResult`
6. CLI reports final outcome to user

---

## Type Definitions

```python
# Type aliases for clarity
from typing import Callable
from pathlib import Path

# Progress callback for streaming updates
ProgressCallback = Callable[[DownloadProgress], None]

# Result types
DownloadOutcome = DownloadResult
ValidationOutcome = ValidationResult
```

---

## Error Hierarchy

```python
class SitemapDownloadError(Exception):
    """Base exception for sitemap download errors."""
    pass

class NetworkError(SitemapDownloadError):
    """Network-related errors (timeouts, connection failures)."""
    pass

class ValidationError(SitemapDownloadError):
    """File validation errors (malformed XML, empty file)."""
    pass

class ConfigurationError(SitemapDownloadError):
    """Invalid configuration (bad URL, invalid paths)."""
    pass
```

---

## Implementation Notes

### Immutability
- All dataclasses use `frozen=True` where appropriate
- Progress objects are replaced, not mutated

### Type Safety
- Use `Path` for file paths (not `str`)
- Use `datetime` for timestamps (not `float` or `str`)
- Use `None` for optional fields, not empty strings or -1

### Validation
- Validation happens in `__post_init__` for config objects
- Runtime validation for downloaded content
- Use descriptive error messages

### Serialization
- All entities can be serialized to JSON for logging
- Use `asdict()` from dataclasses module
- Handle `Path` and `datetime` serialization explicitly

**Example**:
```python
import json
from dataclasses import asdict
from pathlib import Path
from datetime import datetime

def serialize_result(result: DownloadResult) -> str:
    """Serialize result to JSON string."""
    data = asdict(result)
    # Handle Path objects
    if result.file_path:
        data['file_path'] = str(result.file_path)
    # Handle datetime objects
    if result.remote_modified:
        data['remote_modified'] = result.remote_modified.isoformat()
    if result.local_modified:
        data['local_modified'] = result.local_modified.isoformat()
    return json.dumps(data, indent=2)
```
