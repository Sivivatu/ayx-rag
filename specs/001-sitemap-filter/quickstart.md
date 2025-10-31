# Quickstart: Sitemap Filter CLI

**Feature**: 001-sitemap-filter  
**Audience**: Developers  
**Time to Complete**: 5 minutes

## Prerequisites

- Python 3.10+ installed
- `uv` package manager installed
- Dependencies: `uv add typer loguru` and `uv add --dev pytest`
- Alteryx sitemap file: `alteryx-help-current-sitemap.xml`

---

## Quick Start

### 1. Run the Script

Filter English documentation URLs:

```bash
uv run python src/sitemap_filter.py alteryx-help-current-sitemap.xml --language en
```

**Expected Output**:
```json
{
  "total_urls": 35460,
  "filtered_urls": 17823,
  "results": [
    {
      "url": "https://help.alteryx.com/current/designer.html",
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
uv run python src/sitemap_filter.py alteryx-help-current-sitemap.xml \
  --language en \
  --format txt > english-urls.txt
```

**Result**: Plain text file with one URL per line

---

### Get Designer Documentation

```bash
uv run python src/sitemap_filter.py alteryx-help-current-sitemap.xml \
  --product designer \
  --output designer-docs.json
```

**Result**: JSON file with Designer documentation URLs

---

### Get English Designer Docs

```bash
uv run python src/sitemap_filter.py alteryx-help-current-sitemap.xml \
  --language en \
  --product designer \
  --format xml \
  --output english-designer-sitemap.xml
```

**Result**: Valid sitemap XML with filtered URLs

---

### Check Filter Statistics

```bash
uv run python src/sitemap_filter.py alteryx-help-current-sitemap.xml \
  --language en \
  --product designer \
  --dry-run
```

**Result** (stderr):
```
Total URLs: 35460
Filtered URLs: 5234
Language: en
Products: designer
```

---

## Command-Line Reference

### Basic Syntax

```bash
uv run python src/sitemap_filter.py <sitemap-file> [OPTIONS]
```

### Key Options

| Option | Description | Example |
|--------|-------------|---------|
| `--language LANG` or `-l` | Filter by language | `-l en` |
| `--product PROD` or `-p` | Filter by product | `-p designer` |
| `--format FMT` or `-f` | Output format (json/txt/xml) | `-f txt` |
| `--output FILE` or `-o` | Write to file | `-o results.json` |
| `--dry-run` | Show stats only | `--dry-run` |
| `--help` or `-h` | Show help | `--help` |
| `--version` or `-v` | Show version | `--version` |

### Multiple Filters

Use multiple `--product` flags for OR logic:

```bash
uv run python src/sitemap_filter.py alteryx-help-current-sitemap.xml \
  -p designer \
  -p server \
  -p connect
```

Combine language and product for AND logic:

```bash
uv run python src/sitemap_filter.py alteryx-help-current-sitemap.xml \
  --language en \
  --product designer
```

---

## Output Formats

### JSON (default)

```bash
uv run python src/sitemap_filter.py sitemap.xml -l en
```

Produces structured JSON with metadata:
```json
{
  "total_urls": 35460,
  "filtered_urls": 17823,
  "results": [{"url": "...", "lastmod": "..."}]
}
```

### Plain Text

```bash
uv run python src/sitemap_filter.py sitemap.xml -l en -f txt
```

Produces one URL per line (great for piping):
```
https://help.alteryx.com/current/designer.html
https://help.alteryx.com/current/designer/tools.html
```

### XML Sitemap

```bash
uv run python src/sitemap_filter.py sitemap.xml -l en -f xml
```

Produces valid sitemap XML:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://help.alteryx.com/current/designer.html</loc>
    <lastmod>2025-10-23</lastmod>
  </url>
</urlset>
```

---

## Integration Examples

### Count Filtered URLs

```bash
uv run python src/sitemap_filter.py sitemap.xml -l en -f txt | wc -l
```

### Extract URLs to Array in Shell

```bash
urls=$(uv run python src/sitemap_filter.py sitemap.xml -l en -f txt)
```

### Process with jq

```bash
uv run python src/sitemap_filter.py sitemap.xml -l en | \
  jq '.results[] | select(.lastmod > "2025-10-01") | .url'
