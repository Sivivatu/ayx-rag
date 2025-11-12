# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.1] - 2025-11-12

### Performance
- **Fixed Critical Startup Performance Issue** (html-to-markdown)
  - Reduced CLI startup time from 3+ minutes to ~6 seconds (95-97% improvement)
  - Implemented lazy loading for heavy dependencies (DoclingStrategy, MarkdownifyStrategy)
  - Added deferred imports in all CLI commands (convert, batch, evaluate, benchmark)
  - Implemented `__getattr__` in package `__init__.py` for lazy app export
  - Changed evaluate command threshold parameters to optional with lazy loading
  - Heavy ML/document libraries now only load when commands are executed
  - Simple commands like `--help` now respond in ~6s instead of 3+ minutes

## [0.4.0] - 2025-11-12

### Added
- **HTML to Markdown Conversion CLI** - Complete conversion pipeline with 132 tests
  - **Single-File Conversion** (US1):
    - Structure preservation (headings, lists, links, images with alt text, code blocks, tables)
    - YAML front matter generation (source URL, title, last modified timestamp)
    - Code language detection from CSS classes (`language-*`, `lang-*`, etc.)
    - Hybrid table handling (Markdown pipes for simple, HTML for complex spans)
    - Multiple strategy support (Markdownify default, Docling, Pandoc)
    - Performance: <2s per standard page, <1s average
  - **Batch Conversion** (US2):
    - Recursive directory processing with structure preservation
    - Progress tracking every 10 files with rate calculation
    - Error handling continuing after failures with complete error tracking
    - Summary JSON output with timing, rates, and error details
    - Checkpoint/resume capability with automatic saves every 10 files
    - Custom checkpoint paths via `--checkpoint` flag
    - Exclusion patterns for skipping unwanted files/directories
    - External JSON configuration support
    - Performance: ≥25 files/min throughput validated
  - **Quality Evaluation** (US3):
    - Comprehensive metrics: heading fidelity, link preservation, table preservation, code block integrity, image alt coverage
    - Weighted scoring with configurable weights and automatic normalization
    - Multiple report formats: JSON (detailed), CSV (tabular), Markdown (human-readable)
    - Customizable per-metric thresholds with failure flagging
    - Aggregate statistics and per-file breakdowns
    - Manual review percentage calculation (<5% target)
    - Timestamped output option for persistent history tracking

### Changed
- Main CLI now includes `html-to-markdown` nested app with 5 subcommands (convert, batch, evaluate, benchmark, strategies)

### Performance
- Single-file conversion: <2s per standard page (<200KB), <1s average
- Batch throughput: ≥25 files/min validated with 30-file realistic test
- Memory efficient: streaming parse for large HTML files
- Progress updates: every 10 files with rate calculation
- Checkpoint frequency: every 10 files during batch processing

### Testing
- 132 comprehensive tests (94 unit + 38 integration)
- Unit tests: checkpoint, config, converter, I/O utilities, metrics, models, table handler
- Integration tests: CLI workflows, performance validation, strategy benchmarking
- Performance tests: single-file <2s requirement, batch ≥25 files/min throughput

### Documentation
- Complete package README with feature overview, usage examples, configuration guide
- Updated root README with html-to-markdown feature summary
- Comprehensive inline documentation and docstrings
- Design decisions documented (nested CLI, strategy pattern, hybrid tables, checkpoint resume, weighted scoring)

### Research
- Benchmarked 3 conversion strategies (Markdownify, Docling, Pandoc)
- Selected Markdownify as default (100% fidelity, 28ms avg, lightweight)
- Retained all strategies for future document type expansion
- Documented comparison matrix in `specs/004-html-to-markdown/research.md`

## [0.3.0] - 2025-11-07

### Added
- **Page Downloader CLI** (single + batch HTML download)
  - Single URL and file-based batch mode
  - URL→path mapping preserving hierarchy
  - HTML content validation and skip logic
  - Batch progress tracking with rich-based tracker (quiet/verbose modes)
  - Rate limiting via `--delay`
  - Dry run support (`--dry-run`)
  - Configurable max file size, timeouts, retries
  - Structured logging (FR-017) with byte count
  - Summary statistics (total/success/failed/skipped/invalid/duration)
  - Standard exit codes (0 success, 1 failure, 2 validation/skip, 3 config)

### Changed
- Main CLI now forwards positional `url_or_file` and exposes `--quiet`, `--delay` options.

### Fixed
- Preserved test-added log handlers (avoid removing custom sinks)
- Corrected progress session statistics and batch fixture mismatch
- Adjusted mixed batch expected HTML count (5 valid pages)

### Tests
- Restored and renamed integration tests to avoid namespace collisions
- Added logging integration tests verifying format and required fields
- Added batch mode tests (success, comments/blanks parity, mixed errors summary)

### Documentation
- Updated root README with page-downloader feature and examples
- Added package README for page-downloader
- Updated tasks.md marking US2 (batch mode) complete

### Performance
- Batch processing sequential with optional delay; progress tracker lightweight

