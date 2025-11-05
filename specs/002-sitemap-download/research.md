# Research: Sitemap Download Implementation

**Feature**: 002-sitemap-download  
**Date**: 2025-11-03  
**Status**: Complete

## Research Questions

1. Which HTTP client library best suits streaming large file downloads with progress?
2. What is the optimal progress update frequency for responsive UX?
3. What memory usage targets should we set for 100MB+ file handling?
4. What retry strategy is appropriate for transient network failures?

---

## 1. HTTP Client Library Selection

### Option 1: requests

**Pros**:
- Most widely used (50M+ downloads/month)
- Excellent documentation and community support
- Simple, intuitive API
- Built-in streaming with `stream=True`
- Automatic redirect following
- Session support for connection pooling

**Cons**:
- Synchronous only (no async)
- Not actively developed (maintenance mode)
- Timeout handling requires careful configuration

**Code Example**:
```python
import requests
from pathlib import Path

def download_with_progress(url: str, dest: Path):
    response = requests.get(url, stream=True, timeout=(30, 300))
    response.raise_for_status()
    
    total = int(response.headers.get('content-length', 0))
    downloaded = 0
    
    with open(dest, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            downloaded += len(chunk)
            progress = (downloaded / total) * 100
            print(f"Progress: {progress:.1f}%")
```

**Memory Efficiency**: Excellent - streaming keeps memory constant regardless of file size

---

### Option 2: httpx

**Pros**:
- Modern, actively maintained
- Supports both sync and async APIs
- HTTP/2 support
- Excellent timeout handling
- Similar API to requests (easy migration path)
- Better type hints

**Cons**:
- Less mature than requests
- Smaller community (though growing)
- Slightly more complex setup

**Code Example**:
```python
import httpx
from pathlib import Path

def download_with_progress(url: str, dest: Path):
    with httpx.Client(timeout=httpx.Timeout(30.0, read=300.0)) as client:
        with client.stream('GET', url) as response:
            response.raise_for_status()
            
            total = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(dest, 'wb') as f:
                for chunk in response.iter_bytes(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    progress = (downloaded / total) * 100
                    print(f"Progress: {progress:.1f}%")
```

**Memory Efficiency**: Excellent - streaming design, constant memory usage

---

### Option 3: urllib3

**Pros**:
- Low-level, maximum control
- Used by requests under the hood
- Very stable, well-tested
- Excellent connection pooling

**Cons**:
- More verbose, lower-level API
- Requires more boilerplate code
- No built-in progress indication helpers
- Steeper learning curve

**Memory Efficiency**: Excellent with manual streaming

---

### Option 4: urllib (stdlib)

**Pros**:
- No external dependencies
- Part of standard library
- Sufficient for basic HTTP operations

**Cons**:
- Clunky API
- Poor error handling
- No streaming convenience methods
- Limited timeout control
- Difficult to implement progress indication

**Memory Efficiency**: Can be good with careful buffering, but easy to misuse

---

### Decision: **httpx**

**Rationale**:
1. **Modern & Maintained**: Active development with regular updates and security patches
2. **Future-Proof**: Async support means we can optimize later if needed without rewriting
3. **Better DX**: Excellent type hints, clear API, good error messages
4. **Timeout Handling**: More explicit and safer timeout configuration than requests
5. **HTTP/2**: Future compatibility with modern servers
6. **Streaming**: First-class streaming support with clean API

**Alternatives Considered**:
- **requests**: Ruled out due to maintenance mode status. While stable, choosing a deprecated library for new code is risky for long-term maintenance.
- **urllib3**: Too low-level for this use case. We'd need to implement too much boilerplate.
- **urllib**: Insufficient capabilities, would require significant wrapper code.

---

## 2. Progress Update Frequency

### Research Findings

**Human Perception Thresholds**:
- 100ms: Feels instantaneous
- 250ms: Noticeable delay
- 1000ms: Feels sluggish
- 10000ms: Appears broken

