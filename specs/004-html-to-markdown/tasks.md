---

description: "Tasks for implementing HTML→Markdown conversion and evaluation"
---

# Tasks: HTML to Markdown Conversion & Quality Evaluation

**Input**: Design documents from `/specs/004-html-to-markdown/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: TDD is encouraged by the constitution; include unit/integration tests where specified.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)
- [ ] T004 [P] Export typer app in packages/html-to-markdown/src/html_to_markdown/__init__.py
- [ ] T006 Configure logging via loguru in package init (reuse existing pattern)

---

## Phase 2: Foundational (Blocking Prerequisites)
- [ ] T011 Add tests for models/config/table handling in packages/html-to-markdown/tests/unit/
- [ ] T012 Wire CLI skeleton commands in cli.py (convert, batch, evaluate, diff) with no-op stubs


---

## Phase 3: User Story 1 - Convert Single HTML File (Priority: P1) 🎯 MVP

- [ ] T013 [P] [US1] Implement HTML parsing and conversion in packages/html-to-markdown/src/html_to_markdown/converter.py (headings, lists, links, images)
- [ ] T014 [P] [US1] Implement code block handling with language inference in converter.py
- [ ] T015 [P] [US1] Implement table conversion using table_handler in converter.py
- [ ] T017 [US1] Implement CLI command `convert` in cli.py to read HTML and write Markdown
- [ ] T018 [US1] Add unit tests for converter in packages/html-to-markdown/tests/unit/test_converter.py using fixtures
- [ ] T019 [US1] Add integration test for single-file CLI in packages/html-to-markdown/tests/integration/test_cli_single.py

**Checkpoint**: US1 independently functional and testable

---

## Phase 4: User Story 2 - Batch Conversion with Progress (Priority: P2)
- [ ] T020 [P] [US2] Implement directory walker and exclusion patterns in io_utils.py
- [ ] T021 [P] [US2] Add progress indicator and timing in cli.py (batch mode)
- [ ] T022 [US2] Produce summary JSON with counts in packages/html-to-markdown/src/html_to_markdown/evaluation.py or cli layer

**Checkpoint**: US2 independently functional and testable

---

## Phase 5: User Story 3 - Quality Evaluation & Scoring (Priority: P3)

**Goal**: Compute metrics and generate per-file and aggregate reports

- [ ] T024 [P] [US3] Implement metrics computation in packages/html-to-markdown/src/html_to_markdown/evaluation.py
- [ ] T025 [P] [US3] Implement CSV/Markdown report generation in evaluation.py
- [ ] T026 [US3] Implement CLI `evaluate` command in cli.py with thresholds and failure listing

**Checkpoint**: US3 independently functional and testable

---

## Phase 6: User Story 4 - Comparative Library Research (Priority: P4)

**Goal**: Enable research-time diff and multi-strategy benchmark (temporary)

- [ ] T028 [P] [US4] Implement strategies/adapter interface in packages/html-to-markdown/src/html_to_markdown/strategies/base.py
- [ ] T029 [P] [US4] Add docling strategy adapter in strategies/docling_adapter.py
- [ ] T030 [P] [US4] Add pandoc strategy adapter in strategies/pandoc_adapter.py (if needed for benchmark)
- [ ] T032 [US4] Add small benchmark harness script in packages/html-to-markdown/src/html_to_markdown/benchmark.py
- [ ] T033 [US4] Populate research comparison matrix in specs/004-html-to-markdown/research.md
- [ ] T034 [US4] Remove unselected strategies after decision; keep chosen only

**Checkpoint**: Research completed; single library selected and codebase simplified

- [ ] T036 Add CHANGELOG entry for new feature version
- [ ] T037 Generate release notes per template in .github/RELEASE_NOTES_TEMPLATE.md
- [ ] T038 Code cleanup, dead code removal (remove strategies if not chosen)
- [ ] T039 [P] Add extra unit tests for edge cases (deep lists, non-UTF-8, very large HTML)
- [ ] T040 Validate quickstart steps in specs/004-html-to-markdown/quickstart.md

## Dependencies & Execution Order


### User Story Dependencies

### Parallel Opportunities

- [P] tasks across Setup and Foundational
- Within US1: T013–T015 can run in parallel, then T016–T017
- Within US2: T020–T021 in parallel
- Within US3: T024–T025 in parallel
- Within US4: T028–T030 in parallel

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: US1
4. Validate independently and demo

### Incremental Delivery

- Add US2 → Test → Demo
- Add US3 → Test → Demo
- Conduct US4 research → Select library → Remove unselected strategies → Polish
