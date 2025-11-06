# Feature Specification: Page Downloader

**Feature Branch**: `003-page-downloader`  
**Created**: November 5, 2025  
**Status**: Draft  
**Input**: User description: "Create the process for taking each individual url downloaded from the sitemap filter and scrape the raw page"

## Clarifications

### Session 2025-11-05

- Q: Should the system support concurrent downloads, or strictly sequential? → A: Sequential only - simpler implementation, guarantees rate limiting, no concurrency complexity
- Q: How should the system handle SSL/TLS certificate validation? → A: Strict validation always - verify certificates, fail on invalid certs (most secure, appropriate for public sites)
- Q: How should the system enforce robots.txt rules? → A: Check and skip with warning - skip disallowed URLs, log warnings, continue with allowed URLs, with optional --ignore-robots-txt flag to bypass check
- Q: How should the system handle HTTP 429 (Too Many Requests) responses? → A: Retry with longer backoff, respect Retry-After header if present, otherwise use 2x normal backoff
- Q: Should the system enforce a maximum file size limit for downloads? → A: Configurable limit with default 5MB (--max-file-size), abort download if exceeded, log error
- Q: Where should cross-workspace dependencies (httpx, typer, loguru, rich) be declared? → A: Workspace root pyproject.toml - enables reuse across all feature packages, follows uv workspace best practices
- Q: How should the system handle URLs that return valid HTTP responses with non-HTML content? → A: Skip and log warning - Skip non-HTML URLs with warning message, continue processing remaining URLs (graceful degradation for batch operations)
- Q: How should the system handle malformed URLs in the input file? → A: Skip with warning, continue batch - Log warning with line number and invalid URL, skip it, continue processing remaining URLs
- Q: What should the system do when output directory or nested subdirectories don't exist? → A: Auto-create with logging - Create missing directories recursively (mkdir -p behavior), log the creation, proceed with download
- Q: When a URL redirects, which URL should determine the file path? → A: Use final destination URL - Save file using the path from the URL after all redirects are resolved (matches user expectations and current documentation structure)
- Q: If a download is interrupted mid-response, what should the system do? → A: Skip page, log warning - Discard partial content, log warning, treat as failed download, let retry logic handle from scratch (ensures file integrity, consistent with graceful degradation pattern)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Download Single Page (Priority: P1)

As a data engineer building the RAG pipeline, I need to download the raw HTML content of a single Alteryx documentation page from a URL so that the content can be processed and indexed for search.

**Why this priority**: This is the foundational capability - being able to download a single page is the core function that all other features build upon. Without this, no content collection is possible.

**Independent Test**: Can be fully tested by providing a single URL and verifying that the raw HTML is downloaded and saved to the correct file path, delivering immediate value by enabling manual content collection.

**Acceptance Scenarios**:

1. **Given** a valid Alteryx help URL, **When** the download command is executed, **Then** the HTML content is fetched and saved to disk
2. **Given** a successful download, **When** the file is saved, **Then** it preserves the URL's path structure in the output directory (e.g., `en/designer/tools.html`)
3. **Given** a download completes, **When** the HTML is saved, **Then** the system logs the URL, file size, and timestamp
4. **Given** an invalid URL or network error, **When** download is attempted, **Then** the system reports a clear error message without crashing

---

### User Story 2 - Batch Download from URL List (Priority: P2)

As a data engineer processing filtered sitemap results, I need to download HTML pages for all URLs in a text file so that I can collect documentation content at scale without manual intervention.

**Why this priority**: Enables practical use at scale (hundreds/thousands of URLs from sitemap-filter), critical for production workflows but builds on single-page download capability.

**Independent Test**: Can be tested by providing a text file with multiple URLs and verifying that all pages are downloaded with appropriate progress tracking, rate limiting, and error handling.

**Acceptance Scenarios**:

1. **Given** a text file containing one URL per line, **When** the batch download command runs, **Then** each URL is processed sequentially
2. **Given** batch download is in progress, **When** downloading multiple pages, **Then** the system displays progress (X of Y completed, current URL, success/failure status)
3. **Given** batch download encounters an error on one URL, **When** the error occurs, **Then** the system logs the error and continues processing remaining URLs
4. **Given** batch download is configured with rate limiting, **When** downloading consecutive pages, **Then** the system waits the specified delay between requests
5. **Given** batch download completes, **When** all URLs are processed, **Then** the system reports summary statistics (total, successful, failed, skipped)

---

### User Story 3 - Incremental Updates (Priority: P3)

As a data engineer maintaining up-to-date documentation, I need the system to skip downloading pages that haven't changed since the last download so that I can run frequent updates efficiently without re-downloading unchanged content.

**Why this priority**: Optimizes performance for repeated runs and scheduled updates, important for production efficiency but not critical for initial content collection.

