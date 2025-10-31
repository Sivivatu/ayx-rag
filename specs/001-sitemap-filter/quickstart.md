# Quickstart: Sitemap Filter CLI

**Feature**: 001-sitemap-filter  
**Audience**: Developers  
**Time to Complete**: 5 minutes  
**Version**: v0.2.0

## Prerequisites

- Python 3.10+ installed
- `uv` package manager installed (dependencies auto-synced)
- Alteryx sitemap file: `alteryx-help-current-sitemap.xml` (in workspace root)

---

## Quick Start

### 1. Run via Main Entry Point (Recommended)

Filter English documentation URLs:

```bash
uv run main.py alteryx-help-current-sitemap.xml --language en
```

### 2. Or Run from Feature Package

```bash
cd packages/sitemap-filter
uv run python -m sitemap_filter.cli ../../alteryx-help-current-sitemap.xml --language en
```

**Expected Output** (text format, default):
```
https://help.alteryx.com/current/en/designer.html
https://help.alteryx.com/current/en/designer/tools.html
...
```

**For JSON output** (add `--format json`):
```json
{
  "total_urls": 8864,
  "filtered_urls": 1234,
  "filters": {
    "languages": ["en"],
    "products": []
  },
  "urls": [
    {
      "loc": "https://help.alteryx.com/current/en/designer.html",
      "lastmod": "2025-10-23"
    },
    ...
  ]
}
```

---

## Common Use Cases

### Get English URLs Only

```bash
uv run main.py alteryx-help-current-sitemap.xml \
  --language en > english-urls.txt
```

**Result**: Plain text file with one URL per line (text is default format)

---

### Get Designer Documentation

```bash
uv run main.py alteryx-help-current-sitemap.xml \
  --product designer \
  --format json \
  --output designer-docs.json
```

**Result**: JSON file with Designer documentation URLs

---

### Get English Designer Docs

```bash
uv run main.py alteryx-help-current-sitemap.xml \
  --language en \
  --product designer \
  --format xml \
  --output english-designer-sitemap.xml
```

**Result**: Valid sitemap XML with filtered URLs

---

### Check Filter Statistics

```bash
uv run main.py alteryx-help-current-sitemap.xml \
  --language en \
  --product designer \
  --dry-run
```

**Result** (stderr logging):
```
2025-10-31 12:34:56 | INFO | Processing sitemap: alteryx-help-current-sitemap.xml
2025-10-31 12:34:56 | INFO | Parsing complete - 8864 URLs found (0.05s)
2025-10-31 12:34:56 | INFO | Filtering complete - 1234 URLs matched (0.01s)
2025-10-31 12:34:56 | INFO | Filter: Languages=['en'], Products=['designer']
2025-10-31 12:34:56 | INFO | Total execution time: 0.06s
```

---

## Command-Line Reference

### Basic Syntax

```bash
uv run main.py <sitemap-file> [OPTIONS]
```

### Key Options

| Option | Description | Example |
|--------|-------------|---------|
| `--language LANG` or `-l` | Filter by language (8 supported + 'all') | `-l en` |
| `--product PROD` or `-p` | Filter by product (12+ supported) | `-p designer` |
| `--format FMT` or `-f` | Output format: text (default), json, xml | `-f json` |
| `--output FILE` or `-o` | Write to file | `-o results.txt` |
| `--dry-run` | Show stats only (no output) | `--dry-run` |
| `--help` or `-h` | Show help | `--help` |
| `--version` | Show version | `--version` |

### Supported Languages

`en`, `de`, `es`, `fr`, `it`, `ja`, `pt`, `zh-CHS`, `all`

### Supported Products

`designer`, `server`, `connect`, `promote`, `intelligence-suite`, `predictive-tools`, `prescriptive-tools`, `machine-learning`, `auto-insights`, `data-profiling`, `location-intelligence`, `python-sdk`

### Multiple Filters

Use multiple `--language` or `--product` flags for OR logic within that type:

```bash
# Get English OR German URLs
uv run main.py alteryx-help-sitemap.xml -l en -l de

# Get Designer OR Server docs
uv run main.py alteryx-help-sitemap.xml -p designer -p server
```

Combine different filter types for AND logic:

```bash
# Get (English OR German) AND (Designer OR Server)
uv run main.py alteryx-help-sitemap.xml \
  -l en -l de \
  -p designer -p server
```

---

## Output Formats

### Text (default)

```bash
uv run main.py sitemap.xml -l en
```

Produces one URL per line (great for piping):
```
https://help.alteryx.com/current/en/designer.html
https://help.alteryx.com/current/en/designer/tools.html
```

### JSON

```bash
uv run main.py sitemap.xml -l en -f json
```

Produces structured JSON with metadata:
```json
{
  "total_urls": 8864,
  "filtered_urls": 1234,
  "filters": {
    "languages": ["en"],
    "products": []
  },
  "urls": [
    {
      "loc": "https://help.alteryx.com/current/en/designer.html",
      "lastmod": "2025-10-23"
    }
  ]
}
```

### XML Sitemap

```bash
uv run main.py sitemap.xml -l en -f xml
```

Produces valid sitemap XML:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://help.alteryx.com/current/en/designer.html</loc>
    <lastmod>2025-10-23</lastmod>
  </url>
</urlset>
```

---

## Integration Examples

### Count Filtered URLs

```bash
uv run main.py sitemap.xml -l en | wc -l
```

### Extract URLs to Array in Shell

```bash
urls=$(uv run main.py sitemap.xml -l en)
```

### Process with jq

```bash
uv run main.py sitemap.xml -l en -f json | \
  jq '.urls[] | select(.lastmod > "2025-10-01") | .loc'
```

### Feed to Scraper

```bash
uv run main.py sitemap.xml -l en -p designer | \
  xargs -I {} python src/scraper.py {}
