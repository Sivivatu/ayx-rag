# Tasks: Sitemap Download

**Input**: Design documents from `/specs/002-sitemap-download/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/  
**Date**: 2025-11-03

**Tests**: This feature follows TDD principles per the constitution. Tests are included and MUST be written before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This project uses uv workspace packages:
- **Package root**: `packages/sitemap-download/`
- **Source code**: `packages/sitemap-download/src/sitemap_download/`
- **Tests**: `packages/sitemap-download/tests/`
- **Integration**: `main.py` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create workspace package directory structure at packages/sitemap-download/
- [ ] T002 Create pyproject.toml for sitemap-download package with httpx>=0.25.0 as package-specific dependency
- [ ] T003 [P] Verify typer and loguru exist in root pyproject.toml (httpx is package-specific only)
- [ ] T004 [P] Create package README.md at packages/sitemap-download/README.md
- [ ] T005 [P] Create __init__.py files for package structure
- [ ] T006 [P] Create test directory structure with unit/, integration/, fixtures/ at packages/sitemap-download/tests/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data models and error classes that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T007 Create base exception classes in packages/sitemap-download/src/sitemap_download/exceptions.py (SitemapDownloadError, NetworkError, ValidationError, ConfigurationError)
- [ ] T008 [P] Create DownloadConfig dataclass in packages/sitemap-download/src/sitemap_download/models.py
- [ ] T009 [P] Create DownloadProgress dataclass in packages/sitemap-download/src/sitemap_download/models.py
- [ ] T010 [P] Create DownloadResult dataclass in packages/sitemap-download/src/sitemap_download/models.py
- [ ] T011 [P] Create ValidationResult dataclass in packages/sitemap-download/src/sitemap_download/models.py
- [ ] T012 [P] Create RemoteFileInfo dataclass in packages/sitemap-download/src/sitemap_download/models.py
- [ ] T013 Export all models and exceptions in packages/sitemap-download/src/sitemap_download/__init__.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Download Latest Sitemap (Priority: P1) 🎯 MVP

**Goal**: Enable users to download the Alteryx sitemap from a remote URL with progress indication and save it locally

**Independent Test**: Run download command and verify that a valid sitemap XML file is saved to the specified location with progress displayed during download

### Tests for User Story 1 (TDD Required)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T014 [P] [US1] Create test fixture valid_sitemap.xml in packages/sitemap-download/tests/fixtures/
- [ ] T015 [P] [US1] Create test fixture large_sitemap.xml (simulated large file) in packages/sitemap-download/tests/fixtures/
- [ ] T016 [P] [US1] Write unit test test_downloader_init in packages/sitemap-download/tests/unit/test_downloader.py
- [ ] T017 [P] [US1] Write unit test test_download_success in packages/sitemap-download/tests/unit/test_downloader.py
- [ ] T018 [P] [US1] Write unit test test_download_with_progress_callback in packages/sitemap-download/tests/unit/test_downloader.py
- [ ] T019 [P] [US1] Write unit test test_download_network_error in packages/sitemap-download/tests/unit/test_downloader.py
- [ ] T020 [P] [US1] Write unit test test_download_timeout in packages/sitemap-download/tests/unit/test_downloader.py
- [ ] T021 [P] [US1] Write integration test test_cli_basic_download in packages/sitemap-download/tests/integration/test_cli.py
- [ ] T022 [P] [US1] Write unit test test_check_disk_space_sufficient (optional) in packages/sitemap-download/tests/unit/test_downloader.py
- [ ] T023 [P] [US1] Write unit test test_check_disk_space_insufficient (optional) in packages/sitemap-download/tests/unit/test_downloader.py
- [ ] T022 [P] [US1] Write unit test test_check_disk_space_sufficient (optional) in packages/sitemap-download/tests/unit/test_downloader.py
- [ ] T023 [P] [US1] Write unit test test_check_disk_space_insufficient (optional) in packages/sitemap-download/tests/unit/test_downloader.py

### Implementation for User Story 1

- [ ] T028 [US1] Create SitemapDownloader class skeleton in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T028 [US1] Create SitemapDownloader class skeleton in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T028 [US1] Create SitemapDownloader class skeleton in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T028 [US1] Create SitemapDownloader class skeleton in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T029 [US1] Implement SitemapDownloader.__init__ with config validation in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T029 [US1] Implement SitemapDownloader.__init__ with config validation in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T030 [US1] Implement check_disk_space() pre-flight check (optional) in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T030 [US1] Implement check_disk_space() pre-flight check (optional) in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T029 [US1] Implement SitemapDownloader.__init__ with config validation in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T029 [US1] Implement SitemapDownloader.__init__ with config validation in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T031 [US1] Implement HTTP GET with streaming in SitemapDownloader.download() in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T031 [US1] Implement HTTP GET with streaming in SitemapDownloader.download() in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T031 [US1] Implement HTTP GET with streaming in SitemapDownloader.download() in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T031 [US1] Implement HTTP GET with streaming in SitemapDownloader.download() in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T033 [US1] Implement progress tracking logic (256KB/500ms threshold) in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T033 [US1] Implement progress tracking logic (256KB/500ms threshold) in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T033 [US1] Implement progress tracking logic (256KB/500ms threshold) in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T033 [US1] Implement progress tracking logic (256KB/500ms threshold) in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T034 [US1] Implement progress callback invocation in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T034 [US1] Implement progress callback invocation in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T034 [US1] Implement progress callback invocation in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T034 [US1] Implement progress callback invocation in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T035 [US1] Implement atomic file write (temp file + rename) in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T035 [US1] Implement atomic file write (temp file + rename) in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T035 [US1] Implement atomic file write (temp file + rename) in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T035 [US1] Implement atomic file write (temp file + rename) in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T036 [US1] Implement timeout configuration (connection and read) in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T036 [US1] Implement timeout configuration (connection and read) in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T037 [US1] Implement custom HTTP headers (User-Agent, Accept-Encoding) per FR-009 in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T037 [US1] Implement custom HTTP headers (User-Agent, Accept-Encoding) per FR-009 in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T036 [US1] Implement timeout configuration (connection and read) in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T036 [US1] Implement timeout configuration (connection and read) in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T038 [US1] Implement error handling and result creation in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T038 [US1] Implement error handling and result creation in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T038 [US1] Implement error handling and result creation in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T038 [US1] Implement error handling and result creation in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T039 [US1] Create CLI skeleton with typer in packages/sitemap-download/src/sitemap_download/cli.py
- [ ] T039 [US1] Create CLI skeleton with typer in packages/sitemap-download/src/sitemap_download/cli.py
- [ ] T039 [US1] Create CLI skeleton with typer in packages/sitemap-download/src/sitemap_download/cli.py
- [ ] T039 [US1] Create CLI skeleton with typer in packages/sitemap-download/src/sitemap_download/cli.py
- [ ] T040 [US1] Implement CLI options (url, output, connection-timeout, read-timeout) in packages/sitemap-download/src/sitemap_download/cli.py
- [ ] T040 [US1] Implement CLI options (url, output, connection-timeout, read-timeout) in packages/sitemap-download/src/sitemap_download/cli.py
- [ ] T040 [US1] Implement CLI options (url, output, connection-timeout, read-timeout) in packages/sitemap-download/src/sitemap_download/cli.py
- [ ] T040 [US1] Implement CLI options (url, output, connection-timeout, read-timeout) in packages/sitemap-download/src/sitemap_download/cli.py
- [ ] T041 [US1] Implement progress display formatter in packages/sitemap-download/src/sitemap_download/cli.py
- [ ] T041 [US1] Implement progress display formatter in packages/sitemap-download/src/sitemap_download/cli.py
- [ ] T041 [US1] Implement progress display formatter in packages/sitemap-download/src/sitemap_download/cli.py
- [ ] T041 [US1] Implement progress display formatter in packages/sitemap-download/src/sitemap_download/cli.py
- [ ] T037 [US1] Integrate downloader with CLI in packages/sitemap-download/src/sitemap_download/cli.py
- [ ] T037 [US1] Integrate downloader with CLI in packages/sitemap-download/src/sitemap_download/cli.py
- [ ] T037 [US1] Integrate downloader with CLI in packages/sitemap-download/src/sitemap_download/cli.py
- [ ] T037 [US1] Integrate downloader with CLI in packages/sitemap-download/src/sitemap_download/cli.py
- [ ] T038 [US1] Export typer app in packages/sitemap-download/src/sitemap_download/__init__.py
- [ ] T038 [US1] Export typer app in packages/sitemap-download/src/sitemap_download/__init__.py
- [ ] T038 [US1] Export typer app in packages/sitemap-download/src/sitemap_download/__init__.py
- [ ] T038 [US1] Export typer app in packages/sitemap-download/src/sitemap_download/__init__.py
- [ ] T039 [US1] Register sitemap-download command in main.py at repository root
- [ ] T039 [US1] Register sitemap-download command in main.py at repository root
- [ ] T039 [US1] Register sitemap-download command in main.py at repository root
- [ ] T039 [US1] Register sitemap-download command in main.py at repository root
- [ ] T040 [US1] Add structured logging for download operations in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T040 [US1] Add structured logging for download operations in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T040 [US1] Add structured logging for download operations in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T040 [US1] Add structured logging for download operations in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T041 [US1] Verify all US1 tests pass
- [ ] T041 [US1] Verify all US1 tests pass
- [ ] T041 [US1] Verify all US1 tests pass
- [ ] T041 [US1] Verify all US1 tests pass

**Checkpoint**: At this point, User Story 1 should be fully functional - users can download sitemap with progress indication

---

## Phase 4: User Story 2 - Update Existing Sitemap (Priority: P2)

**Goal**: Enable smart incremental updates by checking remote modification dates and skipping unchanged downloads

**Independent Test**: Create local sitemap, run download without force flag, verify skip logic when remote unchanged and download when remote is newer

### Tests for User Story 2 (TDD Required)

- [ ] T049 [P] [US2] Write unit test test_check_remote_info_success in packages/sitemap-download/tests/unit/test_downloader.py
- [ ] T050 [P] [US2] Write unit test test_check_remote_info_timeout in packages/sitemap-download/tests/unit/test_downloader.py
- [ ] T051 [P] [US2] Write unit test test_should_download_force_true in packages/sitemap-download/tests/unit/test_downloader.py
- [ ] T052 [P] [US2] Write unit test test_should_download_file_missing in packages/sitemap-download/tests/unit/test_downloader.py
- [ ] T053 [P] [US2] Write unit test test_should_download_remote_newer in packages/sitemap-download/tests/unit/test_downloader.py
- [ ] T054 [P] [US2] Write unit test test_should_download_up_to_date in packages/sitemap-download/tests/unit/test_downloader.py
- [ ] T055 [P] [US2] Write integration test test_cli_skip_up_to_date in packages/sitemap-download/tests/integration/test_cli.py
- [ ] T056 [P] [US2] Write integration test test_cli_force_download in packages/sitemap-download/tests/integration/test_cli.py

### Implementation for User Story 2

- [ ] T057 [US2] Implement check_remote_info() method with HTTP HEAD request in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T058 [US2] Implement header parsing (Last-Modified, Content-Length, ETag) in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T059 [US2] Implement should_download() decision logic in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T060 [US2] Implement local file modification date checking in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T061 [US2] Integrate modification check into download() workflow in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T062 [US2] Add --force CLI flag in packages/sitemap-download/src/sitemap_download/cli.py
- [ ] T063 [US2] Implement skip notification display in CLI in packages/sitemap-download/src/sitemap_download/cli.py
- [ ] T064 [US2] Add structured logging for skip/update decisions in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T065 [US2] Verify all US2 tests pass

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - download with smart incremental updates

---

## Phase 5: User Story 3 - Validate Downloaded Sitemap (Priority: P3)

**Goal**: Ensure downloaded sitemaps are well-formed XML with expected content before using them in the pipeline

**Independent Test**: Attempt to download and validate sitemaps with various states (valid, malformed, empty) and verify appropriate validation responses

### Tests for User Story 3 (TDD Required)

- [ ] T066 [P] [US3] Create test fixture malformed_sitemap.xml in packages/sitemap-download/tests/fixtures/
- [ ] T067 [P] [US3] Create test fixture empty_sitemap.xml in packages/sitemap-download/tests/fixtures/
- [ ] T068 [P] [US3] Write unit test test_validate_valid_urlset in packages/sitemap-download/tests/unit/test_validator.py
- [ ] T069 [P] [US3] Write unit test test_validate_valid_sitemapindex in packages/sitemap-download/tests/unit/test_validator.py
- [ ] T070 [P] [US3] Write unit test test_validate_empty_file in packages/sitemap-download/tests/unit/test_validator.py
- [ ] T071 [P] [US3] Write unit test test_validate_malformed_xml in packages/sitemap-download/tests/unit/test_validator.py
- [ ] T072 [P] [US3] Write unit test test_validate_missing_namespace in packages/sitemap-download/tests/unit/test_validator.py
- [ ] T073 [P] [US3] Write unit test test_validate_invalid_root_element in packages/sitemap-download/tests/unit/test_validator.py
- [ ] T074 [P] [US3] Write unit test test_validate_no_urls in packages/sitemap-download/tests/unit/test_validator.py
- [ ] T075 [P] [US3] Write unit test test_validate_url_missing_loc in packages/sitemap-download/tests/unit/test_validator.py
- [ ] T076 [P] [US3] Write unit test test_validate_file_not_found in packages/sitemap-download/tests/unit/test_validator.py
- [ ] T077 [P] [US3] Write integration test test_cli_validation_success in packages/sitemap-download/tests/integration/test_cli.py
- [ ] T078 [P] [US3] Write integration test test_cli_validation_failure in packages/sitemap-download/tests/integration/test_cli.py

### Implementation for User Story 3

- [ ] T079 [US3] Create SitemapValidator class in packages/sitemap-download/src/sitemap_download/validator.py
- [ ] T080 [US3] Create SitemapContentHandler SAX handler class in packages/sitemap-download/src/sitemap_download/validator.py
- [ ] T081 [US3] Implement SAX handler startElement() for URL counting in packages/sitemap-download/src/sitemap_download/validator.py
- [ ] T082 [US3] Implement SAX handler endElement() with validation checks in packages/sitemap-download/src/sitemap_download/validator.py
- [ ] T083 [US3] Implement SitemapValidator.validate() with streaming SAX parser in packages/sitemap-download/src/sitemap_download/validator.py
- [ ] T084 [US3] Implement file existence and size validation in packages/sitemap-download/src/sitemap_download/validator.py
- [ ] T085 [US3] Implement XML parse error handling in packages/sitemap-download/src/sitemap_download/validator.py
- [ ] T086 [US3] Implement root element and namespace validation in packages/sitemap-download/src/sitemap_download/validator.py
- [ ] T087 [US3] Implement URL count and content validation in packages/sitemap-download/src/sitemap_download/validator.py
- [ ] T088 [US3] Integrate validator with downloader (validate after download) in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T089 [US3] Implement validation failure rollback (restore old file) in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T090 [US3] Add validation result display in CLI in packages/sitemap-download/src/sitemap_download/cli.py
- [ ] T091 [US3] Add structured logging for validation operations in packages/sitemap-download/src/sitemap_download/validator.py
- [ ] T092 [US3] Verify all US3 tests pass

**Checkpoint**: All user stories should now be independently functional - download, smart updates, and validation working together

---

## Phase 6: Retry Logic & Error Handling

**Purpose**: Robust error handling for production use across all user stories

- [ ] T093 [P] Write unit test test_download_retry_transient_error in packages/sitemap-download/tests/unit/test_downloader.py
- [ ] T094 [P] Write unit test test_download_max_retries_exceeded in packages/sitemap-download/tests/unit/test_downloader.py
- [ ] T095 [P] Write unit test test_download_non_retryable_error in packages/sitemap-download/tests/unit/test_downloader.py
- [ ] T096 [P] Write unit test test_download_preserves_existing_file_on_failure in packages/sitemap-download/tests/unit/test_downloader.py
- [ ] T097 Implement retry loop with exponential backoff in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T098 Implement calculate_retry_delay() with jitter in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T099 Implement retry decision logic (5xx, timeouts, connection errors) in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T100 Implement non-retryable error handling (4xx errors) in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T101 Add --max-retries CLI option in packages/sitemap-download/src/sitemap_download/cli.py
- [ ] T102 Implement retry logging with attempt count in packages/sitemap-download/src/sitemap_download/downloader.py
- [ ] T103 Add error troubleshooting messages in CLI output in packages/sitemap-download/src/sitemap_download/cli.py
- [ ] T104 Verify retry tests pass

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T105 [P] Add --quiet flag for minimal output in packages/sitemap-download/src/sitemap_download/cli.py
- [ ] T106 [P] Implement quiet mode output formatting in packages/sitemap-download/src/sitemap_download/cli.py
- [ ] T107 [P] Add exit code handling (0=success, 1=download fail, 2=validation fail, 3=config error) in packages/sitemap-download/src/sitemap_download/cli.py
- [ ] T108 [P] Write performance test test_download_large_file_memory_usage in packages/sitemap-download/tests/integration/test_performance.py
- [ ] T109 [P] Write performance test test_validate_large_file_memory_usage in packages/sitemap-download/tests/integration/test_performance.py
- [ ] T110 [P] Add docstrings to all public classes and methods in packages/sitemap-download/src/sitemap_download/
- [ ] T111 [P] Update package README.md with usage examples and API documentation
- [ ] T112 [P] Update project root README.md with sitemap-download feature description
- [ ] T113 [P] Add entry to CHANGELOG.md for v0.1.0 (Added: sitemap download with progress, validation, incremental updates)
- [ ] T114 [P] Generate release notes from conventional commits using .github/RELEASE_NOTES_TEMPLATE.md
- [ ] T115 Run complete test suite with coverage (pytest --cov=src --cov-report=term-missing)
- [ ] T116 Validate quickstart.md examples work end-to-end
- [ ] T117 Final commit with format: docs(sitemap-download): update README and create release notes for v0.1.0

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3, 4, 5)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P2): Can start after Foundational - Extends US1 but independently testable
  - User Story 3 (P3): Can start after Foundational - Integrates with US1 but independently testable
- **Retry Logic (Phase 6)**: Can start after US1 complete (extends downloader)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Foundation only - Can start immediately after Phase 2
- **User Story 2 (P2)**: Foundation only - Extends downloader but doesn't break US1 functionality
- **User Story 3 (P3)**: Foundation only - Adds validation but US1/US2 work without it

**Key Point**: All user stories are designed to be independently testable. US2 and US3 enhance US1 but don't break it.

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD)
- Models before services (all in Phase 2)
- Core implementation before CLI integration
- CLI integration before testing complete story
- Story complete and verified before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**: T003, T004, T005 can run in parallel  
**Phase 2 (Foundational)**: T007-T011 (all model dataclasses) can run in parallel  

**Phase 3 (US1)**: 
- Tests: T014-T021 can all run in parallel (different test files)
- Models: Already in Phase 2

**Phase 4 (US2)**:
- Tests: T037-T044 can all run in parallel

**Phase 5 (US3)**:
- Tests: T054-T066 can all run in parallel

**Phase 6 (Retry)**:
- Tests: T081-T084 can run in parallel

**Phase 7 (Polish)**:
- T093-T094, T096-T099, T100-T102 can all run in parallel

**Multi-Developer Strategy**: Once Phase 2 completes, three developers could work on US1, US2, and US3 simultaneously.

---

## Parallel Example: User Story 1

```bash
# Write all tests for User Story 1 together (TDD - tests first):
Task: "[US1] Create test fixture valid_sitemap.xml"
Task: "[US1] Create test fixture large_sitemap.xml"
Task: "[US1] Write unit test test_downloader_init"
Task: "[US1] Write unit test test_download_success"
Task: "[US1] Write unit test test_download_with_progress_callback"
Task: "[US1] Write unit test test_download_network_error"
Task: "[US1] Write unit test test_download_timeout"
Task: "[US1] Write integration test test_cli_basic_download"

