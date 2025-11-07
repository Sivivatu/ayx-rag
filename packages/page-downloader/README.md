# Page Downloader (v0.3.0)

Download HTML pages from Alteryx Help for downstream RAG processing. Supports single URL and batch mode from a file, with structured logging, progress summary, and rate limiting.

## Features

- Single URL or file input (batch)
- URL → directory structure (`current/en/designer/tools.html`)
- HTML-only validation (skips non-HTML)
- Force re-download with `--force`
- Rate limiting with `--delay`
- Quiet mode for scripts, verbose logging for debugging
- Standard exit codes (0/1/2/3)

## CLI Usage

```bash
# Single URL
uv run python main.py page-downloader https://help.alteryx.com/current/en/designer/tools.html \
  --output-dir downloads

# Batch mode (one URL per line)
uv run python main.py page-downloader path/to/urls.txt \
  --output-dir downloads --delay 0.25 --quiet

# Dry run (no writes)
uv run python main.py page-downloader https://help.alteryx.com/current/en/designer/test.html \
  --dry-run
```

## Options

- `--output-dir, -o`: Output directory (default: `downloads`)
- `--max-file-size`: Maximum bytes (default: 5MB)
- `--connection-timeout`: Seconds (default: 30)
- `--read-timeout`: Seconds (default: 300)
- `--max-retries`: Attempts (default: 3)
- `--force, -f`: Re-download even if exists
- `--dry-run`: Preview actions only
- `--no-verify-ssl`: Disable SSL verification (dev/testing)
- `--verbose, -v`: Detailed logs
- `--quiet, -q`: Suppress progress (batch)
- `--delay`: Seconds between requests (batch)

## Exit Codes

- `0`: Success
- `1`: Download failure
- `2`: Validation/Skipped (e.g., non-HTML)
- `3`: Configuration error

## Logging (FR-017)

Verbose mode adds structured logs to stderr with timestamp, level, module, function, line, and message. Successful downloads log the target URL, destination path, and byte count.

## Summary (Batch)

After batch, a summary is printed:

```
Batch Summary:
  Total:    <n>
  Success:  <n>
  Failed:   <n>
  Skipped:  <n>
  Invalid:  <n>   # when applicable
  Duration: <sec>s
```

## Notes

- Only HTML content is saved; non-HTML responses are skipped with exit code 2.
- Paths are derived from URL (query/fragment stripped) to maintain source attribution.
- Respect robots.txt in future phases (planned FR-024).

## Testing

```bash
# Run only page-downloader tests
uv run pytest packages/page-downloader/tests -q

# E2E tests via main.py
uv run pytest tests/test_e2e_page_downloader.py -q
```