```

---

## Troubleshooting

### File Not Found

**Error**: `Error: Sitemap file not found: sitemap.xml`

**Solution**: Check file path is correct. Use absolute path if needed:
```bash
uv run main.py /workspaces/uv-ayx-rag/alteryx-help-current-sitemap.xml -l en
```

### Invalid Language Code

**Error**: `Invalid value for '--language' / '-l': 'xx' is not one of...`

**Solution**: Use valid language codes: `en`, `de`, `es`, `fr`, `it`, `ja`, `pt`, `zh-CHS`, or `all`
```bash
uv run main.py sitemap.xml -l en
```

### Invalid Product

**Error**: `Invalid value for '--product' / '-p': 'invalid' is not one of...`

**Solution**: Use valid product identifiers. See supported products list above.

### Malformed XML

**Error**: `Error parsing sitemap: mismatched tag`

**Solution**: Verify XML file is valid. Check with:
```bash
xmllint --noout sitemap.xml
```

### No Matches Found

**Output**: Empty results

**Solution**: Check filter criteria. Verify products/languages exist in sitemap:
```bash
# Check without filters to see available data
uv run main.py sitemap.xml --dry-run
```

### Large File Warning

**Warning**: `Large sitemap file detected (12.5 MB). Processing may take longer.`

**Solution**: This is informational only. Processing will continue normally.

---

## Performance Notes

- **Small datasets** (<100 URLs): Instant (<0.01s)
- **Medium datasets** (1k-10k URLs): <0.1 second
- **Large datasets** (8k-9k URLs like Alteryx sitemap): ~0.1-0.15 seconds
- **Very large** (35k+ URLs): ~0.3-0.5 seconds

Memory usage scales linearly: ~50MB typical for 8k URLs

Target performance: <3 seconds for all operations (current: well under 1s)

---

## Next Steps

### Development Workflow

1. **Write tests first** (TDD required by constitution):
   ```bash
   cd packages/sitemap-filter
   
   # Create test file
   touch tests/unit/test_new_feature.py
   
   # Write failing test
   # Implement feature
   # Verify test passes
   ```

2. **Run tests**:
   ```bash
   cd packages/sitemap-filter
   uv run pytest tests/ -v
   ```

3. **Check coverage**:
   ```bash
   cd packages/sitemap-filter
   uv run pytest --cov=src/sitemap_filter --cov-report=term-missing
   ```

### Extend Functionality

- Add new output formats in `packages/sitemap-filter/src/sitemap_filter/filters/output.py`
- Add new filter types in `packages/sitemap-filter/src/sitemap_filter/filters/`
- Add new language codes in `packages/sitemap-filter/src/sitemap_filter/cli.py`

### Integration

Use this tool as the first stage in your RAG pipeline:

```bash
# Step 1: Filter to English Designer docs
uv run main.py alteryx-help-current-sitemap.xml \
  -l en -p designer -o urls.txt

# Step 2: Scrape filtered URLs (future feature)
cat urls.txt | xargs -P 10 -I {} python -m web_scraper {}

# Step 3: Process documents (future feature)
python -m doc_processor scraped_docs/

# Step 4: Generate embeddings (future feature)
python -m embeddings processed_docs/
```

---

## Help & Support

### Get Help

```bash
uv run main.py --help
```

### Check Version

```bash
uv run main.py --version
```

---

## Testing Your Installation

Run the full test suite:

```bash
cd packages/sitemap-filter
uv run pytest tests/ -v
```

Expected output:
```
==================== test session starts ====================
collected 77 items

tests/unit/test_language_filter.py .................... [ 29%]
tests/unit/test_product_filter.py ..................... [ 58%]
tests/unit/test_combined_filters.py ................... [ 71%]
tests/unit/test_parser.py ............................. [ 84%]
tests/unit/test_output.py ............................. [ 92%]
tests/integration/test_cli.py ..................        [ 98%]
tests/integration/test_performance.py .....              [100%]

==================== 77 passed in 0.37s ====================
```

Quick smoke test:

```bash
# Should show help without errors
uv run main.py --help

# Should output version
uv run main.py --version

# Should filter successfully
uv run main.py alteryx-help-current-sitemap.xml -l en --dry-run
```

---

## Quick Reference Card

```bash
# English URLs only (text output, default)
uv run main.py sitemap.xml -l en

# Designer docs only (JSON output)
uv run main.py sitemap.xml -p designer -f json

# English Designer docs, text output (default)
uv run main.py sitemap.xml -l en -p designer

# Multiple languages (English OR German)
uv run main.py sitemap.xml -l en -l de

# Multiple products (Designer OR Server)
uv run main.py sitemap.xml -p designer -p server

# All languages
uv run main.py sitemap.xml -l all

# Save to file (text format)
uv run main.py sitemap.xml -l en -o output.txt

# Show statistics only (dry run)
uv run main.py sitemap.xml -l en --dry-run

# XML output
uv run main.py sitemap.xml -l en -f xml

# Pipe to other tools (text format ideal for piping)
uv run main.py sitemap.xml -l en | head -10

# Complex filter: (English OR German) AND (Designer OR Server)
uv run main.py sitemap.xml -l en -l de -p designer -p server
```

---

## Additional Resources

- **Feature README**: [packages/sitemap-filter/README.md](../../packages/sitemap-filter/README.md)
- **Specification**: [spec.md](spec.md)
- **Implementation Plan**: [plan.md](plan.md)
- **Task Tracking**: [tasks.md](tasks.md)
- **Project CHANGELOG**: [../../CHANGELOG.md](../../CHANGELOG.md)
- **Release Notes**: [../../RELEASE_NOTES_v0.2.0.md](../../RELEASE_NOTES_v0.2.0.md)
