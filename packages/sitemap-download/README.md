# Sitemap Download

Download the Alteryx help sitemap from https://help.alteryx.com/current/sitemap.xml with progress indication, validation, and incremental update support.

## Features

- Download sitemap with real-time progress updates
- XML validation before saving
- Incremental updates (skip download if remote unchanged)
- Retry logic with exponential backoff
- Configurable timeouts and chunk size

## Usage

```bash
# Download sitemap (default location: alteryx-help-current-sitemap.xml)
uv run python main.py sitemap-download

# Force download (skip modification date check)
uv run python main.py sitemap-download --force

# Custom destination
uv run python main.py sitemap-download --output custom-sitemap.xml
```

## Development

```bash
# Install dependencies
uv sync

# Run tests
cd packages/sitemap-download && uv run pytest tests/

# Run with coverage
cd packages/sitemap-download && uv run pytest --cov=sitemap_download tests/
```
