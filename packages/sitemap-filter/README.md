# Sitemap Filter

Filter Alteryx help documentation sitemap URLs by language and product for targeted data processing.

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-77%20passing-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-96%25-brightgreen.svg)](tests/)

## Overview

A command-line tool for filtering XML sitemaps from Alteryx help documentation (help.alteryx.com). Filter by language (8 languages supported), product (12+ products), or combine both with flexible AND/OR logic. Output to JSON, text, or XML formats.

**Use Case**: Process the 8,864-URL Alteryx sitemap to extract only the documentation you need - for example, just English Designer docs (654 URLs) instead of all 8,864 URLs.

## Features

- ✅ **Language Filtering**: Filter by 8 languages (en, de, es, fr, it, ja, pt, zh-CHS) or all
- ✅ **Product Filtering**: Filter by product paths (designer, server, connect, etc.)
- ✅ **Combined Filters**: Use both language AND product filters with OR logic within each type
- ✅ **Multiple Output Formats**: JSON (with metadata), plain text, or XML sitemap
- ✅ **File Output**: Write results to file or stdout
- ✅ **Dry Run Mode**: Preview statistics without generating output
- ✅ **Performance**: Processes 8,864 URLs in ~0.1s, 1,200 URLs in 0.014s
- ✅ **Validation**: File size warnings, malformed XML detection

## Quick Start

### Installation

```bash
# From the workspace root
cd packages/sitemap-filter

# Install dependencies (uv handles this automatically)
uv sync
```

### Basic Usage

```bash
# Filter to English URLs only
uv run python -m sitemap_filter.cli sitemap.xml --language en

# Filter to German Designer URLs
uv run python -m sitemap_filter.cli sitemap.xml --language de --product designer

# Multiple products (OR logic)
uv run python -m sitemap_filter.cli sitemap.xml --language en --product designer --product server

# Output to JSON file
uv run python -m sitemap_filter.cli sitemap.xml --language en --format json --output results.json

# Preview statistics without output (dry run)
uv run python -m sitemap_filter.cli sitemap.xml --language en --product designer --dry-run

# Get all URLs (no filtering)
uv run python -m sitemap_filter.cli sitemap.xml --language all
```

### Via Main Entry Point

From the workspace root:

```bash
uv run main.py sitemap.xml --language en --product designer
```

## Command Reference

```
Usage: sitemap_filter.cli [OPTIONS] SITEMAP_FILE

Arguments:
  SITEMAP_FILE  Path to XML sitemap file to filter [required]

Options:
  -l, --language TEXT   Filter by language code (en, de, es, fr, it, ja, pt, 
                        zh-CHS, all). Defaults to 'en'. Use 'all' for all 
                        languages. [default: en]
  -p, --product TEXT    Filter by product path segment. Can specify multiple 
                        times.
  -f, --format TEXT     Output format: json, text, or xml [default: text]
  -o, --output PATH     Write output to file instead of stdout
  --dry-run            Show statistics without outputting URLs
  --help               Show this message and exit.
```

## Output Formats

### JSON Format
```json
{
  "total_urls": 10,
  "filtered_urls": 5,
  "results": [
    {
      "url": "https://help.alteryx.com/current/en/designer.html",
      "lastmod": "2025-10-23"
    }
  ]
}
```

### Text Format
```
https://help.alteryx.com/current/en/designer.html
https://help.alteryx.com/current/en/designer/tools.html
https://help.alteryx.com/current/en/server.html
```

### XML Format
```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://help.alteryx.com/current/en/designer.html</loc>
    <lastmod>2025-10-23</lastmod>
  </url>
</urlset>
```

## Supported Languages

- `en` - English
- `de` - German (Deutsch)
- `es` - Spanish (Español)
- `fr` - French (Français)
- `it` - Italian (Italiano)
- `ja` - Japanese (日本語)
- `pt` - Portuguese (Português)
- `zh-CHS` - Chinese Simplified (简体中文)
- `all` - All languages (no filtering)

## Supported Products

- `designer` - Alteryx Designer
- `server` - Alteryx Server
- `connect` - Alteryx Connect
- `predictive-tools` - Predictive Tools
- `intelligence` - Intelligence Suite
- `auto-insights` - Auto Insights
- `promote` - Promote
- `admin` - Admin features
- `gallery` - Gallery
- `schedules` - Schedules
- `data-sources` - Data Sources
- `cloud` - Cloud features

## Filter Logic

- **Language AND Product**: Both criteria must match (AND logic across types)
- **Multiple Languages**: Any language matches (OR logic within type)
- **Multiple Products**: Any product matches (OR logic within type)

**Example**: `--language en --language de --product designer --product server`
- Returns: (English OR German) AND (Designer OR Server)

## Examples

### Example 1: Extract English Designer Documentation
```bash
uv run python -m sitemap_filter.cli alteryx-help-sitemap.xml \
  --language en \
  --product designer \
  --format json \
  --output designer-en.json
```

**Result**: 654 English Designer URLs saved to `designer-en.json`

### Example 2: Get All German Documentation URLs
```bash
uv run python -m sitemap_filter.cli alteryx-help-sitemap.xml \
  --language de \
  --format text \
  --output german-urls.txt
```

