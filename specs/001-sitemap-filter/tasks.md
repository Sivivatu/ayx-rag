# Tasks: Sitemap Filter CLI

**Input**: Design documents from `/specs/001-sitemap-filter/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli-interface.md

**Tests**: Per constitution Principle III (TDD), tests are REQUIRED and must be written BEFORE implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

Single project structure (from plan.md):
- `src/` - Source code at repository root
- `tests/` - Tests at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project directory structure: src/, src/filters/, tests/unit/, tests/integration/, tests/fixtures/
- [ ] T002 Install runtime dependencies: uv add typer loguru
- [ ] T003 Install dev dependencies: uv add --dev pytest pytest-cov
- [ ] T004 [P] Create empty __init__.py files in src/filters/ and tests/unit/
- [ ] T005 [P] Create pytest.ini configuration file at repository root
- [ ] T006 [P] Create .gitignore entries for Python cache files and test artifacts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T007 Create test fixtures: tests/fixtures/sample_sitemap.xml (100 URLs, mixed languages/products)
- [ ] T008 [P] Create test fixtures: tests/fixtures/malformed_sitemap.xml (invalid XML for error testing)
- [ ] T009 [P] Create test fixtures: tests/fixtures/large_sitemap.xml (1000+ URLs for performance testing)
- [ ] T010 Write failing test for XML parser in tests/unit/test_parser.py
- [ ] T011 Implement XML parser in src/filters/parser.py (parse sitemap, extract loc/lastmod)
- [ ] T012 Verify XML parser test passes
- [ ] T013 Write failing test for URLEntry creation in tests/unit/test_parser.py
- [ ] T014 Implement URLEntry dataclass in src/filters/parser.py (loc, lastmod, language, products attributes)
- [ ] T015 Verify URLEntry test passes
- [ ] T016 Configure loguru logger in src/sitemap_filter.py (stderr output, info/debug/error levels)

**Checkpoint**: Foundation ready - XML parsing works, URLEntry created, logging configured. User story implementation can now begin in parallel.

---

## Phase 3: User Story 1 - Filter by Language (Priority: P1) 🎯 MVP

**Goal**: Enable filtering sitemap URLs by language code (en/de) to focus on English documentation

**Independent Test**: Run script with `--language en` flag and verify all output URLs are English (no /de/ paths)

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T017 [P] [US1] Write failing test for language detection in tests/unit/test_language_filter.py (test detect_language() with /de/ and /current/ patterns)
- [ ] T018 [P] [US1] Write failing test for language filtering in tests/unit/test_language_filter.py (test filter_by_language() returns only matching entries)
- [ ] T019 [P] [US1] Write failing integration test in tests/integration/test_cli.py (test CLI with --language en flag)

### Implementation for User Story 1

- [ ] T020 [US1] Implement detect_language() function in src/filters/language.py (regex pattern matching for /current/{locale}/)
- [ ] T021 [US1] Verify language detection tests pass (T017)
- [ ] T022 [US1] Implement filter_by_language() function in src/filters/language.py (filter URLEntry list by language)
- [ ] T023 [US1] Verify language filtering tests pass (T018)
- [ ] T024 [US1] Add typer CLI app definition in src/sitemap_filter.py with sitemap_file argument
- [ ] T025 [US1] Add --language option to CLI in src/sitemap_filter.py (type: List[str], help text)
- [ ] T026 [US1] Integrate language filter into main() function in src/sitemap_filter.py
- [ ] T027 [US1] Add error handling for invalid language codes in src/sitemap_filter.py
- [ ] T028 [US1] Add logging for language filter operations using loguru
- [ ] T029 [US1] Verify CLI integration test passes (T019)

**Checkpoint**: At this point, User Story 1 should be fully functional - can filter by language via CLI

---

## Phase 4: User Story 2 - Filter by Product Path (Priority: P2)

**Goal**: Enable filtering URLs by product path segments (designer/server/etc.) for focused documentation subsets

**Independent Test**: Run script with `--product designer` flag and verify all output URLs contain /designer/ path segment

### Tests for User Story 2

- [ ] T030 [P] [US2] Write failing test for product extraction in tests/unit/test_product_filter.py (test extract_products() with various URL patterns)
- [ ] T031 [P] [US2] Write failing test for product filtering in tests/unit/test_product_filter.py (test filter_by_product() with single and multiple products)
- [ ] T032 [P] [US2] Write failing integration test in tests/integration/test_cli.py (test CLI with --product designer flag)

### Implementation for User Story 2

- [ ] T033 [US2] Implement extract_products() function in src/filters/product.py (parse URL path for product segments)
- [ ] T034 [US2] Verify product extraction test passes (T030)
- [ ] T035 [US2] Implement filter_by_product() function in src/filters/product.py (OR logic for multiple products)
- [ ] T036 [US2] Verify product filtering test passes (T031)
- [ ] T037 [US2] Add --product option to CLI in src/sitemap_filter.py (type: List[str], multiple values allowed)
- [ ] T038 [US2] Integrate product filter into main() function in src/sitemap_filter.py
- [ ] T039 [US2] Add logging for product filter operations using loguru
- [ ] T040 [US2] Verify CLI integration test passes (T032)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently (can filter by language OR product)

---

## Phase 5: User Story 3 - Combine Multiple Filters (Priority: P3)

**Goal**: Enable combining language and product filters simultaneously (AND logic across types, OR within type)

**Independent Test**: Run script with `--language en --product designer` and verify output matches both criteria

### Tests for User Story 3

- [ ] T041 [P] [US3] Write failing test for combined filters in tests/unit/test_filters.py (test apply_filters() with both language and product criteria)
- [ ] T042 [P] [US3] Write failing integration test in tests/integration/test_cli.py (test CLI with multiple --language and --product flags)
- [ ] T043 [P] [US3] Write failing test for no matches scenario in tests/integration/test_cli.py (conflicting filters result)

### Implementation for User Story 3

- [ ] T044 [US3] Implement FilterCriteria dataclass in src/filters/__init__.py (languages and products attributes)
- [ ] T045 [US3] Implement apply_filters() function in src/filters/__init__.py (AND across types, OR within type)
- [ ] T046 [US3] Verify combined filter test passes (T041)
- [ ] T047 [US3] Update main() in src/sitemap_filter.py to use apply_filters() with FilterCriteria
- [ ] T048 [US3] Add handling for empty results with informative message
- [ ] T049 [US3] Add logging for filter statistics (total URLs, filtered count)
- [ ] T050 [US3] Verify CLI integration tests pass (T042, T043)

**Checkpoint**: All filtering combinations should now work - language, product, or both together

---

## Phase 6: User Story 4 - Output Format Options (Priority: P4)

**Goal**: Support multiple output formats (JSON, txt, xml) for integration with downstream tools

**Independent Test**: Run script with each format flag and verify output structure matches specification

### Tests for User Story 4

- [ ] T051 [P] [US4] Write failing test for JSON formatter in tests/unit/test_output.py (test format_json() produces valid JSON with total_urls, filtered_urls, results)
- [ ] T052 [P] [US4] Write failing test for text formatter in tests/unit/test_output.py (test format_txt() produces one URL per line)
- [ ] T053 [P] [US4] Write failing test for XML formatter in tests/unit/test_output.py (test format_xml() produces valid sitemap XML)
- [ ] T054 [P] [US4] Write failing integration test in tests/integration/test_cli.py (test CLI with --format json/txt/xml flags)
- [ ] T055 [P] [US4] Write failing integration test for file output in tests/integration/test_cli.py (test --output flag writes to file)
- [ ] T056 [P] [US4] Write failing integration test for dry-run in tests/integration/test_cli.py (test --dry-run shows stats only)

### Implementation for User Story 4

- [ ] T057 [P] [US4] Implement format_json() in src/filters/output.py (return dict with total_urls, filtered_urls, results)
- [ ] T058 [P] [US4] Implement format_txt() in src/filters/output.py (return newline-separated URLs)
- [ ] T059 [P] [US4] Implement format_xml() in src/filters/output.py (construct sitemap XML with ElementTree)
- [ ] T060 [US4] Verify formatter tests pass (T051, T052, T053)
- [ ] T061 [US4] Add --format option to CLI in src/sitemap_filter.py (choices: json/txt/xml, default: json)
- [ ] T062 [US4] Add --output option to CLI in src/sitemap_filter.py (file path for output)
- [ ] T063 [US4] Add --dry-run flag to CLI in src/sitemap_filter.py (show stats only, no URL output)
- [ ] T064 [US4] Integrate formatters into main() function in src/sitemap_filter.py
- [ ] T065 [US4] Implement file writing logic in src/sitemap_filter.py (write to file if --output specified)
- [ ] T066 [US4] Implement dry-run logic in src/sitemap_filter.py (skip formatting, print stats to stderr)
- [ ] T067 [US4] Add --help and --version flags using typer decorators
- [ ] T068 [US4] Verify all format integration tests pass (T054, T055, T056)

**Checkpoint**: All output formats working, file output supported, dry-run mode functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T069 [P] Add error handling for file not found in src/sitemap_filter.py (exit code 1)
- [ ] T070 [P] Add error handling for malformed XML in src/filters/parser.py (exit code 1 with line number)
- [ ] T071 [P] Add validation for sitemap file size in src/sitemap_filter.py (warn if >10MB)
- [ ] T072 Add performance logging in src/sitemap_filter.py (parsing time, filtering time, output time)
- [ ] T073 Write unit tests for edge cases in tests/unit/test_parser.py (missing lastmod, empty URLs, encoding issues)
- [ ] T074 Write performance test in tests/integration/test_performance.py (verify <3 seconds for 35k URLs)
- [ ] T075 [P] Update quickstart.md with final CLI examples and command reference
- [ ] T076 [P] Add docstrings to all public functions (Google style)
- [ ] T077 Run pytest with coverage: uv run pytest --cov=src --cov-report=term-missing (verify >80%)
- [ ] T078 Run integration tests from quickstart.md validation scenarios
- [ ] T079 [P] Code cleanup: remove debug prints, unused imports, fix linting issues
- [ ] T080 Final commit: test(sitemap-filter): verify all contract tests pass per cli-interface.md

---

## Phase 8: Documentation & Release

**Purpose**: Update project documentation and prepare release notes (REQUIRED for feature completion)

- [ ] T081 Update README.md Features section with sitemap-filter capabilities and usage examples
- [ ] T082 Update README.md Quick Start section with sitemap-filter installation commands
- [ ] T083 [P] Create CHANGELOG.md entry for version 0.2.0 (sitemap-filter feature)
- [ ] T084 [P] Generate release notes from conventional commits using git log
- [ ] T085 Update project version in relevant files (if pyproject.toml exists)
- [ ] T086 Create feature demo examples in README.md showing real sitemap filtering use cases
- [ ] T087 Final review: Verify README accuracy, links work, examples tested
- [ ] T088 Final commit: docs(sitemap-filter): update README and create release notes for v0.2.0

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories CAN proceed in parallel (if staffed) after Phase 2
  - OR sequentially in priority order: US1 (P1) → US2 (P2) → US3 (P3) → US4 (P4)
- **Polish (Phase 7)**: Depends on all user stories being complete
- **Documentation & Release (Phase 8)**: Depends on Polish completion - REQUIRED before feature considered complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent of US1 (different module: language.py vs product.py)
- **User Story 3 (P3)**: Depends on US1 AND US2 being complete (combines their filters)
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Independent of US1/US2/US3 (different module: output.py)

### Within Each User Story

1. Write all tests first (marked [P] can run in parallel)
2. Verify tests FAIL before implementation
3. Implement core functions (marked [P] can run in parallel if in different files)
4. Verify unit tests pass
5. Integrate into CLI (sequential - modifies src/sitemap_filter.py)
6. Verify integration tests pass
7. Add logging and error handling
8. Story complete - checkpoint reached

### Parallel Opportunities

**Phase 1 (Setup)**: All tasks except T001 can run in parallel
- T002, T003, T004, T005, T006 all modify different files

**Phase 2 (Foundational)**: Test fixture creation can run in parallel
- T007, T008, T009 create different fixture files
- Parser implementation is sequential (TDD cycle: test → implement → verify)

**User Story Tests**: All test files within a story can be written in parallel
- US1: T017, T018, T019 all write to different test files
- US2: T030, T031, T032 all write to different test files
- US3: T041, T042, T043 all write to different test files
- US4: T051, T052, T053, T054, T055, T056 all write to different test files

**User Story Implementation**: Module-specific tasks can run in parallel
- US1: Once tests written, language.py implementation is independent
- US2: Once tests written, product.py implementation is independent
- US4: T057, T058, T059 all write to different functions in output.py

**Cross-Story Parallelism** (if multiple developers available):
- After Phase 2: US1, US2, and US4 can all proceed in parallel (independent modules)
- US3 must wait for US1 and US2 to complete

**Phase 7 (Polish)**: Many tasks are independent
- T069, T070, T071, T075, T076, T079 all modify different areas/files

**Phase 8 (Documentation & Release)**: Most tasks are independent
- T081, T082, T083, T084, T086 all modify different files and can run in parallel
- T087, T088 must be sequential (review before final commit)

---

## Parallel Example: User Story 1

```bash
# Step 1: Launch all test writing for User Story 1 in parallel
Task T017: "Write failing test for language detection in tests/unit/test_language_filter.py"
Task T018: "Write failing test for language filtering in tests/unit/test_language_filter.py"
Task T019: "Write failing integration test in tests/integration/test_cli.py"

