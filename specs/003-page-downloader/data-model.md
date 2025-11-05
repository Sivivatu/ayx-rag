# Data Model: Page Downloader

**Feature**: 003-page-downloader  
**Date**: 2025-11-05  
**Purpose**: Define entities, relationships, and validation rules

## Overview

The page-downloader feature manages five core entities that track download configuration, individual page downloads, batch sessions, and results. These entities enable progress tracking, error handling, incremental updates, and comprehensive reporting.

## Entities

### 1. DownloadConfig

**Purpose**: Encapsulates all user-configurable settings for a download session

**Fields**:

| Field | Type | Required | Default | Description | Validation |
|-------|------|----------|---------|-------------|------------|
| `output_dir` | `Path` | Yes | - | Directory where HTML files are saved | Must be absolute path or relative to CWD |
| `delay` | `float` | No | `0.5` | Delay between consecutive requests (seconds) | Must be >= 0.0 |
| `max_file_size_mb` | `int` | No | `5` | Maximum file size limit in megabytes | Must be > 0 |
| `connect_timeout` | `float` | No | `30.0` | HTTP connection timeout (seconds) | Must be > 0.0 |
| `read_timeout` | `float` | No | `300.0` | HTTP read timeout (seconds) | Must be > 0.0 |
| `max_retries` | `int` | No | `3` | Maximum retry attempts for failed downloads | Must be >= 0 |
| `force` | `bool` | No | `False` | Force re-download all pages (skip incremental check) | - |
| `ignore_robots` | `bool` | No | `False` | Skip robots.txt checking | - |
| `dry_run` | `bool` | No | `False` | Preview downloads without executing | - |
| `user_agent` | `str` | No | `"uv-ayx-rag-page-downloader/0.1.0"` | HTTP User-Agent header | Non-empty string |

**Relationships**:
- Used by `DownloadSession` to configure batch downloads
- Used by `PageDownload` to configure individual downloads

**State Transitions**: Immutable after creation

**Implementation**:
```python
from dataclasses import dataclass
from pathlib import Path

@dataclass
class DownloadConfig:
    """Configuration for download operations."""
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
    
    def __post_init__(self):
        """Validate configuration values."""
        if self.delay < 0:
            raise ValueError("delay must be >= 0")
        if self.max_file_size_mb <= 0:
            raise ValueError("max_file_size_mb must be > 0")
        if self.connect_timeout <= 0:
            raise ValueError("connect_timeout must be > 0")
        if self.read_timeout <= 0:
            raise ValueError("read_timeout must be > 0")
        if self.max_retries < 0:
            raise ValueError("max_retries must be >= 0")
        if not self.user_agent:
            raise ValueError("user_agent cannot be empty")
        
        # Ensure output_dir is Path object
        self.output_dir = Path(self.output_dir)
    
    @property
    def max_file_size_bytes(self) -> int:
        """Convert MB limit to bytes."""
        return self.max_file_size_mb * 1024 * 1024
```

---

### 2. PageDownload

**Purpose**: Represents a single download operation for one URL with detailed tracking

**Fields**:

| Field | Type | Required | Default | Description | Validation |
|-------|------|----------|---------|-------------|------------|
| `url` | `str` | Yes | - | Source URL to download | Must be valid HTTP/HTTPS URL |
| `dest_path` | `Path` | Yes | - | Destination file path | Must be within output_dir |
| `start_time` | `datetime` | No | Auto | When download started | Auto-set on creation |
| `end_time` | `datetime\|None` | No | `None` | When download completed/failed | Set on completion |
| `bytes_transferred` | `int` | No | `0` | Total bytes downloaded | Must be >= 0 |
| `http_status_code` | `int\|None` | No | `None` | HTTP response status code | Valid HTTP status (100-599) |
| `status` | `DownloadStatus` | No | `PENDING` | Current download status | Enum: PENDING, IN_PROGRESS, SUCCESS, FAILED, SKIPPED |
| `error_message` | `str\|None` | No | `None` | Error description if failed | - |
| `retry_count` | `int` | No | `0` | Number of retry attempts made | Must be >= 0 |
| `last_modified` | `datetime\|None` | No | `None` | Remote Last-Modified header value | - |
| `content_type` | `str\|None` | No | `None` | Response Content-Type header | - |

