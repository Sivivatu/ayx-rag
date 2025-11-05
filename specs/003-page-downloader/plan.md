# Implementation Plan: Page Downloader

**Branch**: `003-page-downloader` | **Date**: 2025-11-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-page-downloader/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

The page-downloader feature downloads raw HTML pages from Alteryx documentation URLs (filtered by sitemap-filter) and saves them to disk with human-readable directory structures. It implements sequential processing with rate limiting, retry logic with exponential backoff, robots.txt enforcement, SSL/TLS validation, and incremental update support based on Last-Modified headers. The feature integrates into the RAG pipeline as the content collection stage between sitemap filtering and HTML processing.

## Technical Context

**Language/Version**: Python >=3.10 (aligned with project requirements)  
**Primary Dependencies**: httpx>=0.25.0 (HTTP client with streaming), typer>=0.20.0 (CLI framework), loguru>=0.7.3 (logging), robotexclusionrulesparser or urllib.robotparser (robots.txt)  
**Storage**: Local filesystem (nested directories matching URL path structure)  
**Testing**: pytest>=8.4.2 with pytest-cov>=7.0.0, httpx mocking (respx or pytest-httpx)  
**Target Platform**: Linux dev container (Debian-based), cross-platform Python  
**Project Type**: Single workspace package (uv workspace member under packages/)  
**Performance Goals**: Download 100 pages in <2 minutes with 0.5s rate limiting (SC-002), single page <5 seconds (SC-001), rate limiting variance <10% (SC-008)  
**Constraints**: Sequential processing only (no concurrency), 5MB default file size limit (configurable), strict SSL/TLS validation, HTTP timeouts (30s connect, 300s read)  
**Scale/Scope**: Expected to handle 8,864 filtered URLs from sitemap, support for incremental updates (80% time reduction for unchanged content per SC-004)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| **I. Modular Architecture** | ✅ PASS | Feature organized as uv workspace package under `packages/page-downloader/` with isolated dependencies, clear interfaces, independent tests |
| **II. Data Pipeline Integrity** | ✅ PASS | Downloads preserve source URL attribution, Last-Modified timestamps tracked for incremental updates, progress/error metadata logged |
| **III. Test-Driven Development** | ✅ PASS | TDD workflow required: unit tests for HTTP client, retry logic, path sanitization; integration tests for CLI; contract tests for main.py integration |
| **IV. Incremental Processing** | ✅ PASS | Incremental mode skips unchanged pages (FR-014), batch downloads continue after failures (FR-019), progress tracked per URL |
| **V. Observability & Monitoring** | ✅ PASS | Structured logging with loguru (FR-017), progress metrics displayed (FR-016), summary statistics reported (FR-018), errors include URL/stage/context |
| **VI. Package Management** | ✅ PASS | Dependencies managed via uv exclusively, `pyproject.toml` with uv_build>=0.9.6 backend, versions constrained |
| **VII. Git Commit Standards** | ✅ PASS | Conventional commits required throughout development: `feat(page-downloader):`, `test(page-downloader):`, etc. |
| **VIII. Release Documentation** | ✅ PASS | Feature completion includes README.md updates, CHANGELOG.md entry, release notes generation, final docs commit |
| **IX. Main Entry Point** | ✅ PASS | CLI registered with main.py dispatcher via `app.add_typer()`, command: `python main.py page-downloader` |

**Gate Status**: ✅ ALL GATES PASSED - Ready for Phase 0 research

## Project Structure

### Documentation (this feature)

```text
specs/003-page-downloader/
├── spec.md              # Feature specification with clarifications
├── plan.md              # This file (implementation plan)
├── research.md          # Phase 0: Technology decisions and patterns
├── data-model.md        # Phase 1: Entity definitions and relationships
├── quickstart.md        # Phase 1: Developer getting started guide
├── contracts/           # Phase 1: CLI interface contracts
│   └── cli-interface.md
├── checklists/          # Specification validation
│   └── requirements.md
└── tasks.md             # Phase 2: Task breakdown (created by /speckit.tasks)
```

### Source Code (repository root)

```text
packages/page-downloader/
├── pyproject.toml       # Package metadata, dependencies (httpx, robotexclusionrulesparser)
├── README.md            # Package documentation
├── src/
│   └── page_downloader/
│       ├── __init__.py          # Exports app for main.py integration
│       ├── cli.py               # Typer CLI implementation
│       ├── downloader.py        # HTTP download engine with retry logic
│       ├── models.py            # Data models (DownloadConfig, PageDownload, DownloadSession, DownloadResult)
│       ├── validator.py         # HTML validation, robots.txt checking
│       ├── path_utils.py        # URL-to-filesystem path sanitization
│       ├── progress.py          # Progress tracking and display
│       └── exceptions.py        # Custom exceptions (DownloadError, ValidationError, RobotsDeniedError)
└── tests/
    ├── fixtures/
    │   ├── sample_pages/        # Sample HTML files for testing
    │   ├── robots.txt           # Test robots.txt files
    │   └── url_lists/           # Sample URL list inputs
    ├── unit/
    │   ├── test_downloader.py   # HTTP client, retry logic, timeout handling
    │   ├── test_models.py       # Data model validation
    │   ├── test_validator.py    # HTML validation, robots.txt parsing
    │   ├── test_path_utils.py   # Path sanitization edge cases
    │   └── test_progress.py     # Progress tracking logic
    └── integration/
        ├── test_cli.py          # End-to-end CLI tests with mocked HTTP
        └── test_incremental.py  # Incremental download scenarios

main.py                          # Updated to register page-downloader command
```

**Structure Decision**: Workspace package structure following established pattern from sitemap-filter and sitemap-download. Single package with clear module separation: CLI layer (cli.py), business logic (downloader.py, validator.py), utilities (path_utils.py, progress.py), and models (models.py, exceptions.py). Tests organized by type (unit vs integration) with comprehensive fixtures.

## Complexity Tracking

**No violations** - All constitution principles satisfied without exceptions.
