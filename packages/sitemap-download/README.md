# Sitemap Download

Download and validate XML sitemaps with progress tracking, smart incremental updates, and robust retry logic.

## Features

- **Download with Progress**: Real-time progress indication with speed and ETA
- **XML Validation**: SAX-based streaming validation with URL counting
- **Smart Updates**: Skip downloads when remote file hasn't changed (based on Last-Modified)
- **Retry Logic**: Exponential backoff with jitter for transient failures
- **Archive Support**: Preserve existing sitemaps with timestamp suffixes
- **Memory Efficient**: Streaming download and validation (8KB chunks)
- **Configurable**: Timeouts, retries, chunk size, and more

## Installation

This package is part of the uv-ayx-rag workspace:

```bash
# Install workspace (from repository root)
uv sync

# The sitemap-download command is available through main.py
uv run python main.py sitemap-download --help
```

## Usage

### Basic Download

```bash
# Download to default location (alteryx-help-current-sitemap.xml)
uv run python main.py sitemap-download

# Custom destination
uv run python main.py sitemap-download --output my-sitemap.xml

# Custom URL
uv run python main.py sitemap-download \
  --url https://example.com/sitemap.xml \
  --output example-sitemap.xml
```

### Smart Incremental Updates

```bash
# Skip download if remote hasn't changed
uv run python main.py sitemap-download
# Output: ✓ Local sitemap is up-to-date

# Force download even if unchanged
uv run python main.py sitemap-download --force
```

### Archive Existing Files

```bash
# Archive existing sitemap before downloading new version
uv run python main.py sitemap-download --archive
# Creates: alteryx-help-current-sitemap_2025_11_05_14_30.xml
```

### Quiet Mode

```bash
# Minimal output for scripting
uv run python main.py sitemap-download --quiet
# Output: ✓ Sitemap downloaded: 1.4 MB
```

### Timeout Configuration

```bash
# Increase timeouts for slow connections
uv run python main.py sitemap-download \
  --connection-timeout 60 \
  --read-timeout 600
```

### Retry Configuration

```bash
# Customize retry behavior
uv run python main.py sitemap-download --max-retries 5
# Default: 3 retries with exponential backoff (1s, 2s, 4s)
```

## Exit Codes

The CLI returns standard exit codes for scripting:

- `0`: Success (download completed and validated)
- `1`: Download failed (network error, timeout, etc.)
- `2`: Validation failed (malformed XML, empty file)
- `3`: Configuration error (invalid URL, bad parameters)

Example usage in scripts:

```bash
#!/bin/bash
uv run python main.py sitemap-download --quiet

if [ $? -eq 0 ]; then
  echo "Sitemap updated successfully"
  # Continue pipeline...
elif [ $? -eq 2 ]; then
  echo "Validation failed - investigate sitemap source"
  exit 1
else
  echo "Download failed - check network"
  exit 1
fi
```

## Configuration Options

### Command-Line Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--url` | str | `https://help.alteryx.com/current/sitemap.xml` | Source URL |
| `--output` | path | `alteryx-help-current-sitemap.xml` | Destination file |
| `--force` | flag | false | Force download (skip modification check) |
| `--archive` | flag | false | Archive existing file before download |
| `--quiet` | flag | false | Minimal output |
| `--connection-timeout` | int | 30 | Connection timeout (seconds) |
| `--read-timeout` | int | 300 | Read timeout (seconds) |
| `--max-retries` | int | 3 | Maximum retry attempts |

### Environment Configuration

```bash
# Disable SSL verification (not recommended for production)
export PYTHONHTTPSVERIFY=0
```

## API Usage

The package can also be used as a Python library:

```python
from pathlib import Path
from sitemap_download import SitemapDownloader, DownloadConfig

# Configure download
config = DownloadConfig(
    url="https://help.alteryx.com/current/sitemap.xml",
    destination=Path("sitemap.xml"),
    force=False,
    connection_timeout=30.0,
    read_timeout=300.0,
    max_retries=3,
)

# Create downloader
downloader = SitemapDownloader(config)

# Download with progress callback
def show_progress(progress):
    print(f"Downloaded: {progress.downloaded_bytes}/{progress.total_bytes} bytes")

result = downloader.download(progress_callback=show_progress)

if result.success:
    print(f"Downloaded: {result.file_path}")
    print(f"Size: {result.file_size} bytes")
    print(f"URLs: {result.validation_result.url_count}")
else:
    print(f"Failed: {result.error_message}")
```

## Validation

The downloader automatically validates XML structure:

- ✓ Well-formed XML (SAX parser)
- ✓ Valid root element (`<urlset>` or `<sitemapindex>`)
- ✓ Minimum 1 URL entry
- ✓ All entries have `<loc>` element
- ✓ URL count reported

Validation failures return exit code 2 for scripting.

## Retry Logic

Transient failures are automatically retried:

### Retryable Errors
- 5xx server errors
- Connection timeouts
- Network connection errors

### Non-Retryable Errors  
- 4xx client errors (404, 403, etc.)
- Invalid URLs
- Configuration errors

### Retry Strategy
- **Exponential backoff**: 1s, 2s, 4s, 8s delays
- **Jitter**: 25% randomization prevents thundering herd
- **Logging**: Each retry logged with attempt count

## Development

### Run Tests

```bash
# All tests
cd packages/sitemap-download && uv run pytest tests/

# With coverage
cd packages/sitemap-download && uv run pytest --cov=src --cov-report=term-missing

# Specific test file
cd packages/sitemap-download && uv run pytest tests/unit/test_downloader.py -v
```

### Test Structure

```
tests/
├── fixtures/          # Test XML files
│   ├── sample_sitemap.xml
│   ├── malformed_sitemap.xml
│   └── empty_sitemap.xml
├── integration/       # End-to-end tests
│   ├── test_cli.py
│   └── test_performance.py
└── unit/             # Unit tests
    ├── test_downloader.py
    ├── test_validator.py
    ├── test_models.py
    └── test_cli.py
```

### Code Coverage

Current coverage: **95%+**

```bash
cd packages/sitemap-download && uv run pytest --cov=src --cov-report=html
# Open htmlcov/index.html in browser
```

## Architecture

### Components

- **`downloader.py`**: HTTP download engine with retry logic
- **`validator.py`**: SAX-based XML validation
- **`models.py`**: Data models (config, progress, results)
- **`cli.py`**: Command-line interface
- **`utils.py`**: Utility functions (archive, format)
- **`exceptions.py`**: Custom exception classes

### Design Principles

- **Streaming**: Memory-efficient processing (8KB chunks)
- **Atomic writes**: Temp file + rename for crash safety
- **Separation of concerns**: Download, validate, display
- **TDD**: Comprehensive test suite (56 tests)

## Troubleshooting

### Download Failures

```bash
# Check network connectivity
curl -I https://help.alteryx.com/current/sitemap.xml

# Increase timeouts
uv run python main.py sitemap-download \
  --connection-timeout 60 \
  --read-timeout 600

# Increase retries
uv run python main.py sitemap-download --max-retries 5
```

### Validation Failures

```bash
# Check XML structure manually
xmllint --noout sitemap.xml

# View validation details
uv run python main.py sitemap-download --force
# Validation errors are displayed in output
```

### SSL Certificate Errors

```bash
# Temporary workaround (not recommended for production)
export PYTHONHTTPSVERIFY=0
uv run python main.py sitemap-download
```

## License

Part of the uv-ayx-rag project.