**Network I/O Characteristics**:
- Modern broadband: 50-500 Mbps
- Chunk size affects update granularity
- Too frequent updates can hurt performance (terminal I/O overhead)

### Decision: **Update every 256KB or 500ms, whichever comes first**

**Rationale**:
1. **256KB threshold**: Provides smooth visual feedback without terminal I/O bottleneck
2. **500ms timeout**: Guarantees updates even on slow connections (keeps user informed)
3. **Balanced**: 256KB = ~32 chunks at 8KB chunk size = good granularity without spam
4. **Responsive**: At 50Mbps, updates ~every 40ms; at 5Mbps, uses 500ms fallback

**Implementation**:
```python
last_update = time.time()
last_size = 0
UPDATE_THRESHOLD_BYTES = 256 * 1024  # 256KB
UPDATE_THRESHOLD_SECONDS = 0.5

for chunk in response.iter_bytes(chunk_size=8192):
    f.write(chunk)
    downloaded += len(chunk)
    
    now = time.time()
    bytes_since_update = downloaded - last_size
    time_since_update = now - last_update
    
    if bytes_since_update >= UPDATE_THRESHOLD_BYTES or time_since_update >= UPDATE_THRESHOLD_SECONDS:
        show_progress(downloaded, total)
        last_update = now
        last_size = downloaded
```

---

## 3. Memory Usage Targets

### Research Findings

**File Size Context**:
- Expected sitemap: <100MB (likely 10-50MB compressed)
- 35k+ URLs × ~500 bytes/entry average = ~17.5MB uncompressed
- Modern systems: 8GB+ RAM typical

**Streaming Best Practices**:
- Keep memory usage constant regardless of file size
- Buffer size affects performance vs memory tradeoff
- 8KB chunk size is industry standard (matches OS page size)

### Decision: **Target <10MB memory footprint**

**Rationale**:
1. **10x Safety Margin**: Even for 100MB files, 10MB buffer is sufficient
2. **Streaming**: With 8KB chunks, actual memory usage ~8-16KB + progress state
3. **Practical**: 10MB is negligible on modern systems, provides headroom
4. **Validation**: XML validation can be done streaming (SAX parser) to avoid loading entire file

**Implementation Strategy**:
```python
CHUNK_SIZE = 8 * 1024  # 8KB - OS page size
PROGRESS_BUFFER_SIZE = 1024  # Minimal progress tracking state

# Download streaming: ~8-16KB memory
with client.stream('GET', url) as response:
    for chunk in response.iter_bytes(chunk_size=CHUNK_SIZE):
        f.write(chunk)  # Writes to disk immediately

# Validation streaming: SAX parser, constant memory
import xml.sax

class SitemapValidator(xml.sax.ContentHandler):
    def __init__(self):
        self.url_count = 0
        self.current_element = []
    
    def startElement(self, name, attrs):
        self.current_element.append(name)
    
    def endElement(self, name):
        if name == 'url':
            self.url_count += 1
        self.current_element.pop()

parser = xml.sax.make_parser()
parser.setContentHandler(SitemapValidator())
parser.parse(file_path)  # Streaming parse, constant memory
```

---

## 4. Retry Strategy for Network Failures

### Research Findings

**Network Failure Types**:
- **Transient**: Temporary network glitches, DNS hiccups, server overload (should retry)
- **Permanent**: 404 Not Found, 403 Forbidden, SSL errors (should not retry)
- **Ambiguous**: Timeouts, connection resets (may retry with backoff)

**Best Practices**:
- Exponential backoff prevents thundering herd
- Jitter prevents synchronized retries
- 3 retries is industry standard for most operations
- Only retry idempotent operations (GET is safe)

### Decision: **Exponential backoff with jitter, 3 retries**