```

### Feed to Scraper

```bash
uv run python src/sitemap_filter.py sitemap.xml -l en -p designer -f txt | \
  xargs -I {} python src/scraper.py {}
```

---

## Troubleshooting

### File Not Found

**Error**: `Error: Sitemap file not found: sitemap.xml`

**Solution**: Check file path is correct. Use absolute path if needed:
```bash
uv run python src/sitemap_filter.py /workspaces/uv-ayx-rag/alteryx-help-current-sitemap.xml -l en
```

### Invalid Language Code

**Error**: `argument --language/-l: invalid choice: 'fr'`

**Solution**: Use valid language codes: `en` or `de`
```bash
uv run python src/sitemap_filter.py sitemap.xml -l en
```

### Malformed XML

**Error**: `Error: Failed to parse XML: mismatched tag`

**Solution**: Verify XML file is valid. Check with:
```bash
xmllint --noout sitemap.xml
```

### No Matches Found

**Warning**: `Warning: No URLs matched filter criteria`

**Solution**: Check filter criteria. Verify products exist in sitemap:
```bash
# Check what's available first with dry-run on no filters
uv run python src/sitemap_filter.py sitemap.xml --dry-run
```

---

## Performance Notes

- **Small datasets** (<100 URLs): Instant
- **Medium datasets** (1k-10k URLs): <1 second
- **Large datasets** (35k+ URLs): ~1-2 seconds
- **Very large** (100k+ URLs): ~3-5 seconds

Memory usage scales linearly: ~200 bytes per URL

---

## Next Steps

### Development Workflow

1. **Write tests first** (TDD required by constitution):
   ```bash
   # Create test file
   touch tests/unit/test_language_filter.py
   
   # Write failing test
   # Implement feature
   # Verify test passes
   ```

2. **Run tests**:
   ```bash
   uv run pytest tests/
   ```

3. **Check coverage**:
   ```bash
   uv run pytest --cov=src --cov-report=term-missing
   ```

### Extend Functionality

- Add new output formats in `src/filters/output.py`
- Add new filter types in `src/filters/`
- Add new language codes in CLI choices

### Integration

Use this tool as the first stage in your RAG pipeline:

```bash
# Step 1: Filter to English Designer docs
uv run python src/sitemap_filter.py sitemap.xml \
  -l en -p designer -f txt -o urls.txt

# Step 2: Scrape filtered URLs
cat urls.txt | xargs -P 10 -I {} python src/scraper.py {}

# Step 3: Process documents
python src/processor.py scraped_docs/

# Step 4: Generate embeddings
python src/embeddings.py processed_docs/
```

---

## Help & Support

### Get Help

```bash
uv run python src/sitemap_filter.py --help
```

### Check Version

```bash
uv run python src/sitemap_filter.py --version
```

### Debug Mode

Set verbose logging (if implemented):
```bash
export LOG_LEVEL=DEBUG
uv run python src/sitemap_filter.py sitemap.xml -l en
```

---

## Testing Your Installation

Run the integration test suite:

```bash
uv run pytest tests/integration/test_cli.py -v
```

Expected output:
```
tests/integration/test_cli.py::test_help_flag PASSED
tests/integration/test_cli.py::test_version_flag PASSED
tests/integration/test_cli.py::test_language_filter PASSED
tests/integration/test_cli.py::test_product_filter PASSED
tests/integration/test_cli.py::test_combined_filters PASSED
tests/integration/test_cli.py::test_output_formats PASSED
==================== 6 passed in 2.34s ====================
```

---

## Quick Reference Card

```bash
# English URLs only
uv run python src/sitemap_filter.py sitemap.xml -l en

# Designer docs only
uv run python src/sitemap_filter.py sitemap.xml -p designer

# English Designer docs, plain text
uv run python src/sitemap_filter.py sitemap.xml -l en -p designer -f txt

# Multiple products
uv run python src/sitemap_filter.py sitemap.xml -p designer -p server

# Save to file
uv run python src/sitemap_filter.py sitemap.xml -l en -o output.json

# Show statistics only
uv run python src/sitemap_filter.py sitemap.xml -l en --dry-run

# XML output
uv run python src/sitemap_filter.py sitemap.xml -l en -f xml

# Pipe to other tools
uv run python src/sitemap_filter.py sitemap.xml -l en -f txt | head -10
```