# Verify all tests FAIL (red phase)

# Then implement US1 features sequentially to make tests pass (green phase)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (~5 tasks, <1 hour)
2. Complete Phase 2: Foundational (~7 tasks, 1-2 hours)
3. Complete Phase 3: User Story 1 (~24 tasks, 4-6 hours)
4. **STOP and VALIDATE**: Test User Story 1 independently
   - `python main.py sitemap-download`
   - Verify download works, progress shown, file saved
5. Deploy/demo if ready

**MVP Deliverable**: Basic sitemap download with progress indication (~6-9 hours total)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (2-3 hours)
2. Add User Story 1 → Test independently → Commit (4-6 hours) **← MVP!**
3. Add User Story 2 → Test independently → Commit (3-4 hours) **← Smart updates**
4. Add User Story 3 → Test independently → Commit (3-4 hours) **← Validation**
5. Add Retry Logic → Test thoroughly → Commit (2-3 hours) **← Production ready**
6. Add Polish → Complete documentation → Release (2-3 hours) **← v0.1.0**

**Total Estimated Time**: 16-23 hours for complete feature with all user stories

Each story adds value without breaking previous stories. Can ship after any phase.

### Parallel Team Strategy

With multiple developers and Phase 2 complete:

**Developer A**: User Story 1 (Phase 3) - Core download  
**Developer B**: User Story 2 (Phase 4) - Smart updates  
**Developer C**: User Story 3 (Phase 5) - Validation  

Then converge on Phase 6 (Retry) and Phase 7 (Polish) together.

**Parallel Completion Time**: ~8-12 hours to complete all features (vs 16-23 hours serial)

---

## Notes

- **TDD Required**: Constitution Principle III mandates tests before implementation
- **[P] tasks** = different files, no dependencies, can run in parallel
- **[Story] label** maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail (red) before implementing (green)
- Commit after each logical group of tasks
- Stop at any checkpoint to validate story independently
- Constitution compliance: Modular architecture, data pipeline integrity, observability, package management (uv), main entry point integration
- Exit codes enable script automation (0=success, 1=download fail, 2=validation fail, 3=config error)
- Memory target <10MB enforced through streaming (8KB chunks) and SAX validation
- Progress updates every 256KB or 500ms for responsive UX
- 3 retries with exponential backoff (1s, 2s, 4s) + 25% jitter for transient failures
