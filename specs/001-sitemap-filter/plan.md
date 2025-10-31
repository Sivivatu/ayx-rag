# Implementation Plan: Sitemap Filter CLI

**Branch**: `001-sitemap-filter` | **Date**: 2025-10-30 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-sitemap-filter/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a CLI tool to filter the Alteryx sitemap (8,864 URLs) by language and product paths. The tool enables developers to extract focused subsets of documentation URLs for incremental RAG system development. Primary requirements: filter by language (en/de/es/fr/it/ja/pt/zh-CHS/all with en as default), filter by product path segments (designer/server/etc), combine filters, and output in multiple formats (JSON/txt/xml).

## Technical Context

**Language/Version**: Python 3.10+  
**Primary Dependencies**: xml.etree.ElementTree (XML parsing), typer (CLI framework), loguru (logging)  
**Dev Dependencies**: pytest (per constitution requirement III)  
**Storage**: N/A (stateless script, no persistence)  
**Target Platform**: Linux (dev container), cross-platform compatible  
**Project Type**: Single project (CLI utility)  
**Performance Goals**: Filter 35k URLs in <3 seconds, memory usage <500MB for 100k URLs  
**Constraints**: Must parse 1.5MB XML file efficiently, must preserve timestamps with 100% accuracy  
**Scale/Scope**: Single script, ~500-800 lines of code estimated, 4 user stories with 16 functional requirements

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ I. Modular Architecture
**Status**: PASS  
**Rationale**: CLI utility is a single, focused module. Internal functions (parse XML, detect language, filter URLs, format output) will have clear separation. No cross-module dependencies.

### ✅ II. Data Pipeline Integrity
**Status**: PASS  
**Rationale**: FR-008 requires preserving `lastmod` timestamps. FR-015 requires displaying counts. All filtering maintains source URL attribution. No data transformation beyond filtering.

### ✅ III. Test-Driven Development (NON-NEGOTIABLE)
**Status**: PASS  
**Rationale**: Will implement TDD workflow. Test files: `tests/unit/test_filters.py`, `tests/integration/test_cli.py`. Will cover edge cases from spec (malformed XML, missing dates, conflicting filters).

### ✅ IV. Incremental Processing
**Status**: N/A  
**Rationale**: This is a stateless filter script, not a data processing pipeline. Reads sitemap once, filters in-memory, outputs results. No checkpointing needed for this scope.

### ✅ V. Observability & Monitoring
**Status**: PASS  
**Rationale**: FR-015 requires displaying filter statistics. FR-006/FR-012 require clear error messages with exit codes. Will use structured output for errors to stderr.

### ✅ VI. Package Management (NON-NEGOTIABLE)
**Status**: PASS  
**Rationale**: Will use `uv` exclusively. Standard library dependencies only (no external packages needed). Script invoked via `uv run python src/sitemap_filter.py`.

### ✅ VII. Git Commit Standards (NON-NEGOTIABLE)
**Status**: PASS  
**Rationale**: All commits will follow Conventional Commits format with scope `sitemap-filter`. Simple commits (1-2 files) use subject only, complex commits (3+ files) use bullet points.

## Project Structure

### Documentation (this feature)

```text
specs/001-sitemap-filter/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── cli-interface.md # CLI contract specification
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── sitemap_filter.py    # Main CLI entry point
└── filters/
    ├── __init__.py
    ├── parser.py        # XML parsing logic
    ├── language.py      # Language detection and filtering
    ├── product.py       # Product path filtering
    └── output.py        # Output formatting (JSON/txt/xml)

tests/
├── unit/
│   ├── test_parser.py
│   ├── test_language_filter.py
│   ├── test_product_filter.py
│   └── test_output.py
├── integration/
│   └── test_cli.py
└── fixtures/
    ├── sample_sitemap.xml
    ├── malformed_sitemap.xml
    └── large_sitemap.xml
```

**Structure Decision**: Selected single project structure (Option 1) as this is a standalone CLI utility. The `src/filters/` directory provides modular separation for testability while keeping the codebase focused. Tests are organized by type (unit vs integration) with fixtures for various test scenarios.

## Complexity Tracking

> **No violations** - All constitution checks passed. This feature aligns with project principles.
