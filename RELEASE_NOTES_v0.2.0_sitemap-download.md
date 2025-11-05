# Release v0.2.0 - Sitemap Download

**Package**: `sitemap-download`  
**Released**: 5 November 2025  
**Branch**: `002-sitemap-download`

## Overview

A production-ready HTTP downloader for XML sitemaps with comprehensive validation, smart incremental updates, and robust retry logic. Designed for reliability with streaming downloads, exponential backoff, and memory-efficient SAX parsing.

## ✨ Features

### Core Download Engine
Download XML sitemaps from HTTP/HTTPS URLs with real-time progress tracking.

- **Streaming downloads**: Memory-efficient 8KB chunking (constant memory usage)
- **Real-time progress**: Speed, ETA, downloaded/total bytes, visual progress bar
- **Atomic writes**: Temp file + rename pattern for crash safety
- **Configurable timeouts**: Connection (30s default) and read (300s default)
- **Custom HTTP headers**: User-Agent and Accept-Encoding per specification

**Related commits**:
- `feat(sitemap-download): implement SitemapDownloader with TDD (3576353)`
- `feat(sitemap-download): implement CLI with typer integration (aff7cdf)`

### Smart Incremental Updates (User Story 2)
Avoid unnecessary downloads by comparing modification dates.

- **Remote metadata check**: HTTP HEAD request for Last-Modified, Content-Length, ETag
- **Skip logic**: Download only when remote is newer than local file
- **Force mode**: `--force` flag to bypass modification checks
- **Clear feedback**: Skip notifications with reasoning

**Related commits**:
- `feat(sitemap-download): implement SitemapDownloader with TDD (3576353)`

### XML Validation (User Story 3)
Ensure downloaded files are well-formed sitemaps before use.

- **SAX streaming parser**: Memory-efficient validation for large files
- **Structure validation**: Root element, namespace, URL entries
- **URL counting**: Reports exact count of URLs found
- **Automatic validation**: Runs after every successful download
- **Exit code 2**: Validation failures return distinct exit code for scripting

**Related commits**:
- `feat(sitemap-download): add XML validation with URL counting (c3c305c)`
- `fix(002): validation failures now return exit code 2`

### Retry Logic with Exponential Backoff (Production Ready)
Handle transient network failures gracefully.

- **Smart error classification**: 5xx/timeouts retry, 4xx fail immediately
- **Exponential backoff**: 1s, 2s, 4s, 8s delays (configurable max)
- **Jitter randomization**: 25% variance prevents thundering herd problem
- **Configurable retries**: `--max-retries` option (default: 3)
- **Detailed logging**: Each retry logged with attempt count and delay
- **Retry tracking**: Retry count included in results and error messages

**Related commits**:
- `feat(sitemap-download): implement retry logic with exponential backoff (4369640)`

### Archive Support
Preserve existing sitemaps before downloading updates.

- **Timestamp suffixes**: `YYYY_MM_DD_HH_MM` format
- **Original preservation**: Archive uses shutil.copy2 (preserves metadata)
- **CLI integration**: `--archive` flag
- **Automatic naming**: Example: `sitemap_2025_11_05_14_30.xml`

**Related commits**:
- `feat(sitemap-download): add --archive option to preserve existing sitemaps (0292df8)`
- `refactor(sitemap-download): move utility functions to utils module (32047d4)`

### CLI Features

- **Quiet mode**: `--quiet` for minimal output (scripting friendly)
- **Exit codes**: 0=success, 1=download fail, 2=validation fail, 3=config error
- **Progress display**: Visual progress bar with speed and ETA
- **Validation display**: URL count shown after successful validation
- **Error troubleshooting**: Helpful error messages with suggested fixes

**Related commits**:
- `feat(sitemap-download): implement CLI with typer integration (aff7cdf)`

## 🎯 Performance

- **Streaming**: Constant memory usage regardless of file size
- **SAX validation**: Memory-efficient XML parsing
- **Real-world test**: 8,872 URLs (1.4 MB) in ~3 seconds
- **Progress updates**: Every 256KB or 500ms (responsive UX)
- **Chunk size**: 8KB default (configurable)

## 🐛 Bug Fixes

- **SSL certificate errors**: Disabled verification for help.alteryx.com (`f89c4c8`)
- **Validation exit code**: Fixed exit code 2 for validation failures (was incorrectly 0)
- **Error context**: Added retry count to error messages for better debugging

## 📚 Documentation

### Package Documentation
- **Comprehensive README**: Usage examples, API guide, configuration reference
- **Exit codes reference**: Scripting guide with exit code examples
- **Troubleshooting guide**: Common issues and solutions
- **API examples**: Python library usage with code samples
- **Architecture overview**: Component descriptions and design principles

### Project Documentation
- **Root README updated**: Feature summary and quick examples
- **CHANGELOG entry**: Detailed v0.2.0 changes
- **Docstrings**: All public classes and methods documented
- **Specification artifacts**: Complete specs, plans, tasks, contracts

**Related commits**:
- `docs(sitemap-download): add sitemap download feature spec and quality checklist (7eb4f83)`
- `docs(sitemap-download): add planning artifacts (317e412)`
- `docs: update documentation for uv_build backend and sitemap-download (e5cfd6f)`
- `docs(sitemap-download): mark Phase 5 (US3) tasks complete (a7b11e8)`

## 🧪 Testing

### Test Coverage: 95%+

