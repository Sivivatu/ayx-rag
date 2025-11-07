# Implementation Tasks: Page Downloader

**Feature**: page-downloader  
**Branch**: `003-page-downloader`  
**Generated**: November 6, 2025  
**Approach**: Test-Driven Development (TDD) with user story-based incremental delivery

## Task Summary

- **Total Tasks**: 47
- **User Story 1 (P1)**: 14 tasks (MVP - Download single page)
- **User Story 2 (P2)**: 10 tasks (Batch downloads with progress)
- **User Story 3 (P3)**: 8 tasks (Incremental updates)
- **User Story 4 (P4)**: 6 tasks (Retry with exponential backoff)
- **Setup**: 4 tasks
- **Foundational**: 3 tasks
- **Polish**: 2 tasks
- **Parallel Opportunities**: 31 tasks can run in parallel within their phase

## Implementation Strategy

**MVP Scope** (User Story 1 only): 
- Download single page with basic error handling
- ~14 tasks, estimated 1-2 days
- Delivers immediate value for manual content collection

**Incremental Delivery**:
1. **Sprint 1**: US1 (P1) - Single page download foundation
2. **Sprint 2**: US2 (P2) - Batch processing with progress tracking  
3. **Sprint 3**: US3 (P3) - Incremental updates for efficiency
4. **Sprint 4**: US4 (P4) - Production reliability with retry logic

Each user story is independently testable and deployable.

---

## Phase 1: Setup

**Goal**: Initialize project structure and dependencies

### Tasks

- [x] T001 Create package directory structure at `packages/page-downloader/`
- [x] T002 Create `packages/page-downloader/pyproject.toml` with uv_build backend and package metadata
- [x] T003 Add workspace dependencies to root `pyproject.toml`: httpx>=0.25.0, rich>=13.0.0, typer>=0.20.0, loguru>=0.7.3
- [x] T004 Add dev dependencies to root: respx>=0.20.0, pytest>=8.4.2, pytest-cov>=7.0.0

**Completion Criteria**: `uv sync` runs successfully, all dependencies resolved

---

## Phase 2: Foundational Components

**Goal**: Implement shared components needed by all user stories

### Tasks

- [x] T005 [P] Create `packages/page-downloader/src/page_downloader/__init__.py` (export app for main.py integration)
- [x] T006 [P] Create `packages/page-downloader/src/page_downloader/exceptions.py` with custom exception hierarchy (PageDownloaderError, DownloadError, ValidationError, RobotsDeniedError, ConfigurationError)
- [x] T007 Create `packages/page-downloader/src/page_downloader/models.py` with DownloadConfig dataclass (validate config fields in __post_init__)

**Completion Criteria**: Exceptions and models importable, config validation working

**Dependencies**: Must complete Setup phase first

---

## Phase 3: User Story 1 - Download Single Page (P1)

**Goal**: Download raw HTML from single URL and save to disk

**Independent Test**: Provide URL, verify HTML saved to correct path with proper logging

### Tasks

#### Test Setup
- [x] T008 [P] [US1] Create test fixture `tests/fixtures/sample_pages/valid.html` with sample HTML content
- [x] T009 [P] [US1] Create test fixture `tests/fixtures/sample_pages/large.html` (>5MB) for file size validation
- [x] T010 [P] [US1] Create `tests/conftest.py` with pytest fixtures (sample_config, temp_output_dir, mock_response)

#### Core Implementation
- [x] T011 [US1] Write tests for path sanitization in `tests/unit/test_path_utils.py` (invalid chars, query params, fragments, Unicode)
- [x] T012 [US1] Implement `src/page_downloader/path_utils.py` with sanitize_url_path() function (replace invalid chars with _, strip query/fragments)
- [x] T013 [US1] Write tests for HTML validation in `tests/unit/test_validator.py` (Content-Type checking, non-HTML detection)
- [x] T014 [US1] Implement `src/page_downloader/validator.py` with is_html_content() function
- [x] T015 [US1] Write tests for file operations in `tests/unit/test_downloader.py` (atomic writes, directory creation, disk space handling)
- [x] T016 [US1] Implement `src/page_downloader/downloader.py` with HTTPDownloader class (httpx.Client, streaming, atomic writes, timeouts)
- [ ] T017 [US1] Write tests for CLI single URL mode in `tests/integration/test_cli.py` (success, network error, invalid URL, non-HTML)
- [ ] T018 [US1] Implement `src/page_downloader/cli.py` with typer app and download() command (single URL argument, output-dir option)
- [ ] T019 [US1] Update `main.py` to register page-downloader CLI app with app.add_typer()
- [ ] T020 [US1] Test end-to-end: `uv run python main.py page-downloader https://help.alteryx.com/current/en/designer/tools.html`
- [ ] T021 [US1] Verify logs with timestamp, URL, file size, and file path per FR-017