**Relationships**:
- Part of a `DownloadSession` (many-to-one)
- Produces a `DownloadResult` (one-to-one)

**State Transitions**:
```
PENDING → IN_PROGRESS → {SUCCESS, FAILED, SKIPPED}
        ↓ (retry)
        IN_PROGRESS → {SUCCESS, FAILED}
```

**Implementation**:
```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

class DownloadStatus(Enum):
    """Status of a download operation."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class PageDownload:
    """Tracks a single page download operation."""
    url: str
    dest_path: Path
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    bytes_transferred: int = 0
    http_status_code: Optional[int] = None
    status: DownloadStatus = DownloadStatus.PENDING
    error_message: Optional[str] = None
    retry_count: int = 0
    last_modified: Optional[datetime] = None
    content_type: Optional[str] = None
    
    def mark_in_progress(self):
        """Mark download as in progress."""
        self.status = DownloadStatus.IN_PROGRESS
        self.start_time = datetime.now()
    
    def mark_success(self, bytes_transferred: int, http_status: int, content_type: str):
        """Mark download as successful."""
        self.status = DownloadStatus.SUCCESS
        self.end_time = datetime.now()
        self.bytes_transferred = bytes_transferred
        self.http_status_code = http_status
        self.content_type = content_type
    
    def mark_failed(self, error: str, http_status: Optional[int] = None):
        """Mark download as failed."""
        self.status = DownloadStatus.FAILED
        self.end_time = datetime.now()
        self.error_message = error
        if http_status:
            self.http_status_code = http_status
    
    def mark_skipped(self, reason: str):
        """Mark download as skipped."""
        self.status = DownloadStatus.SKIPPED
        self.end_time = datetime.now()
        self.error_message = reason
    
    @property
    def duration(self) -> float:
        """Calculate download duration in seconds."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
```

---

### 3. DownloadSession

**Purpose**: Represents a batch download operation across multiple URLs with aggregate metrics

**Fields**:

| Field | Type | Required | Default | Description | Validation |
|-------|------|----------|---------|-------------|------------|
| `session_id` | `str` | Yes | Auto | Unique session identifier | UUID format |
| `start_time` | `datetime` | No | Auto | When session started | Auto-set on creation |
| `end_time` | `datetime\|None` | No | `None` | When session completed | Set on completion |
| `total_urls` | `int` | Yes | - | Total number of URLs to process | Must be > 0 |
| `downloads` | `list[PageDownload]` | No | `[]` | List of page downloads | - |
| `config` | `DownloadConfig` | Yes | - | Session configuration | Valid DownloadConfig |

**Computed Properties**:

| Property | Type | Description |
|----------|------|-------------|
| `successful_count` | `int` | Number of successful downloads |
| `failed_count` | `int` | Number of failed downloads |
| `skipped_count` | `int` | Number of skipped downloads |
| `total_bytes_transferred` | `int` | Sum of bytes across all downloads |
| `average_download_speed` | `float` | Bytes per second across session |
| `duration` | `float` | Total session duration in seconds |
| `completion_percentage` | `float` | Percentage of URLs processed |

**Relationships**:
- Contains multiple `PageDownload` entities (one-to-many)
- Uses one `DownloadConfig` (many-to-one)

**State Transitions**: Session progresses linearly through URLs, no explicit state enum

