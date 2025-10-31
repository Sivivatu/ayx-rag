# CLI Interface Contract: Sitemap Filter

**Feature**: 001-sitemap-filter  
**Date**: 2025-10-30  
**Version**: 1.1.0

## Command Signature

```bash
uv run python src/sitemap_filter.py <sitemap_file> [OPTIONS]
```

**CLI Framework**: typer (type-hint based, auto-documented)

---

## Arguments

### Positional Arguments

#### `sitemap_file`
- **Type**: File path (string)
- **Required**: Yes
- **Description**: Path to XML sitemap file to filter
- **Validation**: Must be readable file, valid XML format
- **Example**: `alteryx-help-current-sitemap.xml`

---

## Options

### `--language LANG` / `-l LANG`
- **Type**: String (choice)
- **Required**: No
- **Multiple**: Yes (can specify multiple times)
- **Choices**: `en`, `de`, `es`, `fr`, `it`, `ja`, `pt`, `zh-CHS`, `all`
- **Description**: Filter URLs by language locale. Use 'all' to include all languages.
- **Default**: `en` (English only)
- **Examples**:
  ```bash
  # No flag specified - defaults to English
  sitemap_filter.py sitemap.xml
  
  --language en            # English only (explicit)
  -l de                    # German only
  --language en -l de      # Both English and German
  --language all           # All languages
  -l all                   # All languages (short form)
  ```

### `--product PRODUCT` / `-p PRODUCT`
- **Type**: String
- **Required**: No
- **Multiple**: Yes (can specify multiple times)
- **Description**: Filter URLs by product path segment (OR logic)
- **Default**: None (all products included)
- **Examples**:
  ```bash
  --product designer       # Designer docs only
  -p server                # Server docs only
  -p designer -p server    # Designer OR Server
  ```

### `--format FORMAT` / `-f FORMAT`
- **Type**: String (choice)
- **Required**: No
- **Choices**: `json`, `txt`, `xml`
- **Description**: Output format
- **Default**: `json`
- **Examples**:
  ```bash
  --format json            # JSON array (default)
  -f txt                   # Plain text URLs
  --format xml             # Sitemap XML
  ```

### `--output FILE` / `-o FILE`
- **Type**: File path (string)
- **Required**: No
- **Description**: Write output to file instead of stdout
- **Default**: stdout
- **Examples**:
  ```bash
  --output filtered.json   # Write to file
  -o results.txt           # Write to file (short form)
  ```

### `--dry-run`
- **Type**: Boolean flag
- **Required**: No
- **Description**: Show statistics without outputting URLs
- **Default**: False
- **Example**:
  ```bash
  --dry-run                # Show counts only
  ```

### `--help` / `-h`
- **Type**: Boolean flag
- **Description**: Display help message and exit
- **Example**:
  ```bash
  --help                   # Show usage information
  ```

### `--version` / `-v`
- **Type**: Boolean flag
- **Description**: Display version information and exit
- **Example**:
  ```bash
  --version                # Show script version
  ```

---

## Output Formats

### JSON Format (default)

```json
{
  "total_urls": 35460,
  "filtered_urls": 17823,
  "results": [
    {
      "url": "https://help.alteryx.com/current/designer.html",
      "lastmod": "2025-10-23"
    },
    {
      "url": "https://help.alteryx.com/current/designer/tools.html",
      "lastmod": "2025-10-22"
    }
  ]
}
```

**Schema**:
- `total_urls` (integer): Total URLs in sitemap
- `filtered_urls` (integer): Number of URLs after filtering
- `results` (array): Filtered URL entries
  - `url` (string): The URL location
  - `lastmod` (string): Last modified date (ISO format YYYY-MM-DD)

### Text Format

```
https://help.alteryx.com/current/designer.html
https://help.alteryx.com/current/designer/tools.html
https://help.alteryx.com/current/designer/workflows.html
```

**Format**: One URL per line, no metadata

### XML Format

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://help.alteryx.com/current/designer.html</loc>
    <lastmod>2025-10-23</lastmod>
  </url>
  <url>
    <loc>https://help.alteryx.com/current/designer/tools.html</loc>
    <lastmod>2025-10-22</lastmod>
  </url>
</urlset>
```

**Format**: Valid sitemap XML with filtered URLs

---

## Exit Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 0    | Success | Command executed successfully |
| 1    | Error   | General error (file not found, invalid XML, etc.) |
| 2    | Usage   | Invalid command-line arguments |

---

## Standard Error Output

All error messages and statistics are written to **stderr**, keeping stdout clean for piping.

### Error Messages

```bash
# File not found
Error: Sitemap file not found: nonexistent.xml

# Invalid XML
Error: Failed to parse XML: mismatched tag at line 42

# Invalid language
Error: Invalid language 'fr'. Valid options: en, de