# Step 2: Run tests, verify they fail

# Step 3: Implement (sequential in this case - single module)
Task T020: "Implement detect_language() in src/filters/language.py"
Task T021: "Verify tests pass"
Task T022: "Implement filter_by_language() in src/filters/language.py"
Task T023: "Verify tests pass"

# Step 4: CLI integration (sequential - modifies same file)
Task T024-T029: CLI integration tasks in src/sitemap_filter.py
```

---

## Parallel Example: User Story 4

```bash
# Step 1: Launch all test writing for User Story 4 in parallel
Task T051: "Write failing test for JSON formatter"
Task T052: "Write failing test for text formatter"
Task T053: "Write failing test for XML formatter"
Task T054: "Write failing integration test for format flags"
Task T055: "Write failing integration test for file output"
Task T056: "Write failing integration test for dry-run"

# Step 2: Implement all formatters in parallel (different functions)
Task T057: "Implement format_json() in src/filters/output.py"
Task T058: "Implement format_txt() in src/filters/output.py"
Task T059: "Implement format_xml() in src/filters/output.py"

# These three can be done simultaneously by different developers
# or using parallel LLM task execution
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (~10 minutes)
2. Complete Phase 2: Foundational (~30 minutes) - CRITICAL blocker
3. Complete Phase 3: User Story 1 (~45 minutes)
4. **STOP and VALIDATE**: Test User Story 1 independently
   - Run: `uv run python src/sitemap_filter.py alteryx-help-current-sitemap.xml --language en`
   - Verify: Output contains only English URLs
   - Verify: Performance <3 seconds for 35k URLs
