# Release Notes - v0.3.0 (Page Downloader)

## Overview

Version 0.3.0 introduces the Page Downloader feature, enabling single and batch HTML page retrieval from Alteryx Help documentation with structured logging, validation, and summary statistics.

## Added
- feat(page-downloader): CLI implementation (single URL + batch)
- feat(page-downloader): URLList parsing, DownloadSession, ProgressTracker
- feat(main): register page-downloader CLI command

## Changed
- fix(page-downloader): forward url_or_file; add quiet/delay options in main wrapper
- fix(page-downloader): preserve test log handlers and emit byte-count log

## Fixed
- fix(page-downloader): correct progress tracking stats and batch fixture URL count
- fix(page-downloader): align mixed batch expected count
- fix(page-downloader): add --no-verify-ssl option for SSL certificate issues

## Tests
- test(page-downloader): comprehensive downloader, CLI, batch, logging, E2E tests
- test(page-downloader): restore integration tests with unique module names
- test(page-downloader): remove integration package collisions

## Documentation
- docs(page-downloader): tasks updated (US2 complete)
- README updated with feature overview and examples
- Added package README for page-downloader

## Version Metadata
- Date: 2025-11-07
- Previous Version: 0.2.0
- Next Planned: Incremental updates (US3), retry/backoff (US4)

## Exit Codes
- 0: Success
- 1: Download failure
- 2: Validation/Skipped
- 3: Configuration error

## Future Work
- Incremental page re-validation using Last-Modified (US3)
- Retry with exponential backoff + jitter (US4)
- Robots.txt enforcement (FR-024)

## Full Commit List (Scope: page-downloader)
```
bb74936 fix(page-downloader): preserve test log handlers and emit byte-count log; restore logging tests
d3ff903 test(page-downloader): restore integration tests with unique module names
f66d924 test(page-downloader): remove integration package collisions; delete __init__.py and legacy test modules
aca9ff7 test(page-downloader): rename integration tests to unique module names to avoid import collisions
1bc469c fix(page-downloader): forward url_or_file and add quiet/delay options in main wrapper to match CLI signature
cc8a9ae docs(page-downloader): mark US2 (T022???T031) completed in tasks.md
52c929d test(page-downloader): align mixed batch expected count to fixture
3cf8d25 fix(page-downloader): correct progress tracking stats and batch fixture URL count
44360dc feat(page-downloader): add URLList parsing, DownloadSession, and rich-based ProgressTracker
5c83f64 docs(page-downloader): add session memory for Phase 3 implementation
6176bf8 docs(page-downloader): update tasks.md after implementing CLI and register with main application
7470285 debug(page-downloader): add SSL verification debugging logs
8a8bc3f fix(page-downloader): add --no-verify-ssl option for SSL certificate issues
2395b9a test(page-downloader): add E2E and logging verification tests (T020, T021)
a394057 feat(main): register page-downloader CLI command (T019)
acc51a9 feat(page-downloader): implement CLI with typer (T018)
64cad80 test(page-downloader): add CLI integration tests (T017)
c1aa71b fix(page-downloader): fix failing downloader tests (T015-T016)
338ed20 test(page-downloader): add comprehensive downloader tests (T015)
6888be0 feat(page-downloader): implement HTML validation (T013-T014)
bccd9f3 feat(page-downloader): implement path sanitization (T011-T012)
241a5b5 refactor(page-downloader): generate large.html dynamically in tests
064bd2e test(page-downloader): create test fixtures and conftest (T008-T010)
def52e2 feat(page-downloader): complete Phase 2 foundational components (T005-T007)
92413e2 chore(page-downloader): mark Phase 1 tasks complete in tasks.md
1426db5 feat(page-downloader): complete Phase 1 setup (T001-T004)
3b33b01 docs(page-downloader): expand tasks.md with granular subtasks (T048-T068)
ae0f64d docs(page-downloader): generate implementation task breakdown via /speckit.tasks
2fb19ce docs(page-downloader): resolve remaining 4 edge cases from clarification session
a1b149d docs(page-downloader): add 5 clarifications to spec
0514059 docs(page-downloader): create implementation plan and Phase 0/1 artifacts
fb8b660 docs(page-downloader): create specification with clarifications for v0.1.0
```

## Acknowledgments
Thanks to the existing sitemap feature foundations enabling rapid page retrieval implementation.
