# Implementation Plan: Sitemap Download

**Branch**: `002-sitemap-download` | **Date**: 2025-11-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-sitemap-download/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Download the Alteryx help sitemap from https://help.alteryx.com/current/sitemap.xml with progress indication, validation, and incremental update support. The feature will be implemented as a uv workspace package with CLI interface integrated into main.py, using HTTP client library for downloading with timeout/retry handling, XML validation before saving, and modification date checking to avoid unnecessary downloads.

## Technical Context

**Language/Version**: Python 3.10+  
**Primary Dependencies**: 
- **httpx** (>=0.25.0): Modern HTTP client with streaming support, async-capable, excellent timeout handling
- typer: CLI framework (already in project)
- loguru: Structured logging (already in project)
- xml.etree.ElementTree: XML parsing (standard library)
- xml.sax: Streaming XML validation (standard library)

**Storage**: Local filesystem (default: `alteryx-help-current-sitemap.xml` at project root)  
**Testing**: pytest with pytest-cov (already configured in project)  
**Target Platform**: Linux (Debian dev container), cross-platform compatible  
**Project Type**: Single project (uv workspace package under `packages/sitemap-download/`)  
**Performance Goals**: 
- Download complete sitemap (<100MB, 35k+ URLs) in under 60 seconds on standard broadband
- Validation overhead <5 seconds for 50MB files
- Progress updates every 256KB or 500ms (whichever comes first) for responsive UX

**Constraints**: 
- Connection timeout: 30 seconds (configurable)
- Read timeout: 300 seconds for large files (configurable)
- Must preserve existing file on download/validation failure
- Must validate XML structure before committing to disk
- Memory usage target: <10MB (streaming download with 8KB chunks + SAX validation)

**Scale/Scope**: 
- Single sitemap file per execution
- Expected file size: <100MB
- Expected URL count: 35,000-40,000 entries
- Retry strategy: 3 retries with exponential backoff (1s, 2s, 4s) and ±25% jitter
- Retries only on transient errors (5xx, timeouts, connection errors)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle Compliance Review

**I. Modular Architecture**: ✅ PASS
- Feature implemented as workspace package: `packages/sitemap-download/`
- Clear separation: download logic, validation, CLI interface
- Isolated dependencies in package pyproject.toml
- Exposes typed interface for integration

**II. Data Pipeline Integrity**: ✅ PASS
- Preserves source URL metadata in download logs
- Respects `lastmod` timestamps for incremental updates (FR-006)
- Validates downloaded data before committing to disk (FR-013)

**III. Test-Driven Development**: ✅ PASS
- Tests written before implementation
- Unit tests: download, validation, modification date checking
- Integration tests: full download workflow, error scenarios
- Contract tests: CLI interface

**IV. Incremental Processing**: ✅ PASS
- Checks remote modification date before downloading (FR-006)
- Skips download if remote unchanged (saves bandwidth)
- Force flag bypasses check when needed (FR-007)
- Preserves existing file on failure (FR-014)

**V. Observability & Monitoring**: ✅ PASS
- Structured logging with loguru (timestamps, operation outcomes)
- Progress metrics: bytes downloaded, percentage complete (FR-004)
- Error context: URL, stage, error type, file state (FR-008)
- Success metrics: file size, URL count, operation duration (FR-016)

**VI. Package Management**: ✅ PASS
- Dependencies managed exclusively with uv
- Package-specific dependencies in packages/sitemap-download/pyproject.toml
- No direct pip usage

**VII. Git Commit Standards**: ✅ PASS
- Conventional commits format required
- Scope: `sitemap-download`
- Example: `feat(sitemap-download): implement HTTP download with progress`

**VIII. Release Documentation**: ✅ PASS
- README.md update with feature capabilities and usage
- CHANGELOG.md entry for version
- Release notes from conventional commits
- Final docs commit before merge

**IX. Main Entry Point**: ✅ PASS
- CLI registered with main.py dispatcher
- Command: `python main.py sitemap-download [options]`
- Feature exports typer app in __init__.py

### Gate Status: ✅ APPROVED

No constitution violations. All principles satisfied by design. No complexity justification needed.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
# Single project with uv workspace package
packages/
└── sitemap-download/
    ├── pyproject.toml           # Package dependencies (httpx/requests, etc.)
    ├── README.md                # Package-specific documentation
    ├── src/
    │   └── sitemap_download/
    │       ├── __init__.py      # Exports CLI app
    │       ├── cli.py           # CLI implementation
    │       ├── downloader.py    # HTTP download logic
    │       ├── validator.py     # XML validation
    │       └── models.py        # Data models (DownloadResult, etc.)
    └── tests/
        ├── unit/
        │   ├── test_downloader.py
        │   ├── test_validator.py
        │   └── test_models.py
        ├── integration/
        │   └── test_cli.py
        └── fixtures/
            ├── valid_sitemap.xml
            └── invalid_sitemap.xml

# Project root integration
main.py                          # Registers sitemap-download command
```

**Structure Decision**: Single project structure using uv workspace packages. The sitemap-download feature is self-contained under `packages/sitemap-download/` with clear module separation (downloader, validator, models, CLI). This follows the pattern established by sitemap-filter and enables independent testing and dependency management.

## Complexity Tracking

> No constitution violations identified. This section is not applicable for this feature.