5. **MVP COMPLETE** - Can now filter sitemap by language

**Total MVP Time**: ~90 minutes for a working language filter

### Incremental Delivery

1. **Foundation** (Phase 1 + 2): XML parsing works, tests ready → ~40 minutes
2. **MVP** (Phase 3): Language filtering functional → +45 minutes = 85 minutes total
3. **Product Filter** (Phase 4): Add product filtering → +35 minutes = 120 minutes total
4. **Combined Filters** (Phase 5): Enable filter combinations → +25 minutes = 145 minutes total
5. **Output Formats** (Phase 6): Add JSON/txt/xml output → +40 minutes = 185 minutes total
6. **Polish** (Phase 7): Error handling, docs, performance → +30 minutes = 215 minutes total
7. **Documentation & Release** (Phase 8): Update README, create release notes → +20 minutes = 235 minutes total

**Total Implementation Time**: ~4 hours for complete feature with all 4 user stories and documentation

### Parallel Team Strategy

With 2-3 developers working simultaneously:

1. **Together**: Complete Setup + Foundational (~40 minutes)
2. **Split work** (after Phase 2 complete):
   - Developer A: User Story 1 (Language filter) → Phase 3
   - Developer B: User Story 2 (Product filter) → Phase 4
   - Developer C: User Story 4 (Output formats) → Phase 6
