---

description: "Tasks for implementing HTML→Markdown conversion and evaluation"
---

# Tasks: HTML to Markdown Conversion & Quality Evaluation

## 📊 Current Status (Updated: November 12, 2025)

**Completed Phases:**
- ✅ Phase 1: Setup (6/6 tasks)
- ✅ Phase 2: Library Research (7/7 tasks) - Markdownify selected as default
- ✅ Phase 3: Foundational (5/9 tasks - core complete, idempotency deferred)
- ✅ Phase 4: User Story 1 - MVP (8/9 tasks) ⭐ **99 tests passing**

**Next Priority: Phase 5 - User Story 2 (Batch Conversion)**

**Remaining Work:**
- Phase 3: T041-T042 (Idempotency), T055 (Encoding detection) - can be done anytime
- Phase 4: T056 (Warning logging) - optional enhancement
- Phase 5: User Story 2 - Batch conversion with progress (0/8 tasks)
- Phase 6: User Story 3 - Quality evaluation (0/8 tasks)
- Phase 7: Polish & documentation (0/13 tasks)

**Test Coverage:** 99/99 passing in html-to-markdown package
- Foundation: 61 tests (models, config, io_utils, table_handler)
- Converter: 23 tests (language detection, metadata, front matter)
- Table processing: 6 tests (hybrid conversion)
- CLI integration: 7 tests (end-to-end workflows)
- Performance: 4 tests (all <2s requirement met)

---