**Implementation**:
```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import uuid4

@dataclass
class DownloadSession:
    """Tracks a batch download session."""
    total_urls: int
    config: DownloadConfig
    session_id: str = field(default_factory=lambda: str(uuid4()))
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    downloads: list[PageDownload] = field(default_factory=list)
    
    @property
    def successful_count(self) -> int:
        return sum(1 for d in self.downloads if d.status == DownloadStatus.SUCCESS)
    
    @property
    def failed_count(self) -> int:
        return sum(1 for d in self.downloads if d.status == DownloadStatus.FAILED)
    
    @property
    def skipped_count(self) -> int:
        return sum(1 for d in self.downloads if d.status == DownloadStatus.SKIPPED)
    
    @property
    def total_bytes_transferred(self) -> int:
        return sum(d.bytes_transferred for d in self.downloads)
    
    @property
    def duration(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return (datetime.now() - self.start_time).total_seconds()
    
    @property
    def average_download_speed(self) -> float:
        """Calculate average speed in bytes/second."""
        duration = self.duration
        if duration > 0:
            return self.total_bytes_transferred / duration
        return 0.0
    
    @property
    def completion_percentage(self) -> float:
        """Calculate percentage of URLs processed."""
        completed = len([d for d in self.downloads if d.end_time is not None])
        return (completed / self.total_urls) * 100 if self.total_urls > 0 else 0.0
    
    def add_download(self, download: PageDownload):
        """Add a page download to this session."""
        self.downloads.append(download)
    
    def mark_complete(self):
        """Mark session as complete."""
        self.end_time = datetime.now()
```

---

### 4. DownloadResult

**Purpose**: Immutable summary of a single download outcome for reporting

**Fields**:

| Field | Type | Required | Default | Description | Validation |
|-------|------|----------|---------|-------------|------------|
| `url` | `str` | Yes | - | Source URL | Must be valid HTTP/HTTPS URL |
| `dest_path` | `Path` | Yes | - | Destination file path | Must exist (for success) |
| `status` | `DownloadStatus` | Yes | - | Final download status | SUCCESS, FAILED, or SKIPPED |
| `error_message` | `str\|None` | No | `None` | Error description if failed/skipped | - |
| `file_size_bytes` | `int` | No | `0` | Size of downloaded file | Must be >= 0 |
| `duration_seconds` | `float` | No | `0.0` | Time taken for download | Must be >= 0.0 |
| `timestamp` | `datetime` | Yes | - | When download completed | - |

**Relationships**:
- Created from `PageDownload` (one-to-one)
- Part of session summary (many-to-one with `DownloadSession`)

**State Transitions**: Immutable after creation

**Implementation**:
```python
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

@dataclass(frozen=True)
class DownloadResult:
    """Immutable result of a download operation."""
    url: str
    dest_path: Path
    status: DownloadStatus
    timestamp: datetime
    error_message: Optional[str] = None
    file_size_bytes: int = 0
    duration_seconds: float = 0.0
    
    @classmethod
    def from_page_download(cls, page_download: PageDownload) -> "DownloadResult":
        """Create DownloadResult from PageDownload."""
        return cls(
            url=page_download.url,
            dest_path=page_download.dest_path,
            status=page_download.status,
            timestamp=page_download.end_time or datetime.now(),
            error_message=page_download.error_message,
            file_size_bytes=page_download.bytes_transferred,
            duration_seconds=page_download.duration,
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "url": self.url,
            "dest_path": str(self.dest_path),
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
            "error_message": self.error_message,
            "file_size_bytes": self.file_size_bytes,
            "duration_seconds": self.duration_seconds,
        }
```

---

### 5. URLList

**Purpose**: Represents the input containing URLs to download

**Fields**:

| Field | Type | Required | Default | Description | Validation |
|-------|------|----------|---------|-------------|------------|
| `source` | `str` | Yes | - | File path or single URL | Valid file path or HTTP/HTTPS URL |
| `format` | `URLListFormat` | Yes | - | Input format type | Enum: FILE, SINGLE_URL |
| `urls` | `list[str]` | No | `[]` | Parsed URLs | All must be valid HTTP/HTTPS |
| `total_count` | `int` | No | `0` | Total number of URLs | Must match len(urls) |

**Relationships**:
- Input to `DownloadSession` (one-to-one)

**State Transitions**: Loaded once, immutable after parsing

