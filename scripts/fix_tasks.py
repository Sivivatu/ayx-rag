#!/usr/bin/env python3
"""
Simple and robust task fixes for tasks.md

Applies analysis recommendations in order:
1. Fix T003 wording
2. Fix duplicate T016
3. Add 2 disk space check tests
4. Add 1 disk space check implementation
5. Add 1 FR-009 implementation
6. Renumber all tasks sequentially
7. Fix parallel opportunities reference
"""

import re
from pathlib import Path


def main():
    filepath = Path("/workspaces/uv-ayx-rag/specs/002-sitemap-download/tasks.md")

    print("📖 Reading tasks.md...")
    with open(filepath) as f:
        content = f.read()

    print("🔧 Applying fixes...")

    # Fix 1: Clarify T003 wording
    content = content.replace(
        "- [ ] T003 [P] Add httpx>=0.25.0 to root pyproject.toml if typer and loguru need to be added there",
        "- [ ] T003 [P] Verify typer and loguru exist in root pyproject.toml (httpx is package-specific only)",
    )

    # Fix 2: Fix duplicate T016 by finding the second one and renumbering from there
    # First occurrence at line ~70: test_downloader_init
    # Second occurrence at line ~71: test_download_success
    # Strategy: Replace the specific line
    content = content.replace(
        "- [ ] T016 [P] [US1] Write unit test test_download_success in packages/sitemap-download/tests/unit/test_downloader.py",
        "- [ ] T017 [P] [US1] Write unit test test_download_success in packages/sitemap-download/tests/unit/test_downloader.py",
    )

    # Now shift T017-T020 to T018-T021
    # Work backwards to avoid double-replacement
    content = content.replace(
        "- [ ] T020 [P] [US1] Write integration test test_cli_basic_download",
        "- [ ] T021 [P] [US1] Write integration test test_cli_basic_download",
    )
    content = content.replace(
        "- [ ] T019 [P] [US1] Write unit test test_download_timeout",
        "- [ ] T020 [P] [US1] Write unit test test_download_timeout",
    )
    content = content.replace(
        "- [ ] T018 [P] [US1] Write unit test test_download_network_error",
        "- [ ] T019 [P] [US1] Write unit test test_download_network_error",
    )
    content = content.replace(
        "- [ ] T017 [P] [US1] Write unit test test_download_with_progress_callback",
        "- [ ] T018 [P] [US1] Write unit test test_download_with_progress_callback",
    )

    # Fix 3: Add disk space check tests after T021 (was T020)
    insertion_point = "- [ ] T021 [P] [US1] Write integration test test_cli_basic_download in packages/sitemap-download/tests/integration/test_cli.py\n"
    new_tests = """- [ ] T021 [P] [US1] Write integration test test_cli_basic_download in packages/sitemap-download/tests/integration/test_cli.py
- [ ] T022 [P] [US1] Write unit test test_check_disk_space_sufficient (optional) in packages/sitemap-download/tests/unit/test_downloader.py
- [ ] T023 [P] [US1] Write unit test test_check_disk_space_insufficient (optional) in packages/sitemap-download/tests/unit/test_downloader.py
"""
    content = content.replace(insertion_point, new_tests)

    # Fix 4 & 5: Renumber Phase 3 implementation and add new tasks
    # Tests end at T023 (after adding 2 disk space tests)
    # Implementation starts at T024
    # Original impl was T021-T036 (16 tasks)
    # New impl is T024-T042 (19 tasks: +2 for insertions, +1 for starting at 024 not 021)
    # Mapping:
    # T021 (skeleton) -> T024
    # T022 (__init__) -> T025
    # [INSERT T026 disk check]
    # T023 (HTTP GET) -> T027
    # T024 (progress tracking) -> T028
    # T025 (progress callback) -> T029
    # T026 (atomic file) -> T030
    # T027 (timeout) -> T031
    # [INSERT T032 FR-009]
    # T028 (error handling) -> T033
    # T029 (CLI skeleton) -> T034
    # T030 (CLI options) -> T035
    # T031 (progress display) -> T036
    # T032 (integrate) -> T037
    # T033 (export) -> T038
    # T034 (register) -> T039
    # T035 (logging) -> T040
    # T036 (verify) -> T041
    # Plus checkpoint text update

    impl_replacements = [
        ("T036", "T041"),  # Verify all US1 tests pass
        ("T035", "T040"),  # Add structured logging
        ("T034", "T039"),  # Register sitemap-download command
        ("T033", "T038"),  # Export typer app
        ("T032", "T037"),  # Integrate downloader with CLI
        ("T031", "T036"),  # Implement progress display formatter
        ("T030", "T035"),  # Implement CLI options
        ("T029", "T034"),  # Create CLI skeleton
        ("T028", "T033"),  # Implement error handling
        # INSERT FR-009 here as T032
        ("T027", "T031"),  # Implement timeout configuration
        ("T026", "T030"),  # Implement atomic file write
        ("T025", "T029"),  # Implement progress callback
        ("T024", "T028"),  # Implement progress tracking
        ("T023", "T027"),  # Implement HTTP GET with streaming
        # INSERT disk space check here as T026
        ("T022", "T025"),  # Implement __init__
        ("T021", "T024"),  # Create SitemapDownloader class skeleton
    ]

    # First pass: Replace in implementation section only (after "### Implementation for User Story 1")
    lines = content.split("\n")
    result_lines = []
    in_us1_impl = False
    disk_check_added = False
    fr009_added = False

    for line in lines:
        if "### Implementation for User Story 1" in line:
            in_us1_impl = True
            result_lines.append(line)
            continue

        if in_us1_impl and line.startswith("## Phase 4"):
            in_us1_impl = False

        if in_us1_impl and line.startswith("- [ ] T"):
            # Apply replacements
            for old, new in impl_replacements:
                if line.startswith(f"- [ ] {old} [US1]"):
                    line = line.replace(old, new, 1)
                    break

            result_lines.append(line)

            # Add disk space check after T025 (__init__)
            if "T025 [US1]" in line and "__init__" in line and not disk_check_added:
                result_lines.append(
                    "- [ ] T026 [US1] Implement check_disk_space() pre-flight check (optional) in packages/sitemap-download/src/sitemap_download/downloader.py"
                )
                disk_check_added = True

            # Add FR-009 after T031 (timeout)
            elif "T031 [US1]" in line and "timeout" in line and not fr009_added:
                result_lines.append(
                    "- [ ] T032 [US1] Implement custom HTTP headers (User-Agent, Accept-Encoding) per FR-009 in packages/sitemap-download/src/sitemap_download/downloader.py"
                )
                fr009_added = True

        # Also handle checkpoint update
        if in_us1_impl and "T036 [US1] Verify all US1 tests pass" in line:
            line = line.replace("T036", "T041")

        if in_us1_impl and "**Checkpoint**: At this point, User Story 1" in line:
            # This line comes after the verify task, so it's not in a task line
            pass  # Keep as is

        result_lines.append(line)

    content = "\n".join(result_lines)

    # Fix 6: Renumber Phase 4 onwards using temporary placeholders to avoid conflicts
    # Original Phase 3 ended at T036, Phase 4 started at T037
    # After fixes, Phase 3 ends at T042, so Phase 4 starts at T043 (shift of +6)

    # Step 1: Replace with temporary placeholders (TXXX format)
    lines = content.split("\n")
    temp_lines = []
    for line in lines:
        if line.startswith("- [ ] T") and "[US1]" not in line:  # Skip Phase 3 US1 tasks
            match = re.match(r"^- \[ \] T(\d{3})", line)
            if match:
                num = int(match.group(1))
                if num >= 37:  # Phase 4 and beyond
                    new_num = num + 6
                    line = re.sub(r"^(- \[ \] )T\d{3}", rf"\1X{new_num:03d}", line)
        temp_lines.append(line)

    # Step 2: Convert placeholders back to T format
    final_lines = []
    for line in temp_lines:
        if line.startswith("- [ ] X"):
            line = line.replace("- [ ] X", "- [ ] T", 1)
        final_lines.append(line)

    content = "\n".join(final_lines)

    # Fix 7: Update parallel opportunities reference
    content = content.replace(
        "T013-T020 can all run in parallel", "T014-T021 can all run in parallel"
    )

    print("✅ Fixes applied!")
    print("\n💾 Writing updated tasks.md...")

    with open(filepath, "w") as f:
        f.write(content)

    print("✅ Complete!")

    # Validation
    print("\n🔍 Validating...")
    task_lines = [line for line in content.split("\n") if re.match(r"^- \[ \] T\d{3}", line)]
    task_nums = [int(re.search(r"T(\d{3})", line).group(1)) for line in task_lines]

    from collections import Counter

    counts = Counter(task_nums)
    duplicates = [t for t, c in counts.items() if c > 1]

    if duplicates:
        print(f"❌ Duplicates found: {duplicates}")
        return 1

    unique_sorted = sorted(set(task_nums))
    expected = list(range(1, len(unique_sorted) + 1))

    if unique_sorted != expected:
        missing = set(expected) - set(unique_sorted)
        extra = set(unique_sorted) - set(expected)
        if missing:
            print(f"❌ Missing: {sorted(missing)}")
        if extra:
            print(f"❌ Extra: {sorted(extra)}")
        return 1

    print(f"✅ Validation passed: {len(unique_sorted)} tasks, T001-T{max(task_nums):03d}")
    return 0


if __name__ == "__main__":
    exit(main())