### Example 3: Preview Statistics Before Processing
```bash
uv run python -m sitemap_filter.cli alteryx-help-sitemap.xml \
  --language en \
  --product designer \
  --product server \
  --dry-run
```

**Output** (to stderr):
```
2025-10-31 15:26:33.243 | INFO | Processing sitemap: alteryx-help-sitemap.xml
2025-10-31 15:26:33.328 | INFO | Parsed 8864 URL entries from sitemap
2025-10-31 15:26:33.330 | INFO | Applying filters: languages=['en'], products=['designer', 'server']
2025-10-31 15:26:33.332 | INFO | Total URLs: 8864
2025-10-31 15:26:33.332 | INFO | Filtered URLs: 892
2025-10-31 15:26:33.332 | INFO | Dry run complete - no output generated
```

### Example 4: Multiple Languages for Translation Workflow
```bash
uv run python -m sitemap_filter.cli alteryx-help-sitemap.xml \
  --language en \
  --language de \
  --language fr \
  --product designer \
  --format xml \
  --output multilingual-designer.xml
```

## Performance

- **Small sitemap** (10 URLs): < 0.001s
- **Medium sitemap** (1,200 URLs): 0.014s
- **Large sitemap** (8,864 URLs): ~0.1s
- **Memory usage**: < 50MB for typical sitemaps

Performance tested on 1,200-URL sitemap with language and product filters.

## Development

### Running Tests

```bash
# All tests
uv run pytest tests/

# With coverage
uv run pytest tests/ --cov=src/sitemap_filter --cov-report=term-missing

# Specific test file
uv run pytest tests/unit/test_language_filter.py -v

# Performance tests only
uv run pytest tests/integration/test_performance.py -v
```

### Test Coverage

- **Overall**: 96% coverage
- **77 tests**: All passing
- **Test Categories**:
  - Unit tests: 56 tests (parser, language, product, filters, output)
  - Integration tests: 16 tests (CLI functionality)
  - Performance tests: 5 tests (speed validation)

### Project Structure

```
packages/sitemap-filter/
├── src/
│   └── sitemap_filter/
│       ├── __init__.py          # Package exports
│       ├── cli.py               # CLI entry point
│       └── filters/
│           ├── __init__.py      # FilterCriteria, apply_filters
│           ├── parser.py        # XML parsing, URLEntry
│           ├── language.py      # Language detection & filtering
│           ├── product.py       # Product extraction & filtering
│           └── output.py        # Output formatters (JSON/text/XML)
├── tests/
│   ├── fixtures/
│   │   ├── sample_sitemap.xml
│   │   ├── malformed_sitemap.xml
│   │   └── large_sitemap.xml
│   ├── unit/                    # Unit tests for each module
│   └── integration/             # CLI and performance tests
├── pyproject.toml               # Dependencies and metadata
└── README.md                    # This file
```

## Architecture

### Data Flow

```
XML Sitemap → Parser → URLEntry objects → Filters → Formatter → Output
```

### Key Components

1. **Parser** (`filters/parser.py`)
   - Parses XML sitemap using ElementTree
   - Creates URLEntry dataclass instances
   - Detects language from URL patterns
   - Extracts product path segments

2. **Filters** (`filters/language.py`, `filters/product.py`, `filters/__init__.py`)
   - Language filter: Matches against detected language codes
   - Product filter: Matches against extracted product paths
   - Combined filter: Applies AND/OR logic across filter types

3. **Formatters** (`filters/output.py`)
   - JSON: Structured output with metadata
   - Text: One URL per line
   - XML: Valid sitemap with filtered URLs

4. **CLI** (`cli.py`)
   - Typer-based command-line interface
   - Argument validation and error handling
   - Performance logging and statistics
   - File size warnings

## Error Handling

The tool provides clear error messages for common issues:

- **File not found**: Exit code 2 with error message
- **Malformed XML**: Exit code 1 with parsing error details
- **Invalid format**: Exit code 1 with supported formats listed
- **Large file warning**: Warns for sitemaps > 10MB

## Logging

Uses loguru for structured logging to stderr:

- **INFO**: Processing steps, statistics, completion
- **DEBUG**: Detailed timing information (parsing, filtering, output)
- **WARNING**: Large files, missing language detection
- **ERROR**: File errors, XML parsing failures

## Contributing

### Development Workflow

1. Write tests first (TDD required)
2. Implement feature
3. Verify tests pass with coverage
4. Update documentation
5. Follow Conventional Commits format

### Commit Format

```
type(scope): description

[optional body]
```

Types: `feat`, `fix`, `test`, `docs`, `refactor`, `perf`, `chore`

## Version History

### v0.2.0 (2025-10-31)
- Initial release
- Language filtering (8 languages)
- Product filtering (12+ products)
- Combined filters with AND/OR logic
- Multiple output formats (JSON, text, XML)
- File output support
- Dry-run mode
- Performance logging
- 96% test coverage

## License

Part of the uv-ayx-rag project. See root LICENSE file for details.

## Links

- [Project Root](../../README.md)
- [Specification](../../specs/001-sitemap-filter/spec.md)
- [Implementation Plan](../../specs/001-sitemap-filter/plan.md)
- [Task Breakdown](../../specs/001-sitemap-filter/tasks.md)