**Completion Criteria**: Single URL downloads work with proper error handling, all US1 tests pass

**Dependencies**: Must complete Foundational phase first

**Parallel Opportunities**: T008-T010 (fixtures), then T011+T013+T015+T017 (tests in parallel)

---

## Phase 4: User Story 2 - Batch Download from URL List (P2)

**Goal**: Process multiple URLs from file with progress tracking and error resilience

**Independent Test**: Provide URL list file, verify all URLs processed with progress display and summary stats

### Tasks

#### Test Setup
- [ ] T022 [P] [US2] Create test fixture `tests/fixtures/url_lists/batch.txt` with 10 sample URLs
- [ ] T023 [P] [US2] Create test fixture `tests/fixtures/url_lists/mixed_urls.txt` with valid, invalid, and non-HTML URLs

#### Core Implementation
- [ ] T024 [US2] Write tests for URLList parsing in `tests/unit/test_models.py` (parse file, validate URLs, handle malformed lines)
- [ ] T025 [US2] Implement URLList class in `src/page_downloader/models.py` with from_file() method (validate URLs per FR-027a)
- [ ] T026 [US2] Write tests for DownloadSession in `tests/unit/test_models.py` (track counts, calculate statistics, session state)
- [ ] T027 [US2] Implement DownloadSession class in `src/page_downloader/models.py` (track total/success/failed/skipped counts)
- [ ] T028 [US2] Write tests for progress display in `tests/unit/test_progress.py` (rich progress bar, quiet mode, verbose mode)
- [ ] T029 [US2] Implement `src/page_downloader/progress.py` with ProgressTracker class using rich.Progress (FR-016)
- [ ] T030 [US2] Write tests for batch CLI mode in `tests/integration/test_cli.py` (file input, progress display, continue on errors, summary stats)
- [ ] T031 [US2] Update CLI in `src/page_downloader/cli.py` to accept file path, add --delay, --verbose, --quiet options

**Completion Criteria**: Batch downloads process all URLs sequentially, display progress, continue after errors, show summary (FR-018)

**Dependencies**: Must complete US1 first

**Parallel Opportunities**: T022-T023 (fixtures), then T024+T026+T028+T030 (tests in parallel)

---

## Phase 5: User Story 3 - Incremental Updates (P3)

**Goal**: Skip unchanged pages based on Last-Modified headers

**Independent Test**: Run download twice, verify unchanged pages skipped on second run

### Tasks

#### Core Implementation
- [ ] T032 [US3] Write tests for incremental checking in `tests/unit/test_downloader.py` (HEAD requests, Last-Modified comparison, file timestamp)
- [ ] T033 [US3] Implement check_if_modified() method in HTTPDownloader (FR-013: compare local mtime with remote Last-Modified)
- [ ] T034 [US3] Update download() method in HTTPDownloader to skip unchanged pages (FR-014), log "unchanged" status
- [ ] T035 [US3] Write tests for --force flag in `tests/integration/test_cli.py` (bypass incremental check, re-download all)
- [ ] T036 [US3] Add --force option to CLI in `src/page_downloader/cli.py` (FR-015)
- [ ] T037 [US3] Write integration tests in `tests/integration/test_incremental.py` (two-run scenario, verify 80% time reduction per SC-004)
- [ ] T038 [US3] Update DownloadResult model to include skip_reason field
- [ ] T039 [US3] Test 404 handling: verify local file preserved when remote returns 404

**Completion Criteria**: Incremental mode skips unchanged pages, --force bypasses check, 80% time reduction on repeated runs

**Dependencies**: Must complete US2 first

**Parallel Opportunities**: T032+T035+T037 (tests in parallel)

---

## Phase 6: User Story 4 - Retry Failed Downloads (P4)

**Goal**: Automatic retry with exponential backoff for transient failures

**Independent Test**: Simulate network failures, verify retry behavior with backoff

### Tasks

