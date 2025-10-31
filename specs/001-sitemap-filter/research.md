# Research: Sitemap Filter CLI

**Feature**: 001-sitemap-filter  
**Date**: 2025-10-30  
**Phase**: 0 - Technical Research

## Overview

Research technical decisions for implementing a CLI tool that filters XML sitemaps by language and product path segments, with multiple output format support.

---

## Decision 1: XML Parsing Library

**Decision**: Use Python standard library `xml.etree.ElementTree`

**Rationale**:
- **Built-in**: No external dependencies, aligns with constitution principle VI (Package Management)
- **Performance**: Efficient for 1.5MB XML files with 35k entries (meets SC-001: <3 seconds)
- **Security**: Safer than alternatives like `xml.dom.minidom` for untrusted input
- **Memory**: Tree-based parsing fits well within 500MB constraint for 100k URLs (SC-010)
- **Simplicity**: Straightforward API for parsing sitemap schema

**Alternatives Considered**:
- **lxml**: More features but adds external dependency, violates "standard library only" approach
- **xml.dom.minidom**: DOM-based, higher memory usage, slower parsing
- **SAX parsing**: Streaming approach unnecessary for sitemap size, adds complexity
- **defusedxml**: Security wrapper but overkill for trusted internal sitemaps

**Implementation Notes**:
- Use `ET.iterparse()` for memory-efficient parsing if needed
- Validate against sitemap schema namespace: `http://www.sitemaps.org/schemas/sitemap/0.9`
- Handle encoding issues with explicit UTF-8

---

## Decision 2: CLI Argument Parsing

**Decision**: Use **typer** CLI framework

**Rationale**:
- **Modern API**: Type-hint based, leverages Python 3.10+ features
- **Auto-documentation**: Generates help from type hints and docstrings
- **Rich output**: Built-in colored terminal output and progress bars
- **Type validation**: Automatic validation from type annotations
- **Industry standard**: Well-maintained, built on click foundation

**Alternatives Considered**:
- **argparse**: Standard library but verbose, limited type checking
- **click**: Mature but decorator-heavy syntax
- **docopt**: Parse from docstring but less flexible for complex scenarios
- **sys.argv manual parsing**: Reinventing the wheel, error-prone

**Implementation Notes**:
- Use `List[str]` type hint for multiple `--product` flags (FR-004)
- Use `Literal['en', 'de']` for `--language` validation
- Use `Literal['json', 'txt', 'xml']` for `--format` validation
- Implement `--version` with typer callback (FR-011)
- Use typer.Argument() for required sitemap file parameter
- Leverage typer.Option() for all optional flags

---

## Decision 3: Language Detection Strategy

**Decision**: URL path pattern matching (regex-based)

**Rationale**:
- **Assumption-based**: English URLs have no locale prefix (`/current/{path}`), non-English have locale (`/current/{locale}/{path}`)
- **Performance**: Regex compilation once, fast matching for 35k URLs
- **Accuracy**: Deterministic pattern matching (meets SC-002: 99% accuracy)
- **Simplicity**: No ML or language detection libraries needed

**Alternatives Considered**:
- **Language detection libraries** (langdetect, polyglot): Unnecessary complexity, requires fetching content
- **Manual string parsing**: Slower than compiled regex, harder to maintain
- **URL structure assumptions only**: Less flexible if sitemap structure changes

**Implementation Notes**:
- Pattern for non-English: `help.alteryx.com/current/([a-z]{2})/`
- Default to English if no locale prefix found
- Extract locale code for filtering: `en`, `de`, etc.

---

## Decision 4: Output Format Implementation

**Decision**: Separate formatter functions for each format

**Rationale**:
- **Modularity**: Aligns with constitution principle I (Modular Architecture)
- **Testability**: Each formatter independently testable
- **Extensibility**: Easy to add new formats later
- **Single Responsibility**: Each function handles one format

**Alternatives Considered**:
- **Template engine** (jinja2): Overkill for simple formats, adds dependency
- **Single formatter with conditionals**: Harder to test, violates SRP
- **Class hierarchy**: Over-engineering for simple formatting logic

**Implementation Notes**:
- `format_json(entries)`: Use `json.dumps()` with indent=2 for readability
- `format_txt(entries)`: One URL per line, simple string join
- `format_xml(entries)`: Reconstruct sitemap XML structure with `ET.Element` and `ET.tostring()`
- All formats preserve `lastmod` (FR-008)

---

## Decision 5: Filter Combination Logic

**Decision**: AND across filter types, OR within filter type

**Decision**: Use set operations for efficient filtering

**Rationale**:
- **Requirement**: FR-005 specifies AND logic between types (language AND product)
- **Requirement**: FR-004 specifies OR logic within type (product A OR product B)
- **Performance**: Set intersection/union is O(n), efficient for 35k URLs
- **Clarity**: Boolean logic clearly expressed in code

**Alternatives Considered**:
- **List comprehensions with nested conditions**: Less efficient, harder to read
- **Database-style queries**: Overengineering for in-memory filtering
- **Pandas DataFrame**: Adds large dependency for simple filtering