**Independent Test**: Can be tested independently by running downloads twice on the same URL set and verifying that unchanged pages are skipped on the second run while modified pages are re-downloaded.

**Acceptance Scenarios**:

1. **Given** a page was previously downloaded, **When** checking for updates, **Then** the system compares local file timestamp with remote Last-Modified header
2. **Given** a remote page is newer than local file, **When** incremental download runs, **Then** the page is re-downloaded and local file is updated
3. **Given** a remote page is unchanged, **When** incremental download runs, **Then** the system skips the download and logs "unchanged"
4. **Given** the user forces a full refresh, **When** the download command includes the force flag, **Then** all pages are re-downloaded regardless of timestamps
5. **Given** a previously downloaded page returns 404, **When** incremental download runs, **Then** the system logs the missing page but preserves the local file

---

### User Story 4 - Retry Failed Downloads (Priority: P4)

As a data engineer dealing with network variability, I need the system to automatically retry failed downloads with exponential backoff so that temporary network issues don't require manual intervention.

**Why this priority**: Improves reliability for production use but MVP can function with basic error handling and manual retries.

**Independent Test**: Can be tested by simulating network failures (timeouts, connection errors) and verifying that the system retries appropriately before reporting failure.

**Acceptance Scenarios**:

1. **Given** a download encounters a timeout, **When** the error occurs, **Then** the system retries up to the configured maximum (default: 3 attempts)
2. **Given** retry attempts are in progress, **When** waiting between attempts, **Then** the system uses exponential backoff with jitter
3. **Given** all retry attempts fail, **When** maximum retries are exhausted, **Then** the system logs the failure and continues to the next URL
4. **Given** a download encounters HTTP 5xx error, **When** the error occurs, **Then** the system treats it as retryable and follows retry logic
5. **Given** a download encounters HTTP 4xx error, **When** the error occurs, **Then** the system treats it as non-retryable and skips immediately

---

### Edge Cases

- What happens when the URL returns a redirect (301/302)? → System follows redirects per FR-023, uses final destination URL for file path, logs original URL for audit trail
- What happens if the output directory doesn't exist or lacks write permissions? → System auto-creates missing directories recursively with logging; if lacks write permissions, logs error and exits with configuration error code
- How does the system handle malformed URLs in the input file? → System logs warning with line number and invalid URL, skips it, continues processing remaining URLs
- What happens if the URL returns non-HTML content (e.g., PDF, JSON)? → System skips the URL, logs a warning with URL and Content-Type, continues with remaining URLs
- How does the system handle URLs with query parameters or fragments?
- How does the system handle partial downloads (connection interrupted mid-response)? → System discards partial content, logs warning with URL and bytes received, treats as failed download for retry logic
- What happens if local disk space is exhausted during batch download?
- How does the system handle concurrent downloads for the same URL (race condition)?
- What happens when URL path contains characters invalid for filesystem (e.g., `?`, `*`, `:`)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept a text file containing one URL per line as input
- **FR-002**: System MUST accept a single URL as command-line argument for ad-hoc downloads
- **FR-003**: System MUST download the raw HTML content of each URL via HTTP GET request
- **FR-003a**: System MUST process URLs sequentially (one at a time), not concurrently, to ensure predictable rate limiting and simpler error handling
- **FR-004**: System MUST save downloaded HTML files using the URL's path structure (e.g., `en/designer/tools.html`) within the configured output directory
- **FR-005**: System MUST sanitize URL paths to ensure valid filesystem names (replace invalid characters)
- **FR-006**: System MUST provide configurable rate limiting (delay between requests, default: 0.5 seconds)
- **FR-007**: System MUST support configurable connection timeout (default: 30 seconds)
- **FR-008**: System MUST support configurable read timeout (default: 300 seconds)
- **FR-008a**: System MUST support configurable maximum file size (--max-file-size, default: 5MB) and abort downloads exceeding this limit
- **FR-009**: System MUST implement retry logic with exponential backoff and jitter for transient failures
- **FR-010**: System MUST support configurable maximum retry attempts (default: 3)
- **FR-011**: System MUST distinguish between retryable errors (timeouts, 5xx, 429) and non-retryable errors (other 4xx)
- **FR-011a**: System MUST handle HTTP 429 responses as retryable with extended backoff, respecting Retry-After header when present, otherwise using 2x normal backoff delay
- **FR-012**: System MUST validate that downloaded content is HTML (check Content-Type header); if non-HTML content is detected, system MUST skip the URL, log a warning with the URL and Content-Type, and continue processing remaining URLs
- **FR-013**: System MUST check if local HTML file exists and compare with remote Last-Modified header
- **FR-014**: System MUST skip downloading unchanged pages (local timestamp >= remote timestamp) in incremental mode
- **FR-015**: System MUST support a force flag (`--force`) to bypass incremental checks and re-download all pages
- **FR-016**: System MUST display real-time progress during batch downloads (current URL, X of Y completed, success/failure)
- **FR-017**: System MUST log each download operation with timestamp, URL, file path, status, and file size
- **FR-018**: System MUST report summary statistics after batch download (total URLs, successful, failed, skipped, duration)
- **FR-019**: System MUST continue processing remaining URLs after individual download failures
- **FR-020**: System MUST preserve existing local files if download or validation fails
- **FR-021**: System MUST use atomic writes (temp file + rename) to prevent file corruption
- **FR-022**: System MUST support custom HTTP headers (User-Agent, Accept, Accept-Encoding)
- **FR-022a**: System MUST verify SSL/TLS certificates and reject connections with invalid, expired, or self-signed certificates
- **FR-023**: System MUST follow HTTP redirects (301, 302, 303, 307, 308); the final destination URL after all redirects MUST be used to determine the file path structure
- **FR-024**: System MUST check robots.txt for help.alteryx.com and skip URLs disallowed by robots.txt directives, logging a warning for each skipped URL
- **FR-024a**: System MUST support an optional flag (--ignore-robots-txt) to bypass robots.txt checking for special circumstances
- **FR-025**: System MUST provide dry-run mode to preview what would be downloaded without actually downloading
- **FR-026**: System MUST exit with standard exit codes (0: success, 1: download failures occurred, 2: validation failures, 3: configuration error)
- **FR-027**: Cross-workspace dependencies (httpx, typer, loguru, rich) MUST be declared in workspace root pyproject.toml to enable reuse across feature packages
- **FR-027a**: System MUST validate URLs during input parsing; when a malformed URL is detected, system MUST log a warning with line number and invalid URL, skip it, and continue processing remaining URLs
- **FR-027b**: System MUST auto-create missing output directories and nested subdirectories recursively, log directory creation events, and proceed with download
- **FR-027c**: System MUST handle interrupted downloads (connection drops mid-response) by discarding partial content, logging a warning, and allowing retry logic to attempt full download from scratch

