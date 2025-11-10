# Implementation Plan: HTML to Markdown Conversion & Quality Evaluation

**Branch**: `004-html-to-markdown` | **Date**: 2025-11-10 | **Spec**: `specs/004-html-to-markdown/spec.md`
**Input**: Feature specification from `/specs/004-html-to-markdown/spec.md`

**Note**: Generated via `/speckit.plan` workflow.

## Summary

Convert previously downloaded Alteryx help HTML pages into high-fidelity Markdown with structural preservation (headings, lists, tables, code blocks, links, images alt text) and front matter metadata. Establish an evaluation framework with quantitative metrics to select a single conversion library (Docling vs alternatives) prior to implementation. Provide batch processing, diffing during research, scoring, and reporting capabilities while adhering to project constitution (modular workspace package, TDD, uv-only, single main entry point integration).

## Technical Context

**Language/Version**: Python 3.10+ (workspace standard)  
**Primary Dependencies**: NEEDS CLARIFICATION (candidate list: docling, pandoc wrapper, markdownify/html2text, trafilatura + custom serializer, BeautifulSoup + custom renderer)  
**Storage**: Local filesystem only (HTML input, Markdown output, evaluation JSON/CSV)  
**Testing**: pytest (unit for converters, integration for batch/evaluation, property-based tests for idempotency)  
**Target Platform**: Linux (dev container Debian 13) via uv run  
**Project Type**: Workspace feature package (`packages/html-to-markdown`)  
**Performance Goals**: ≤2s per standard page (<200KB); throughput ≥25 pages/minute batch; evaluation metrics computed within ≤5 minutes for 500-page sample  
**Constraints**: Memory-efficient streaming parse for large pages (>2MB), no external network calls during conversion, pure Python (uv_build backend)  
**Scale/Scope**: Initial corpus subset (server product English); scalable to full 8,864 filtered URLs later.

Unresolved items are restricted to library choice; all other aspects are clear.

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Modular Architecture | PASS | Will create dedicated workspace package with isolated deps. |
| II. Data Pipeline Integrity | PASS | Front matter retains source path, last modified; evaluation logs preserved. |
| III. Test-Driven Development (NON-NEGOTIABLE) | PASS | Plan includes writing tests before converter implementation. |
| IV. Incremental Processing | PASS | Batch conversion with resumable progress via summary JSON; future checkpoint file optional. |
| V. Observability & Monitoring | PASS | Structured JSON summary + per-file warnings; loguru existing in workspace for logging. |
| VI. Package Management (NON-NEGOTIABLE) | PASS | uv only; declare deps in package `pyproject.toml`. |
| VII. Git Commit Standards (NON-NEGOTIABLE) | PASS | Conventional commits enforced in workflow. |
| VIII. Release Documentation (NON-NEGOTIABLE) | PASS | Will update README, CHANGELOG, release notes before merge. |
| IX. Main Entry Point (NON-NEGOTIABLE) | PASS | Feature CLI registered in `main.py` via `app.add_typer()`. |

No gate violations; proceed to Phase 0 research.

## Project Structure

### Documentation (this feature)

```text
specs/004-html-to-markdown/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
packages/html-to-markdown/
├── pyproject.toml              # uv_build backend, docling or chosen library dep
├── src/
│   └── html_to_markdown/
│       ├── __init__.py         # exports typer app
│       ├── cli.py              # CLI commands (convert, batch, evaluate, diff)
│       ├── converter.py        # HTML→Markdown logic
│       ├── evaluation.py       # Metrics computation
│       ├── table_handler.py    # Hybrid table conversion logic
│       ├── models.py           # Dataclasses (SourceDocument, ConvertedDocument, etc.)
│       ├── config.py           # Thresholds & configuration loading
│       └── strategies/         # Adapters for candidate libraries (research phase only)
└── tests/
  ├── unit/
  │   ├── test_converter.py
  │   ├── test_table_handler.py
  │   ├── test_evaluation.py
  │   └── test_config.py
  ├── integration/
  │   ├── test_cli_single.py
  │   ├── test_cli_batch.py
  │   └── test_cli_evaluate.py
  └── fixtures/
    ├── html_samples/
    ├── expected_markdown/
    └── large_pages/
```

**Structure Decision**: Use a workspace feature package consistent with existing patterns (`sitemap-filter`, `page-downloader`). Strategies subdirectory is temporary during research; only chosen library kept afterward (others removed before merge).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none) | N/A | N/A |