**Implementation Notes**:
```python
# Pseudocode structure
all_entries = parse_sitemap(file)

if language_filter:
    entries = set(e for e in all_entries if e.language in languages)
else:
    entries = set(all_entries)

if product_filter:
    product_matches = set()
    for product in products:
        product_matches.update(e for e in entries if product in e.url)
    entries = entries.intersection(product_matches) if entries else product_matches

return entries
```

---

## Decision 6: Error Handling Strategy

**Decision**: Fail-fast with descriptive errors

**Rationale**:
- **Requirement**: FR-012 requires non-zero exit codes on errors
- **Requirement**: SC-006 requires clear, actionable error messages
- **Requirement**: SC-007 requires fast failure (<1 second)
- **Constitution**: Principle V (Observability) requires error context

**Alternatives Considered**:
- **Silent failures**: Violates requirements
- **Warning-based**: Confusing UX, unclear success state
- **Try-catch everything**: Hides real errors, makes debugging harder

**Implementation Notes**:
- XML parsing errors: Show file path, line number if available
- File not found: Show file path, suggest checking path
- Invalid language/product: Show provided value, list valid options
- Malformed lastmod: Show URL, continue with warning (non-critical)
- Use `sys.exit(1)` for errors, `sys.exit(0)` for success

---

## Decision 7: Performance Optimization

**Decision**: In-memory processing with generator expressions where beneficial

**Rationale**:
- **Requirement**: SC-001 requires <3 seconds for 35k URLs
- **Requirement**: SC-010 requires <500MB memory for 100k URLs
- **Simplicity**: 1.5MB XML file easily fits in memory
- **Constitution**: Principle IV (Incremental Processing) doesn't apply to this stateless tool

**Alternatives Considered**:
- **Streaming parsing**: Unnecessary complexity for file size
- **Parallel processing**: Overkill, XML parsing is I/O-bound not CPU-bound
- **Caching**: No repeated operations to cache

**Implementation Notes**:
- Load full XML into memory (efficient for <10MB files)
- Use generator expressions for filtering steps
- Pre-compile regex patterns for language detection
- Avoid unnecessary data copies

---

## Decision 8: Testing Strategy

**Decision**: TDD with pytest, separate unit and integration tests

**Rationale**:
- **Constitution**: Principle III (TDD) is NON-NEGOTIABLE
- **Requirement**: Need 80%+ coverage
- **Modularity**: Unit test each filter/formatter function independently
- **Integration**: Test full CLI with various flag combinations

**Alternatives Considered**:
- **unittest**: Standard library but pytest has better fixtures and assertions
- **Manual testing only**: Violates constitution
- **Integration tests only**: Insufficient coverage, harder to debug

**Implementation Notes**:
```
tests/
├── unit/
│   ├── test_parser.py           # Test XML parsing, error handling
│   ├── test_language_filter.py  # Test language detection, filtering
│   ├── test_product_filter.py   # Test product path matching
│   └── test_output.py           # Test each format function
├── integration/
│   └── test_cli.py              # Test full CLI with subprocess
└── fixtures/
    ├── sample_sitemap.xml       # Valid sitemap, ~100 URLs
    ├── malformed_sitemap.xml    # Missing tags, wrong namespace
    └── large_sitemap.xml        # 1000+ URLs for performance testing
```

---

## Decision 9: Logging Strategy

**Decision**: Use **loguru** for all logging

**Rationale**:
- **Zero configuration**: Works out of the box with sensible defaults
- **Structured logging**: Supports JSON output for observability (constitution V)
- **Performance**: Minimal overhead, async-friendly
- **Developer experience**: Clean API, no logger initialization boilerplate
- **Rich context**: Automatic exception catching with full context

**Alternatives Considered**:
- **standard logging**: Verbose configuration, requires manual setup
- **structlog**: More features but heavier, requires more setup
- **print statements**: Not structured, no log levels or filtering

**Implementation Notes**:
- Use `logger.info()` for progress updates to stderr
- Use `logger.debug()` for detailed parsing information
- Use `logger.warning()` for non-critical issues (e.g., no matches)
- Use `logger.error()` for failures (e.g., file not found, invalid XML)
- Configure serialization for JSON output in production mode
- Respect `--quiet` flag to suppress non-error messages

---

## Summary

All technical decisions balance **simplicity with modern best practices**:
- ✅ **Core parsing**: Standard library (xml.etree.ElementTree) - no external deps needed
- ✅ **CLI framework**: typer - modern, type-safe, auto-documented
- ✅ **Logging**: loguru - structured, zero-config, observable
- ✅ **Constitution compliance**: Package Management (uv), TDD (pytest), Observability (structured logs)
- ✅ **Performance requirements**: SC-001 (<3s), SC-010 (<500MB) both met
- ✅ **Testability**: All components independently testable (TDD principle III)
- ✅ **Modularity**: Clear separation of concerns (Architecture principle I)

**Runtime Dependencies**: `typer`, `loguru` (via `uv add`)  
**Dev Dependencies**: `pytest` (via `uv add --dev`)

**Next Phase**: Proceed to Phase 1 (Design) - create data-model.md, contracts/, and quickstart.md