**Rationale**:
1. **3 Retries**: Balances reliability (catches transient issues) vs speed (fails fast on permanent errors)
2. **Exponential Backoff**: 1s, 2s, 4s delays give network/server time to recover
3. **Jitter**: ±25% randomization prevents synchronized retry storms
4. **Selective**: Only retry on transient errors (5xx, timeouts, connection errors)

**Implementation**:
```python
import time
import random
from typing import Optional
import httpx

RETRY_STATUS_CODES = {500, 502, 503, 504}  # Server errors worth retrying
MAX_RETRIES = 3
BASE_DELAY = 1.0  # seconds

def download_with_retry(url: str, dest: Path) -> Optional[Path]:
    """Download with exponential backoff retry strategy."""
    last_error = None
    
    for attempt in range(MAX_RETRIES + 1):
        try:
            # Attempt download
            response = httpx.get(url, timeout=httpx.Timeout(30.0, read=300.0))
            
            # Check if we should retry
            if response.status_code in RETRY_STATUS_CODES:
                if attempt < MAX_RETRIES:
                    delay = calculate_retry_delay(attempt)
                    logger.warning(f"Retry {attempt + 1}/{MAX_RETRIES} after {delay:.1f}s (status: {response.status_code})")
                    time.sleep(delay)
                    continue
            
            # Raise for other errors
            response.raise_for_status()
            
            # Success - save file
            with open(dest, 'wb') as f:
                for chunk in response.iter_bytes():
                    f.write(chunk)
            
            return dest
            
        except (httpx.TimeoutException, httpx.ConnectError) as e:
            last_error = e
            if attempt < MAX_RETRIES:
                delay = calculate_retry_delay(attempt)
                logger.warning(f"Retry {attempt + 1}/{MAX_RETRIES} after {delay:.1f}s (error: {type(e).__name__})")
                time.sleep(delay)
            else:
                logger.error(f"Max retries exceeded: {e}")
                
        except httpx.HTTPStatusError as e:
            # Don't retry 4xx errors (client errors)
            logger.error(f"HTTP error {e.response.status_code}: {e}")
            return None
    
    return None

def calculate_retry_delay(attempt: int) -> float:
    """Calculate delay with exponential backoff and jitter."""
    delay = BASE_DELAY * (2 ** attempt)  # Exponential: 1s, 2s, 4s
    jitter = random.uniform(-0.25, 0.25) * delay  # ±25% jitter
    return max(0.1, delay + jitter)  # Minimum 100ms
```

**Retry Decision Matrix**:
| Error Type | Retry? | Reason |
|------------|--------|--------|
| 500-504 | ✅ Yes | Server errors, often transient |
| 429 | ✅ Yes | Rate limit, respect Retry-After header |
| Timeout | ✅ Yes | Network congestion, may resolve |
| Connection Error | ✅ Yes | DNS/network glitch, often transient |
| 400-404 | ❌ No | Client error, won't fix with retry |
| 403 | ❌ No | Forbidden, permission issue |
| SSL Error | ❌ No | Certificate/security issue |

---

## Summary

### Key Decisions

1. **HTTP Client**: httpx (modern, async-capable, excellent DX)
2. **Progress Updates**: Every 256KB or 500ms (responsive without spam)
3. **Memory Target**: <10MB (streaming with 8KB chunks + SAX validation)
4. **Retry Strategy**: 3 retries with exponential backoff + jitter (1s, 2s, 4s)

### Technology Stack

```toml
# packages/sitemap-download/pyproject.toml
[project]
dependencies = [
    "httpx>=0.25.0",      # HTTP client with streaming
    "typer>=0.9.0",       # CLI framework
    "loguru>=0.7.0",      # Structured logging
]
```

### Next Steps

- Phase 1: Design data models (DownloadResult, DownloadProgress, ValidationResult)
- Phase 1: Design API contracts (CLI interface, downloader interface, validator interface)
- Phase 1: Create quickstart.md with usage examples