3. **Sync point**: After US1 and US2 complete
   - Developer A or B: User Story 3 (Combined filters) → Phase 5
4. **Together**: Phase 7 (Polish & validation)
5. **Split documentation** (Phase 8):
   - Developer A: README updates (T081, T082, T086)
   - Developer B: CHANGELOG and release notes (T083, T084)
   - Developer C: Version updates (T085)
6. **Together**: Final review and commit (T087, T088)

**Parallel Completion Time**: ~2.5 hours total with 3 developers (including documentation)

---

## Contract Validation

All tasks must satisfy the contracts defined in `contracts/cli-interface.md`:

- **Command signature**: `uv run python src/sitemap_filter.py <sitemap_file> [OPTIONS]`
- **Options**: --language, --product, --format, --output, --dry-run, --help, --version
- **Exit codes**: 0 (success), 1 (error), 2 (usage error)
- **Output formats**: JSON (default), txt, xml with correct schemas
- **Error messages**: Clear, actionable messages to stderr
- **Statistics**: Total URLs and filtered count to stderr

Refer to `contracts/cli-interface.md` for 18 contract test cases (TC-001 through TC-018) that must all pass.

---

## Notes

- **TDD is NON-NEGOTIABLE**: Per constitution Principle III, tests MUST be written before implementation
- **[P] tasks**: Different files, no dependencies - can run in parallel
- **[Story] label**: Maps task to specific user story for traceability
- **Each user story**: Should be independently completable and testable
- **Test-fail-implement-pass cycle**: Always verify tests fail before implementing
- **Commit frequently**: After each task or logical group of tasks
- **Checkpoint validation**: Stop at each checkpoint to validate story independently
- **Constitution compliance**: All code must follow principles in `.specify/memory/constitution.md`
- **Package management**: Use `uv` exclusively (uv add, uv run) - never use pip

---

## Success Metrics

Upon completion of all tasks, the feature should meet these criteria:

- ✅ All 18 contract tests from `cli-interface.md` pass
- ✅ Test coverage >80% (measured with pytest-cov)
- ✅ Performance: Filter 35,460 URLs in <3 seconds
- ✅ Memory: <500MB for 100k URL sitemap
- ✅ All user stories independently functional and tested
- ✅ CLI follows typer best practices with type hints
- ✅ Logging uses loguru with structured output
- ✅ Error messages are clear and actionable
- ✅ All commits follow Conventional Commits format
- ✅ Documentation in quickstart.md matches implementation
- ✅ README.md updated with feature capabilities and examples
- ✅ Release notes generated from conventional commits
- ✅ CHANGELOG.md entry created for feature version