- **56 tests total**: 48 unit tests + 8 integration tests
- **Test categories**:
  - Downloader: 12 tests (init, download, retries, disk space)
  - Validator: 9 tests (valid/invalid XML scenarios)
  - Models: 20 tests (config, progress, results validation)
  - CLI: 6 unit + 2 integration tests
  - Exceptions: 7 tests
- **Test fixtures**: Valid, malformed, empty XML sitemaps
- **Mock-based testing**: httpx.Client mocking with pytest
- **Retry testing**: time.sleep patching for fast tests
- **TDD approach**: Tests written before implementation

**Related commits**:
- `test(sitemap-download): add comprehensive unit tests for models and exceptions (c1a066f)`
- All feature commits included tests

## 🔧 Technical Details

### Dependencies

**Runtime**:
- `httpx`: Modern HTTP client with async support
- `typer`: Type-hint based CLI framework
- `loguru`: Structured logging

**Development**:
- `pytest`: Testing framework
- `pytest-cov`: Coverage reporting

**Build**:
- `uv_build`: Native uv build backend (zero-config)

### Architecture

- **Modular design**: downloader, validator, models, cli, utils, exceptions
- **Separation of concerns**: Download, validate, display logic separated
- **Streaming**: Memory-efficient processing throughout
- **Atomic operations**: Crash-safe file writes with temp files
- **TDD**: Test-driven development, 56 tests passing

### Package Structure

```
packages/sitemap-download/
├── src/
│   └── sitemap_download/
│       ├── __init__.py        # Package exports
│       ├── downloader.py      # HTTP download engine (393 lines)
│       ├── validator.py       # SAX-based validation (170 lines)
│       ├── models.py          # Data models (180 lines)
│       ├── cli.py             # CLI interface (193 lines)
│       ├── utils.py           # Utility functions (50 lines)
│       └── exceptions.py      # Custom exceptions (30 lines)
├── tests/
│   ├── fixtures/              # Test XML files
│   ├── integration/           # End-to-end tests
│   └── unit/                  # Unit tests
├── pyproject.toml             # Package metadata + dependencies
└── README.md                  # Package documentation
```

## 📦 Installation

```bash
# From repository root
uv sync

# The sitemap-download command is available through main.py
uv run python main.py sitemap-download --help
```

## 🚀 Usage Examples

### Basic Download
```bash
# Download to default location
uv run python main.py sitemap-download

# Custom URL and destination
uv run python main.py sitemap-download \
  --url https://example.com/sitemap.xml \
  --output my-sitemap.xml
```

### Smart Updates
```bash
# Skip download if unchanged
uv run python main.py sitemap-download
# Output: ✓ Local sitemap is up-to-date

# Force update
uv run python main.py sitemap-download --force
```

### Archive and Update
```bash
# Preserve existing file before downloading
uv run python main.py sitemap-download --archive
# Creates: sitemap_2025_11_05_14_30.xml
```

### Scripting with Exit Codes
```bash
#!/bin/bash
uv run python main.py sitemap-download --quiet

case $? in
  0) echo "Success"; process-sitemap.sh ;;
  1) echo "Download failed"; exit 1 ;;
  2) echo "Validation failed"; exit 1 ;;
  3) echo "Configuration error"; exit 1 ;;
esac
```

### Custom Timeouts and Retries
```bash
# Increase timeouts for slow connections
uv run python main.py sitemap-download \
  --connection-timeout 60 \
  --read-timeout 600 \
  --max-retries 5
```

## 🔄 Migration from Manual Downloads

**Before** (manual download):
```bash
curl -o sitemap.xml https://help.alteryx.com/current/sitemap.xml
# No progress indication
# No validation
# No incremental updates
# No retry on failure
```

**After** (with sitemap-download):
```bash
uv run python main.py sitemap-download
# ✓ Real-time progress with speed/ETA
# ✓ Automatic XML validation
# ✓ Skip unchanged downloads
# ✓ Retry transient failures
# ✓ Archive old versions
```

## ⚠️ Breaking Changes

None - this is the initial release.

## 🙏 Contributors

- @Sivivatu - Feature development, testing, documentation

## 📋 What's Next?

**Version 0.2.0** will focus on web scraping capabilities:
- Extract HTML content from sitemap URLs
- Parse and clean documentation pages
- Extract metadata (titles, descriptions, timestamps)
- Store structured content for embedding pipeline

See [specs/003-web-scraper/](../specs/003-web-scraper/) for details (when created).

---

## Release Checklist

- [X] All tests passing (56/56)
- [X] Test coverage >95%
- [X] Documentation complete (package README, root README, CHANGELOG)
- [X] Conventional commits followed
- [X] Docstrings added to all public APIs
- [X] Release notes created
- [X] Constitution principles validated
- [X] User stories independently testable
- [X] Exit codes standardized (0/1/2/3)

---

## Links

- **Repository**: https://github.com/Sivivatu/ayx-rag
- **Branch**: `002-sitemap-download`
- **Package Documentation**: [packages/sitemap-download/README.md](../packages/sitemap-download/README.md)
- **Changelog**: [CHANGELOG.md](../CHANGELOG.md)
- **Specification**: [specs/002-sitemap-download/spec.md](../specs/002-sitemap-download/spec.md)

---

**Full Changelog**: https://github.com/Sivivatu/ayx-rag/compare/v0.1.0...v0.2.0