#### Core Implementation
- [ ] T040 [US4] Write tests for retry logic in `tests/unit/test_downloader.py` (timeouts, 5xx errors, 429 with Retry-After, exponential backoff, jitter)
- [ ] T041 [US4] Implement retry_with_backoff() decorator in `src/page_downloader/downloader.py` (exponential backoff + jitter per FR-009)
- [ ] T042 [US4] Update HTTPDownloader to distinguish retryable/non-retryable errors (FR-011: 5xx, 429, timeouts retryable; 4xx non-retryable)
- [ ] T043 [US4] Implement special handling for HTTP 429 in HTTPDownloader (FR-011a: respect Retry-After header, 2x backoff)
- [ ] T044 [US4] Add --max-retries option to CLI in `src/page_downloader/cli.py` (FR-010)
- [ ] T045 [US4] Write integration tests in `tests/integration/test_cli.py` (verify retry counts logged, max retries respected)

**Completion Criteria**: Transient failures retry up to max attempts, 429 respects Retry-After, 4xx errors skip immediately

**Dependencies**: Must complete US3 first (or can start after US2)

**Parallel Opportunities**: T040+T045 (tests in parallel with implementation)

---

## Phase 7: Polish & Cross-Cutting Concerns

**Goal**: Complete remaining requirements and production readiness

### Tasks

#### Additional Features
- [ ] T046 [P] Implement robots.txt checking in `src/page_downloader/validator.py` using urllib.robotparser (FR-024), add --ignore-robots-txt flag (FR-024a)
- [ ] T047 [P] Implement --dry-run mode in CLI (FR-025: preview downloads without executing)

**Completion Criteria**: All functional requirements implemented, all tests pass with >95% coverage

**Dependencies**: Complete all user stories

---

## Dependency Graph

### Story Completion Order

```
Setup (Phase 1)
  ↓
Foundational (Phase 2)
  ↓
User Story 1 (P1) ← MUST COMPLETE FIRST (MVP)
  ↓
User Story 2 (P2) ← Requires US1 downloader
  ↓
User Story 3 (P3) ← Requires US2 batch processing
  ↓
User Story 4 (P4) ← Can start after US2, parallel with US3
  ↓
Polish (Phase 7)
```

### Within-Story Parallelization

**US1 Parallel Groups**:
1. T008, T009, T010 (fixtures) - no dependencies
2. T011, T013, T015, T017 (tests) - after fixtures
3. T012, T014, T016 (implementation) - after corresponding tests

**US2 Parallel Groups**:
1. T022, T023 (fixtures) - no dependencies
2. T024, T026, T028, T030 (tests) - after fixtures
3. T025, T027, T029 (implementation) - after corresponding tests

**US3 Parallel Groups**:
1. T032, T035, T037 (tests) - can run in parallel
2. T033, T034, T036 (implementation) - after corresponding tests

**US4 Parallel Groups**:
1. T040, T045 (tests) - can run in parallel
2. T041, T042, T043, T044 (implementation) - after tests

---

## Expanded Subtasks (Granular)

These subtasks break down complex implementation tasks into small, actionable steps (suitable for individual PRs). IDs continue sequentially from existing tasks.

### US1 (P1) - MVP Detailed Subtasks

- [ ] T048 [US1] Create `src/page_downloader/utils/http_client.py` with HTTP client wrapper class skeleton (methods: head(), stream_get(), close())
- [ ] T049 [US1] Write unit tests `tests/unit/test_http_client.py` for http client wrapper (mock httpx responses with respx)
- [ ] T050 [US1] Implement `http_client.head()` to send HEAD request with timeouts and SSL verification
- [ ] T051 [US1] Implement `http_client.stream_get()` to stream response body in chunks and yield bytes
- [ ] T052 [US1] Create `src/page_downloader/utils/io.py` implementing `atomic_write()` (tempfile + os.replace) and unit tests `tests/unit/test_io.py`
- [ ] T053 [US1] Implement `src/page_downloader/downloader.py::download_one()` orchestration: run head(), validate content-type, stream_get(), enforce max file size, call atomic_write()
- [ ] T054 [US1] Write unit tests `tests/unit/test_downloader_download_one.py` covering success, non-HTML skip, size-exceed, and partial failure cleanup
- [ ] T055 [US1] Add logging calls in downloader for start/finish/skip/error including URL, bytes and path; write tests to assert log messages
- [ ] T056 [US1] Implement `src/page_downloader/path_utils.py::sanitize_url_path()` (replace invalid chars, strip query/fragments) and unit tests
- [ ] T057 [US1] Implement CLI wiring for single-URL mode to call download_one() and return proper exit codes; add integration test for CLI single URL
- [ ] T058 [US1] Add sample fixture `tests/fixtures/sample_pages/non_html.pdf` and a test to ensure non-HTML is skipped and logged