### Coverage
- Page-downloader unit + integration tests passing (19 integration; unit suite green)

### Notes
- Incremental updates (US3) and retry/backoff enhancements (US4) scheduled for future versions.

## [0.2.0] - 2025-11-05

### Added
- **Sitemap Download CLI** - Download and validate XML sitemaps with production-ready reliability
  - HTTP/HTTPS download with streaming (8KB chunks, memory efficient)
  - Real-time progress tracking (speed, ETA, downloaded/total bytes)
  - XML validation with SAX streaming (validates structure, counts URLs)
  - Smart incremental updates (compares Last-Modified dates, skips unchanged downloads)
  - Retry logic with exponential backoff (1s, 2s, 4s delays)
  - Jitter randomization (25% variance) to prevent thundering herd
  - Error classification: 5xx/timeouts retryable, 4xx fail immediately
  - Archive support (preserve existing files with timestamp suffixes)
  - Configurable timeouts (connection and read)
  - Configurable retry attempts (default: 3)
  - Quiet mode for scripting
  - Exit codes (0=success, 1=download fail, 2=validation fail, 3=config error)
  - Atomic file writes (temp file + rename for crash safety)
- Test infrastructure with 95%+ coverage
  - 56 tests (48 unit, 8 integration)
  - Test fixtures for XML validation scenarios
  - Mock-based retry testing with time.sleep patching
- Comprehensive documentation
  - Package README with full API guide, usage examples, troubleshooting
  - Root README updated with feature summary
  - Docstrings for all public classes and methods

### Performance
- Streaming download: constant memory usage regardless of file size
- Streaming validation: SAX parser (memory efficient for large XML)
- 8,872 URLs downloaded in ~3 seconds (1.4 MB)
- Progress updates every 256KB or 500ms

### Fixed
- Validation failures now return proper exit code 2 (was 0)

## [0.1.0] - 2025-11-03

### Added
- **Sitemap Filter CLI** - Filter Alteryx help documentation sitemap URLs by language and product
  - Language filtering for 8 languages (en, de, es, fr, it, ja, pt, zh-CHS)
  - Product filtering for 12+ Alteryx products (designer, server, connect, etc.)
  - Combined filters with AND/OR logic (language AND product, multiple values OR within type)
  - Multiple output formats: JSON (with metadata), plain text, XML sitemap
  - File output support with `--output` flag
  - Dry-run mode for previewing statistics without generating output
  - Performance logging for parsing, filtering, and output phases
  - File size validation with warnings for large sitemaps (>10MB)
  - Comprehensive error handling with clear messages
- Test infrastructure with 96% coverage
  - 77 tests (56 unit, 16 integration, 5 performance)
  - Test fixtures for various scenarios
  - Performance validation (<3s for large sitemaps)
- CLI accessible via workspace main entry point
- Comprehensive documentation in feature README

### Performance
- Processes 8,864 URLs in ~0.1 seconds
- Filters 1,200 URLs in 0.014 seconds
- Memory efficient (<50MB for typical workloads)

### Documentation
- Feature README with complete usage guide
- Architecture documentation
- API examples for all use cases
- Updated root README with feature summary

## Version History

- **0.3.0** (2025-11-07): Page Downloader (single + batch) feature
- **0.2.0** (2025-11-05): Sitemap Download feature
- **0.1.0** (2025-11-03): Sitemap Filter feature
- **Unreleased**: Active development

---

## Previous Template Entries

### [Initial Setup] - 2025-10-31

#### Added
- Project initialization
- Dev container with Debian-based environment
- Oh My Zsh with spaceship prompt
- VS Code configuration and extensions
- Git repository setup
- Project README with comprehensive documentation
- Constitution defining development principles
- Speckit templates for feature workflow

### Documentation
- README.md with project overview and quick start
- Constitution.md with 7 core principles
- Copilot instructions for AI agent guidance
- Release notes template for future releases

---

## Template for Future Entries

## [X.Y.Z] - YYYY-MM-DD

### Added
- New features and capabilities

### Changed
- Changes to existing functionality

### Deprecated
- Features scheduled for removal

### Removed
- Features removed in this version

### Fixed
- Bug fixes

### Security
- Security improvements and vulnerability fixes

---

## Version History

- **0.1.0** (2025-10-31): Initial project setup
- **Unreleased**: Active development

---

## How to Update This File

1. **During Development**: Add entries to `[Unreleased]` section as features are completed
2. **Before Release**: Move `[Unreleased]` items to new version section
3. **Version Numbering**:
   - **MAJOR** (X.0.0): Breaking changes
   - **MINOR** (0.X.0): New features, backward compatible
   - **PATCH** (0.0.X): Bug fixes, backward compatible
4. **Always Include**: Date in YYYY-MM-DD format
5. **Categories**: Use standard categories (Added, Changed, Fixed, etc.)
6. **Commits Reference**: Link to conventional commits where applicable

## Links

- [Keep a Changelog](https://keepachangelog.com/)
- [Semantic Versioning](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