**Implementation**:
```python
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from urllib.parse import urlparse

class URLListFormat(Enum):
    """Format of URL input."""
    FILE = "file"
    SINGLE_URL = "single_url"

@dataclass
class URLList:
    """Represents input URLs for downloading."""
    source: str
    format: URLListFormat
    urls: list[str] = field(default_factory=list)
    
    @classmethod
    def from_file(cls, file_path: Path) -> "URLList":
        """Load URLs from text file (one per line)."""
        with open(file_path, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
        
        # Validate all URLs
        for url in urls:
            if not cls._is_valid_url(url):
                raise ValueError(f"Invalid URL: {url}")
        
        return cls(
            source=str(file_path),
            format=URLListFormat.FILE,
            urls=urls,
        )
    
    @classmethod
    def from_single_url(cls, url: str) -> "URLList":
        """Create URLList from single URL."""
        if not cls._is_valid_url(url):
            raise ValueError(f"Invalid URL: {url}")
        
        return cls(
            source=url,
            format=URLListFormat.SINGLE_URL,
            urls=[url],
        )
    
    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """Validate URL format."""
        try:
            result = urlparse(url)
            return all([result.scheme in ('http', 'https'), result.netloc])
        except Exception:
            return False
    
    @property
    def total_count(self) -> int:
        """Total number of URLs."""
        return len(self.urls)
```

## Entity Relationships

```
URLList (1) ─────> (1) DownloadSession
                         ↓
                   contains (1:N)
                         ↓
                   PageDownload (N)
                         ↓
                   produces (1:1)
                         ↓
                   DownloadResult (N)

DownloadConfig ───> (1:N) DownloadSession
               └──> (1:N) PageDownload
```

## Data Flow

1. **Input Parsing**: `URLList.from_file()` or `URLList.from_single_url()` creates validated URL list
2. **Session Creation**: `DownloadSession` initialized with `URLList.urls` and `DownloadConfig`
3. **Download Execution**: For each URL, create `PageDownload`, execute download, update state
4. **Result Collection**: Convert each `PageDownload` to `DownloadResult` for reporting
5. **Summary**: `DownloadSession` provides aggregate metrics from all `PageDownload` entities

## Validation Rules

### URL Validation
- Must start with `http://` or `https://`
- Must have valid domain (non-empty netloc)
- Path components sanitized for filesystem safety

### File Path Validation
- Output directory must be writable
- Destination paths must be within output_dir (no path traversal)
- File names must not contain reserved characters

### Configuration Validation
- All timeouts must be positive
- Delays must be non-negative
- Max file size must be positive
- Max retries must be non-negative

### State Transition Validation
- `PageDownload.status` must follow valid state machine
- Cannot mark SUCCESS without http_status_code and bytes_transferred
- Cannot mark FAILED without error_message

## Persistence

**Current Implementation**: In-memory only (no database)

**Logging**: Structured logs to stderr via loguru
- Each state transition logged with timestamp
- Session summaries logged on completion

**Future Enhancement** (out of scope for MVP):
- SQLite database for progress persistence
- Resume capability across sessions
- Historical download tracking

## Testing Considerations

**Unit Tests**:
- Validate field constraints (__post_init__ validation)
- Test state transitions (mark_success, mark_failed, etc.)
- Test computed properties (duration, speeds, percentages)
- Test URLList parsing (valid/invalid URLs, file formats)

**Integration Tests**:
- Full download session with mocked HTTP
- Incremental update scenarios (Last-Modified comparison)
- Error handling workflows (retries, failures)

**Test Fixtures**:
```python
@pytest.fixture
def sample_config():
    return DownloadConfig(output_dir=Path("/tmp/test"))

@pytest.fixture
def sample_page_download():
    return PageDownload(
        url="https://help.alteryx.com/test.html",
        dest_path=Path("/tmp/test/test.html")
    )

@pytest.fixture
def sample_session(sample_config):
    return DownloadSession(total_urls=10, config=sample_config)
```

## Summary

The data model provides clear separation of concerns:
- **DownloadConfig**: User settings and configuration
- **URLList**: Input validation and parsing
- **PageDownload**: Individual download tracking with state machine
- **DownloadSession**: Batch coordination and aggregate metrics
- **DownloadResult**: Immutable result records for reporting

All entities use dataclasses for simplicity, type safety, and IDE support. Validation is enforced at creation time via `__post_init__` methods. State transitions are explicit and tracked. The model supports the full lifecycle from input parsing through execution to result reporting.