### US2 (P2) - Batch Processing Detailed Subtasks

- [ ] T059 [US2] Implement `src/page_downloader/models.py::URLList.from_file()` to parse file, validate lines, emit (line_no, url) tuples and unit tests `tests/unit/test_urllist.py`
- [ ] T060 [US2] Implement `src/page_downloader/models.py::DownloadSession` helpers: start(), record_result(), summary() and unit tests `tests/unit/test_downloadsession.py`
- [ ] T061 [US2] Implement `src/page_downloader/progress.py::ProgressTracker` using rich with methods start(total), advance(), stop(), and unit tests `tests/unit/test_progress_tracker.py`
- [ ] T062 [US2] Integrate batch loop in `src/page_downloader/downloader.py::download_batch()` which iterates URLList, calls download_one(), updates DownloadSession and ProgressTracker; add integration tests using respx to mock multiple endpoints
- [ ] T063 [US2] Implement error classification helper `src/page_downloader/utils/errors.py` to map httpx exceptions/status codes to retryable boolean; unit tests `tests/unit/test_errors_classification.py`
- [ ] T064 [US2] Add CLI batch mode entry (file input) and options: --delay, --verbose, --quiet; add integration tests for file input mode
- [ ] T065 [US2] Implement summary output routine that prints DownloadSession.summary() at end and tests assert summary content for sample runs

### Misc / Polish Subtasks

- [ ] T066 [P] Add `tests/fixtures/robots/robots_allow.txt` and `robots_disallow.txt` and unit tests for robots checking in `tests/unit/test_robots.py`
- [ ] T067 [P] Add CI job configuration snippet to run `uv run pytest` for `packages/page-downloader/` (create `.github/workflows/page-downloader-ci.yml` placeholder)
- [ ] T068 [P] Create `packages/page-downloader/README.md` minimal usage examples (single URL, batch, incremental) and note dependencies

---

These subtasks are intentionally small and focused so each maps to a single unit of work and corresponding tests. After these are implemented, merge into the main feature branch in small PRs.


## Testing Strategy

### Test Coverage Targets
- Unit tests: >95% coverage for models, downloader, validator, path_utils
- Integration tests: All CLI scenarios from spec acceptance criteria
- Fixtures: Realistic HTML samples, various URL formats, edge cases

### TDD Workflow (per quickstart.md)
1. Write test for requirement
2. Run test (should fail)
3. Implement minimal code
4. Run test (should pass)
5. Refactor for clarity

### Key Test Scenarios
- **HTTP mocking**: Use respx for all HTTP interactions in tests
- **File operations**: Use pytest tmp_path fixture for isolated test files
- **Error simulation**: Mock timeouts, 5xx errors, 429 responses, disk full
- **Edge cases**: Malformed URLs, non-HTML, redirects, partial downloads, invalid chars

---

## Exit Criteria

### Per User Story
- ✅ All acceptance scenarios pass
- ✅ Unit tests pass with >95% coverage
- ✅ Integration tests pass end-to-end
- ✅ Independent test criteria verified
- ✅ No regressions in previous stories

### Overall Completion
- ✅ All 32 functional requirements (FR-001 to FR-027e) implemented
- ✅ All 8 success criteria (SC-001 to SC-008) verified
- ✅ All 8 edge cases handled per clarifications
- ✅ Constitution compliance: All 9 principles satisfied
- ✅ Documentation: README.md updated, CHANGELOG.md entry, release notes generated
- ✅ CLI integration: `python main.py page-downloader --help` works
- ✅ Test coverage: >95% overall, all critical paths covered

---

## Notes

**Workspace Dependencies** (per FR-027): 
- httpx, typer, loguru, rich declared in root `pyproject.toml`
- No package-specific dependencies needed

**File Paths**: All paths in tasks are relative to repository root `/workspaces/uv-ayx-rag/`

**TDD Approach**: Tests written before implementation for all core functionality per Constitution Principle III

**Parallel Execution**: 31 tasks marked with [P] can run in parallel within their phase (different files, no cross-dependencies)
