#!/usr/bin/env python3
"""
Robust task renumbering script for tasks.md

This script applies the analysis recommendations to tasks.md:
1. Fix duplicate T016 -> T017
2. Add FR-009 implementation task (custom HTTP headers)
3. Add disk space check tests (2 tasks)
4. Add disk space check implementation (1 task)
5. Renumber all subsequent tasks accordingly

Strategy:
- Parse the file into phases
- Insert new tasks at appropriate locations
- Renumber all tasks sequentially within each phase
- Update cross-references (like parallel opportunities)
"""

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Task:
    """Represents a task line in tasks.md"""

    original_line: str
    task_id: str
    line_number: int
    is_test: bool
    phase: str
    user_story: str

    def with_new_id(self, new_id: str) -> str:
        """Return the line with a new task ID"""
        pattern = r"\bT\d{3}\b"
        return re.sub(pattern, new_id, self.original_line, count=1)


def parse_tasks(filepath: Path) -> tuple[list[str], list[Task]]:
    """Parse tasks.md and extract all task lines"""
    with open(filepath) as f:
        lines = f.readlines()

    tasks = []
    current_phase = ""

    for i, line in enumerate(lines, 1):
        # Track current phase
        if line.startswith("## Phase"):
            current_phase = line.strip()

        # Extract task lines
        match = re.match(r"^- \[ \] (T\d{3}) (\[P\] )?\[([^\]]+)\]", line)
        if match:
            task_id = match.group(1)
            is_test = match.group(2) is not None
            user_story = match.group(3)

            tasks.append(
                Task(
                    original_line=line,
                    task_id=task_id,
                    line_number=i,
                    is_test=is_test,
                    phase=current_phase,
                    user_story=user_story,
                )
            )

    return lines, tasks


def apply_fixes(lines: list[str], tasks: list[Task]) -> list[str]:
    """Apply all fixes from analysis recommendations"""

    # Build the new content
    new_lines = []

    for i, line in enumerate(lines, 1):
        # Fix 1: Clarify T003 wording
        if i == 33 and "T003" in line and "should be part of overall" in line:
            line = "- [ ] T003 [P] Verify typer and loguru exist in root pyproject.toml (httpx is package-specific only)\n"

        # Fix 2: Fix duplicate T016 (second occurrence on line 71)
        if i == 71 and line.startswith("- [ ] T016") and "test_download_success" in line:
            line = line.replace("T016", "T017_TEMP")  # Temp marker to avoid double-replacement

        # Fix 3: Renumber T017-T020 to T018-T021
        if re.match(r"^- \[ \] T(017|018|019|020) \[P\] \[US1\]", line):
            match = re.match(r"^- \[ \] T(\d{3})", line)
            if match:
                old_num = int(match.group(1))
                line = re.sub(r"^(- \[ \] )T\d{3}", rf"\1T{old_num + 1:03d}", line)

        new_lines.append(line)

        # Fix 4: Add disk space check tests after T020 (now T021)
        if i == 75 and "T020" in line and "integration test" in line and "US1" in line:
            new_lines.append(
                "- [ ] T022 [P] [US1] Write unit test test_check_disk_space_sufficient (optional) in packages/sitemap-download/tests/unit/test_downloader.py\n"
            )
            new_lines.append(
                "- [ ] T023 [P] [US1] Write unit test test_check_disk_space_insufficient (optional) in packages/sitemap-download/tests/unit/test_downloader.py\n"
            )

        # Fix 5: Add disk space check implementation after T022 (__init__)
        if i == 80 and "T022" in line and "__init__" in line:
            new_lines.append(
                "- [ ] DISK_CHECK [US1] Implement check_disk_space() pre-flight check (optional) in packages/sitemap-download/src/sitemap_download/downloader.py\n"
            )

        # Fix 6: Add FR-009 implementation after T027 (timeout config)
        if i == 85 and "T027" in line and "timeout configuration" in line:
            new_lines.append(
                "- [ ] FR009 [US1] Implement custom HTTP headers (User-Agent, Accept-Encoding) per FR-009 in packages/sitemap-download/src/sitemap_download/downloader.py\n"
            )

    # Fix 7: Update parallel opportunities reference
    result = []
    for line in new_lines:
        if "T013-T020" in line and "parallel" in line:
            line = line.replace("T013-T020", "T014-T021")
        # Convert temp marker back
        if "T017_TEMP" in line:
            line = line.replace("T017_TEMP", "T017")
        result.append(line)

    return result


def renumber_tasks(lines: list[str]) -> list[str]:
    """Renumber all tasks sequentially"""

    # Simple approach: renumber all tasks sequentially from T001
    result = []
    task_counter = 1

    for line in lines:
        # Only renumber actual task lines
        if re.match(r"^- \[ \] T\d{3}", line):
            # Replace the task ID with the next sequential number
            line = re.sub(r"^(- \[ \] )T\d{3}", rf"\1T{task_counter:03d}", line)
            task_counter += 1
        result.append(line)

    return result


def parse_tasks_from_lines(lines: list[str]) -> tuple[list[str], list[Task]]:
    """Parse tasks from a list of lines"""
    tasks = []
    current_phase = ""

    for i, line in enumerate(lines, 1):
        if line.startswith("## Phase"):
            current_phase = line.strip()

        match = re.match(r"^- \[ \] (T\d{3}) (\[P\] )?\[([^\]]+)\]", line)
        if match:
            task_id = match.group(1)
            is_test = match.group(2) is not None
            user_story = match.group(3)

            tasks.append(
                Task(
                    original_line=line,
                    task_id=task_id,
                    line_number=i,
                    is_test=is_test,
                    phase=current_phase,
                    user_story=user_story,
                )
            )

    return lines, tasks


def validate_result(lines: list[str]) -> bool:
    """Validate the final result has no duplicates and sequential IDs"""
    _, tasks = parse_tasks_from_lines(lines)

    task_nums = [int(t.task_id[1:]) for t in tasks]

    # Check for duplicates
    from collections import Counter

    counts = Counter(task_nums)
    duplicates = [t for t, c in counts.items() if c > 1]

    if duplicates:
        print(f"❌ Duplicates found: {duplicates}")
        return False

    # Check for sequential IDs
    unique_sorted = sorted(set(task_nums))
    expected = list(range(1, len(unique_sorted) + 1))

    if unique_sorted != expected:
        missing = set(expected) - set(unique_sorted)
        print(f"❌ Non-sequential: missing {missing}")
        return False

    print(f"✅ Validation passed: {len(unique_sorted)} tasks, T001-T{max(task_nums):03d}")
    return True


def main():
    """Main execution"""
    filepath = Path("/workspaces/uv-ayx-rag/specs/002-sitemap-download/tasks.md")

    print("📖 Reading tasks.md...")
    lines, tasks = parse_tasks(filepath)
    print(f"   Found {len(tasks)} tasks")

    print("\n🔧 Applying fixes...")
    lines = apply_fixes(lines, tasks)

    print("🔢 Renumbering tasks...")
    lines = renumber_tasks(lines)

    print("\n✓ Validating result...")
    if not validate_result(lines):
        print("❌ Validation failed! Not writing file.")
        return 1

    print("\n💾 Writing updated tasks.md...")
    with open(filepath, "w") as f:
        f.writelines(lines)

    print("✅ Complete! All analysis fixes applied.")
    return 0


if __name__ == "__main__":
    exit(main())
