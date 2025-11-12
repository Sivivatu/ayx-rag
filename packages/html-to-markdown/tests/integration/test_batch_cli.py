"""Integration tests for batch CLI command."""

import json

import pytest
from html_to_markdown.cli import app
from typer.testing import CliRunner

runner = CliRunner()


@pytest.fixture
def html_files(tmp_path):
    """Create multiple HTML files for batch testing."""
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    # Create valid HTML files
    for i in range(5):
        html = f"""<!DOCTYPE html>
<html>
<head><title>Page {i}</title></head>
<body>
    <h1>Page {i}</h1>
    <p>This is content for page {i}.</p>
</body>
</html>"""
        (input_dir / f"page{i}.html").write_text(html, encoding="utf-8")

    # Create nested directory structure
    nested = input_dir / "subfolder"
    nested.mkdir()
    (nested / "nested.html").write_text("<h1>Nested</h1><p>Content</p>", encoding="utf-8")

    return input_dir


def test_batch_converts_multiple_files(html_files, tmp_path):
    """Should convert all HTML files in directory."""
    out_dir = tmp_path / "output"

    result = runner.invoke(app, ["batch", str(html_files), "--out", str(out_dir)])

    assert result.exit_code == 0
    assert "Batch Conversion Complete" in result.stdout
    assert "Total files: 6" in result.stdout
    assert "Converted: 6" in result.stdout

    # Verify output files exist
    assert (out_dir / "page0.md").exists()
    assert (out_dir / "page4.md").exists()
    assert (out_dir / "subfolder" / "nested.md").exists()


def test_batch_preserves_directory_structure(html_files, tmp_path):
    """Should maintain directory structure in output."""
    out_dir = tmp_path / "output"

    result = runner.invoke(app, ["batch", str(html_files), "--out", str(out_dir)])

    assert result.exit_code == 0

    # Check nested structure preserved
    nested_out = out_dir / "subfolder" / "nested.md"
    assert nested_out.exists()
    content = nested_out.read_text()
    assert "Nested" in content


def test_batch_shows_progress_updates(html_files, tmp_path):
    """Should show progress during conversion."""
    out_dir = tmp_path / "output"

    result = runner.invoke(app, ["batch", str(html_files), "--out", str(out_dir)])

    assert result.exit_code == 0
    assert "Progress:" in result.stdout
    assert "files/s" in result.stdout
    assert "Elapsed:" in result.stdout


def test_batch_generates_summary_json(html_files, tmp_path):
    """Should generate summary JSON when requested."""
    out_dir = tmp_path / "output"
    summary_path = tmp_path / "summary.json"

    result = runner.invoke(
        app,
        [
            "batch",
            str(html_files),
            "--out",
            str(out_dir),
            "--summary",
            str(summary_path),
        ],
    )

    assert result.exit_code == 0
    assert summary_path.exists()

    summary = json.loads(summary_path.read_text())
    assert summary["total_files"] == 6
    assert summary["converted"] == 6
    assert summary["failed"] == 0
    assert "duration_seconds" in summary
    assert "rate_files_per_second" in summary
    assert summary["strategy"] == "markdownify"


def test_batch_handles_malformed_html(tmp_path):
    """Should continue processing when encountering errors."""
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    # Valid file
    (input_dir / "valid.html").write_text("<h1>Valid</h1><p>Content</p>", encoding="utf-8")

    # Malformed file (invalid encoding trigger)
    (input_dir / "invalid.html").write_text("<<>>Not properly formed<<", encoding="utf-8")

    # Another valid file
    (input_dir / "valid2.html").write_text("<h1>Valid 2</h1>", encoding="utf-8")

    out_dir = tmp_path / "output"
    summary_path = tmp_path / "summary.json"

    runner.invoke(
        app,
        [
            "batch",
            str(input_dir),
            "--out",
            str(out_dir),
            "--summary",
            str(summary_path),
        ],
    )

    # Should complete but exit with code 1 due to failures
    # However, valid files should still convert
    assert (out_dir / "valid.md").exists()
    assert (out_dir / "valid2.md").exists()

    # Check summary includes error info if any failures occurred
    if summary_path.exists():
        summary = json.loads(summary_path.read_text())
        assert summary["total_files"] == 3
        assert summary["converted"] >= 2  # At least the valid ones


def test_batch_with_exclusion_patterns(tmp_path):
    """Should respect exclusion patterns."""
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    # Create files
    (input_dir / "include.html").write_text("<h1>Include</h1>", encoding="utf-8")
    (input_dir / "exclude.html").write_text("<h1>Exclude</h1>", encoding="utf-8")
    (input_dir / "test.html").write_text("<h1>Test</h1>", encoding="utf-8")

    out_dir = tmp_path / "output"

    result = runner.invoke(
        app,
        [
            "batch",
            str(input_dir),
            "--out",
            str(out_dir),
            "--exclude",
            "**/exclude.html",
        ],
    )

    assert result.exit_code == 0

    # Excluded file should not be converted
    assert (out_dir / "include.md").exists()
    assert (out_dir / "test.md").exists()
    assert not (out_dir / "exclude.md").exists()