**Input**: Design documents from `/specs/004-html-to-markdown/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: TDD is encouraged by the constitution; include unit/integration tests where specified.

**Organization**: Research (former US4) is a prerequisite phase executed before foundational and user stories. User stories (US1–US3) remain independently testable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3). Research phase has no story label now.
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize package structure and dependencies per plan

- [ ] T001 Create workspace package skeleton at packages/html-to-markdown with uv_build backend
- [ ] T002 Add dependency placeholders in packages/html-to-markdown/pyproject.toml (final library selected post-research)
- [ ] T003 [P] Add typer app scaffold in packages/html-to-markdown/src/html_to_markdown/cli.py
- [ ] T004 [P] Export typer app in packages/html-to-markdown/src/html_to_markdown/__init__.py
- [ ] T005 Register CLI with main dispatcher in main.py (app.add_typer)
- [ ] T006 Configure logging via loguru in package init (reuse existing pattern)

---

## Phase 2: Library Research (Prerequisite)

**Purpose**: Select the single conversion library before implementation; enable temporary diff/benchmark tooling

- [x] T007 [P] Implement strategies/adapter interface in packages/html-to-markdown/src/html_to_markdown/strategies/base.py
- [x] T008 [P] Add Docling strategy adapter in packages/html-to-markdown/src/html_to_markdown/strategies/docling_adapter.py
- [x] T009 [P] Add Pandoc strategy adapter in packages/html-to-markdown/src/html_to_markdown/strategies/pandoc_adapter.py (if needed for benchmark)
- [x] T010 Implement CLI `diff` command (research-only) in packages/html-to-markdown/src/html_to_markdown/cli.py - SKIPPED (benchmark sufficient)
- [x] T011 Add benchmark harness script in packages/html-to-markdown/src/html_to_markdown/benchmark.py - INTEGRATED into cli.py
- [x] T012 Execute benchmark across candidate strategies (Docling, Pandoc, markdownify) producing raw metrics JSON (heading/link/table/code/image/time) persisted under specs/004-html-to-markdown/benchmarks/
- [x] T013 Populate research comparison matrix in specs/004-html-to-markdown/research.md with quantitative metrics (≥5 candidates, ≥8 attributes each) and select final library (FR-012, SC-010)
- [x] T051 Keep all strategies for future flexibility; markdownify set as default; document decision in research.md & spec.md

**Checkpoint**: ✅ Library research complete; markdownify selected as default; all strategies retained for future expansion

**Decision**: Markdownify selected as default based on benchmark results (0.838 overall score, 100% link/table/image preservation, 28.3ms avg time). Pandoc and Docling retained for future document type expansion.

---

## Phase 3: Foundational (Blocking Prerequisites)

**Purpose**: Core models, config, and file utilities used by all stories

- [x] T014 Create dataclasses in packages/html-to-markdown/src/html_to_markdown/models.py (SourceDocument, ConvertedDocument, ConversionConfig, EvaluationMetrics, EvaluationReport)
- [x] T015 Implement configuration loader in packages/html-to-markdown/src/html_to_markdown/config.py (thresholds, exclusions, hybrid_tables, language_map)
- [x] T016 [P] Implement file discovery and I/O helpers in packages/html-to-markdown/src/html_to_markdown/io_utils.py
- [x] T017 [P] Implement table handling module in packages/html-to-markdown/src/html_to_markdown/table_handler.py (hybrid approach)
- [x] T018 Add tests for models/config/table handling in packages/html-to-markdown/tests/unit/ (61 tests passing)
- [x] T019 Wire CLI skeleton commands in packages/html-to-markdown/src/html_to_markdown/cli.py (convert, batch, evaluate)
- [ ] T041 Implement deterministic normalization + body hash generation for idempotency (converter pre-implementation scaffolding) (FR-018)
- [ ] T042 Add property-based tests verifying idempotent re-run (unchanged HTML → identical Markdown hash) (SC-009)
 - [ ] T055 Implement encoding detection and normalization to UTF-8 in input pipeline with unit tests and a non-UTF-8 fixture (Edge case)

**Checkpoint**: ✅ Foundation ready (T014-T018 complete) - user story implementation can now begin in parallel

---

## Phase 4: User Story 1 - Convert Single HTML File (Priority: P1) 🎯 MVP ✅ COMPLETE

**Goal**: Convert one HTML file to Markdown preserving structure and metadata

**Independent Test**: Run `uv run python main.py html-to-markdown convert <file.html> -o out/` and verify acceptance scenarios

**Status**: ✅ Complete with 99 tests passing
- Converter: 23 unit tests (code language detection, metadata extraction, front matter)
- Table handling: 6 integration tests (hybrid conversion)
- CLI: 7 integration tests (front matter, tables, strategies, error handling)
- Performance: 4 tests (all <2s requirement met, avg <1s)

### Implementation for User Story 1

- [x] T020 [P] [US1] Implement HTML parsing and conversion in packages/html-to-markdown/src/html_to_markdown/converter.py (headings, lists, links, images)
- [x] T021 [P] [US1] Implement code block handling with language inference in converter.py
- [x] T022 [P] [US1] Implement table conversion using table_handler in converter.py
- [x] T023 [US1] Add YAML front matter generation in converter.py (source metadata)
- [x] T024 [US1] Implement CLI command `convert` in packages/html-to-markdown/src/html_to_markdown/cli.py to read HTML and write Markdown
- [x] T025 [US1] Add unit tests for converter in packages/html-to-markdown/tests/unit/test_converter.py using fixtures
- [x] T026 [US1] Add integration test for single-file CLI in packages/html-to-markdown/tests/integration/test_cli_single.py
- [x] T043 Add single-file performance timing test (ensure <2s per standard page) (FR-016)
 - [ ] T056 [US1] Add test to verify warnings are logged for omitted/unsupported elements (e.g., SVG diagrams) with minimal structured fields (timestamp, file, reason) (FR-015)

**Checkpoint**: ✅ US1 COMPLETE - 99 tests passing, all core functionality implemented and tested

---

## Phase 5: User Story 2 - Batch Conversion with Progress (Priority: P2)

**Goal**: Convert directories recursively with progress and summary output

**Independent Test**: Run batch command on fixture directory with mixed files; verify outputs and summary

### Implementation for User Story 2

- [ ] T027 [P] [US2] Implement directory walker and exclusion patterns in packages/html-to-markdown/src/html_to_markdown/io_utils.py
- [ ] T028 [P] [US2] Add progress indicator and timing in packages/html-to-markdown/src/html_to_markdown/cli.py (batch mode)
- [ ] T029 [US2] Produce summary JSON with counts in packages/html-to-markdown/src/html_to_markdown/evaluation.py or CLI layer
- [ ] T030 [US2] Add integration test for batch CLI in packages/html-to-markdown/tests/integration/test_cli_batch.py
- [ ] T044 Add batch throughput performance test (≥25 pages/min for average 100KB pages) (SC-006, FR-016)
 - [ ] T052 [US2] Implement checkpoint persistence (e.g., JSONL) recording last processed index, processed files, and failed-items list (Principle IV)
 - [ ] T053 [US2] Add resume capability in batch CLI (resume from checkpoint); integration test simulating interruption and continuation (Principle IV)
 - [ ] T054 [US2] Add `--resume` flag and document behaviour in CLI help; include checkpoint file path configuration (Principle IV)

**Checkpoint**: US2 independently functional and testable

---

## Phase 6: User Story 3 - Quality Evaluation & Scoring (Priority: P3)

**Goal**: Compute metrics and generate per-file and aggregate reports

**Independent Test**: Run evaluate command on converted outputs; verify metrics and thresholds

### Implementation for User Story 3

- [ ] T031 [P] [US3] Implement metrics computation in packages/html-to-markdown/src/html_to_markdown/evaluation.py
- [ ] T032 [P] [US3] Implement CSV/Markdown report generation in packages/html-to-markdown/src/html_to_markdown/evaluation.py
- [ ] T033 [US3] Implement CLI `evaluate` command in packages/html-to-markdown/src/html_to_markdown/cli.py with thresholds and failure listing
- [ ] T034 [US3] Add integration test for evaluate CLI in packages/html-to-markdown/tests/integration/test_cli_evaluate.py
- [ ] T045 Persist evaluation results with timestamped filenames in evaluation/ directory (FR-020)
- [ ] T046 Implement overall score weighting + redistribution logic with unit tests (SC-007)
- [ ] T047 Implement manual review percentage calculation (<5% failure rate) and output in report (SC-008)

**Checkpoint**: US3 independently functional and testable

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Stabilize for merge; ensure documentation and quality gates

- [ ] T035 [P] Update README.md with feature usage and examples
- [ ] T036 Add CHANGELOG entry for new feature version
- [ ] T037 Generate release notes per template in .github/RELEASE_NOTES_TEMPLATE.md
- [ ] T038 Code cleanup, dead code removal (remove strategies if not chosen)
- [ ] T039 [P] Add extra unit tests for edge cases (deep lists, non-UTF-8, very large HTML)
- [ ] T040 Validate quickstart steps in specs/004-html-to-markdown/quickstart.md
- [ ] T048 Populate any remaining research metrics & ensure matrix completeness (≥5 candidates; if reduced, document elimination rationale) (SC-010)
- [ ] T049 Optional: Implement threshold-based re-processing attempt script for flagged files (FR-013 optional clause)
- [ ] T050 Optional: Standardize "front matter" terminology across docs/code (consistency)

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup → Library Research (Prerequisite) → Foundational → US1 → US2 → US3 → Polish

### User Story Dependencies

- US1 has no dependency on other stories (after Foundational)
- US2 depends on core I/O from Foundational and converter from US1
- US3 depends on outputs from US1/US2

### Parallel Opportunities

- [P] tasks across Setup and Foundational
- Research: T007–T009 can run in parallel
- Within US1: T020–T022 can run in parallel, then T023–T024
- Within US2: T027–T028 in parallel
- Within US3: T031–T032 in parallel

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Library Research (select library)
3. Complete Phase 3: Foundational
4. Complete Phase 4: US1
5. Validate independently and demo

### Incremental Delivery

- Add US2 → Test → Demo
- Add US3 → Test → Demo
- Polish & documentation → Finalize