# No matches
Warning: No URLs matched filter criteria
Total URLs: 35460
Filtered URLs: 0
```

### Statistics Output (stderr)

```bash
Total URLs: 35460
Filtered URLs: 17823
Language: en
Products: designer, server
```

---

## Usage Examples

### Example 1: Default English Filter

```bash
# No language flag - defaults to English
uv run python src/sitemap_filter.py alteryx-help-current-sitemap.xml
```

**Output** (stdout):
```json
{
  "total_urls": 8864,
  "filtered_urls": 1108,
  "results": [...]
}
```

### Example 2: All Languages

```bash
uv run python src/sitemap_filter.py alteryx-help-current-sitemap.xml --language all
```

**Output** (stdout):
```json
{
  "total_urls": 8864,
  "filtered_urls": 8864,
  "results": [...]
}
```

### Example 3: Filter Designer Docs in Text Format

```bash
uv run python src/sitemap_filter.py alteryx-help-current-sitemap.xml \
  --product designer \
  --format txt
```

**Output** (stdout):
```
https://help.alteryx.com/current/de/designer.html
https://help.alteryx.com/current/designer.html
...
```

### Example 3: English Designer Docs to File

```bash
uv run python src/sitemap_filter.py alteryx-help-current-sitemap.xml \
  --language en \
  --product designer \
  --output english-designer.json
```

**Output**: Results written to `english-designer.json`  
**stderr**: Statistics displayed

### Example 4: Dry Run Statistics

```bash
uv run python src/sitemap_filter.py alteryx-help-current-sitemap.xml \
  --language en \
  --product designer \
  --dry-run
```

**Output** (stderr only):
```
Total URLs: 35460
Filtered URLs: 5234
Language: en
Products: designer
```

### Example 5: Multiple Products

```bash
uv run python src/sitemap_filter.py alteryx-help-current-sitemap.xml \
  --language en \
  -p designer \
  -p server \
  -p connect \
  --format xml \
  -o filtered-sitemap.xml
```

**Output**: XML sitemap with English URLs for Designer, Server, or Connect

### Example 6: Piping to Other Tools

```bash
# Get English Designer URLs and count them
uv run python src/sitemap_filter.py alteryx-help-current-sitemap.xml \
  -l en -p designer -f txt | wc -l

# Download all filtered URLs
uv run python src/sitemap_filter.py alteryx-help-current-sitemap.xml \
  -l en -f txt | xargs -I {} curl -O {}
```

---

## Error Scenarios

### Scenario 1: File Not Found

**Command**:
```bash
uv run python src/sitemap_filter.py missing.xml
```

**Exit Code**: 1  
**stderr**:
```
Error: Sitemap file not found: missing.xml
```

### Scenario 2: Malformed XML

**Command**:
```bash
uv run python src/sitemap_filter.py broken.xml
```

**Exit Code**: 1  
**stderr**:
```
Error: Failed to parse XML: mismatched tag at line 42
```

### Scenario 3: Invalid Argument

**Command**:
```bash
uv run python src/sitemap_filter.py sitemap.xml --language fr
```

**Exit Code**: 2  
**stderr**:
```
Usage: sitemap_filter.py [OPTIONS] SITEMAP_FILE

Try 'sitemap_filter.py --help' for help.

Error: Invalid value for '--language': 'fr' is not one of 'en', 'de'.
```

### Scenario 4: No Matches

**Command**:
```bash
uv run python src/sitemap_filter.py sitemap.xml --language en --product nonexistent
```

**Exit Code**: 0 (success, but no results)  
**stdout**:
```json
{
  "total_urls": 35460,
  "filtered_urls": 0,
  "results": []
}
```
**stderr**:
```
Warning: No URLs matched filter criteria
```

---

## Contract Testing

### Test Cases

1. **TC-001**: Verify `--help` displays usage information
2. **TC-002**: Verify `--version` displays version string
3. **TC-003**: Verify missing positional argument shows error
4. **TC-004**: Verify invalid file path returns exit code 1
5. **TC-005**: Verify malformed XML returns exit code 1
6. **TC-006**: Verify `--language en` filters correctly
7. **TC-007**: Verify `--language de` filters correctly
8. **TC-008**: Verify `--product designer` filters correctly
9. **TC-009**: Verify multiple `--product` flags work (OR logic)
10. **TC-010**: Verify combined language and product filters (AND logic)
11. **TC-011**: Verify `--format json` produces valid JSON
12. **TC-012**: Verify `--format txt` produces one URL per line
13. **TC-013**: Verify `--format xml` produces valid sitemap XML
14. **TC-014**: Verify `--output file.json` writes to file
15. **TC-015**: Verify `--dry-run` shows statistics without URLs
16. **TC-016**: Verify statistics written to stderr, not stdout
17. **TC-017**: Verify no matches scenario handles gracefully
18. **TC-018**: Verify exit code 0 on success, 1 on error

---

## Version History

- **1.2.0** (2025-10-31): Added 'all' language option and English default for --language
- **1.1.0** (2025-10-31): Updated to use typer CLI framework with type hints
- **1.0.0** (2025-10-30): Initial contract specification