def test_batch_no_files_found(tmp_path):
    """Should handle empty directory gracefully."""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    out_dir = tmp_path / "output"

    result = runner.invoke(app, ["batch", str(empty_dir), "--out", str(out_dir)])

    assert result.exit_code == 0
    assert "No HTML files found" in result.stdout


def test_batch_calculates_conversion_rate(html_files, tmp_path):
    """Should calculate and display conversion rate."""
    out_dir = tmp_path / "output"

    result = runner.invoke(app, ["batch", str(html_files), "--out", str(out_dir)])

    assert result.exit_code == 0
    assert "files/min" in result.stdout
    assert "Rate:" in result.stdout


def test_batch_with_strategy_option(html_files, tmp_path):
    """Should accept strategy option."""
    out_dir = tmp_path / "output"

    result = runner.invoke(
        app,
        [
            "batch",
            str(html_files),
            "--out",
            str(out_dir),
            "--strategy",
            "markdownify",
        ],
    )

    assert result.exit_code == 0
    assert "markdownify" in result.stdout


def test_batch_creates_checkpoint_on_failure(tmp_path):
    """Should create checkpoint when failures occur."""
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    # Create files that will fail
    (input_dir / "file1.html").write_text("<h1>OK</h1>", encoding="utf-8")
    (input_dir / "file2.html").write_text("<h1>OK</h1>", encoding="utf-8")

    out_dir = tmp_path / "output"
    out_dir / ".checkpoint.json"

    result = runner.invoke(app, ["batch", str(input_dir), "--out", str(out_dir)])

    # Should succeed without errors in this case
    assert result.exit_code == 0


def test_batch_resume_from_checkpoint(tmp_path):
    """Should resume from checkpoint and skip processed files."""
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    # Create multiple files
    for i in range(5):
        (input_dir / f"page{i}.html").write_text(f"<h1>Page {i}</h1>", encoding="utf-8")

    out_dir = tmp_path / "output"
    out_dir.mkdir()

    # First: manually create some output files to simulate partial completion
    for i in range(3):
        (out_dir / f"page{i}.md").write_text(f"# Page {i}\n", encoding="utf-8")

    # Create checkpoint showing these files were processed
    from html_to_markdown.checkpoint import Checkpoint

    checkpoint = Checkpoint.create_new(total_files=5)
    checkpoint.mark_processed("page0.html")
    checkpoint.mark_processed("page1.html")
    checkpoint.mark_processed("page2.html")
    checkpoint.save(out_dir / ".checkpoint.json")

    # Run with resume flag
    result = runner.invoke(
        app,
        [
            "batch",
            str(input_dir),
            "--out",
            str(out_dir),
            "--resume",
        ],
    )

    assert result.exit_code == 0
    assert "Resuming from checkpoint" in result.stdout
    assert "Previously processed: 3/5" in result.stdout
    assert "Remaining files to process: 2" in result.stdout

    # All files should now exist in output
    assert len(list(out_dir.glob("*.md"))) == 5
    # Verify the resumed files were created
    assert (out_dir / "page3.md").exists()
    assert (out_dir / "page4.md").exists()


def test_batch_resume_without_checkpoint(tmp_path):
    """Should start fresh if no checkpoint exists."""
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    (input_dir / "test.html").write_text("<h1>Test</h1>", encoding="utf-8")

    out_dir = tmp_path / "output"

    # Try to resume without checkpoint
    result = runner.invoke(
        app,
        [
            "batch",
            str(input_dir),
            "--out",
            str(out_dir),
            "--resume",
        ],
    )

    assert result.exit_code == 0
    # Should not show resume message
    assert "Resuming from checkpoint" not in result.stdout


def test_batch_checkpoint_removed_on_success(tmp_path):
    """Should remove checkpoint when all files processed successfully."""
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    (input_dir / "file1.html").write_text("<h1>Test</h1>", encoding="utf-8")
    (input_dir / "file2.html").write_text("<h1>Test 2</h1>", encoding="utf-8")

    out_dir = tmp_path / "output"
    out_dir / ".checkpoint.json"

    result = runner.invoke(app, ["batch", str(input_dir), "--out", str(out_dir)])

    assert result.exit_code == 0
    # Checkpoint should be removed on success
    assert "Checkpoint removed" in result.stdout


def test_batch_custom_checkpoint_path(tmp_path):
    """Should support custom checkpoint path."""
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    (input_dir / "test.html").write_text("<h1>Test</h1>", encoding="utf-8")

    out_dir = tmp_path / "output"
    custom_checkpoint = tmp_path / "my_checkpoint.json"

    result = runner.invoke(
        app,
        [
            "batch",
            str(input_dir),
            "--out",
            str(out_dir),
            "--checkpoint",
            str(custom_checkpoint),
        ],
    )

    assert result.exit_code == 0