### Key Entities

- **URL List**: Represents the input containing URLs to download, includes source file path, total URL count, and format (text or JSON)
- **Page Download**: Represents a single download operation for one URL, includes source URL, destination file path, start time, completion time, bytes transferred, HTTP status code, success/failure status, and retry count
- **Download Session**: Represents a batch download operation across multiple URLs, includes session start time, end time, total URLs, successful downloads, failed downloads, skipped downloads, total bytes transferred, and average download speed
- **Download Configuration**: Represents user-specified settings, includes output directory, rate limit delay, connection timeout, read timeout, max retries, force refresh flag, dry-run flag, and custom HTTP headers
- **Download Result**: Represents the outcome of processing a single URL, includes URL, local file path, status (success/failed/skipped), error message if failed, file size, and timestamps

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can download a single documentation page in under 5 seconds on standard broadband connection
- **SC-002**: System successfully downloads 100 pages sequentially with configured rate limiting (0.5s delay) in under 2 minutes
- **SC-003**: System handles network failures gracefully with clear error messages and continues processing remaining URLs in 100% of batch scenarios
- **SC-004**: System correctly identifies and skips unchanged pages in incremental mode, reducing download time by at least 80% for repeated runs on mostly-unchanged content
- **SC-005**: Users can verify download progress in real-time with updates showing current URL and completion percentage
- **SC-006**: System recovers from interrupted downloads without corrupting existing files 100% of the time
- **SC-007**: Downloaded HTML files maintain human-readable directory structure matching URL paths for easy manual inspection
- **SC-008**: System respects rate limiting to avoid overwhelming remote server, maintaining configured delay between requests with less than 10% variance

## Assumptions

- The Alteryx help site (help.alteryx.com) does not require authentication for documentation pages
- Remote servers support HTTP HEAD requests for checking Last-Modified headers
- Individual documentation pages are typically under 5MB in size (enforced by configurable default limit)
- URL paths follow standard web conventions (no exotic characters beyond what URLencode handles)
- Users have write permissions to the output directory
- Standard HTTP/HTTPS protocols are sufficient (no special proxy requirements)
- Downloaded HTML files do not require JavaScript execution or dynamic content rendering
- The sitemap-filter tool outputs URL lists in plain text format (one URL per line)
- Rate limiting of 0.5-2 seconds between requests is acceptable to help.alteryx.com
- Network bandwidth is sufficient for downloading multiple MB of HTML content per page
- Local filesystem supports nested directory structures up to URL path depth
- HTML content validation is based on Content-Type header, not parsing the entire document
- The RAG pipeline will handle HTML parsing and content extraction in a separate feature (004-page-processor)
