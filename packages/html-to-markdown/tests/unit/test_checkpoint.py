"""Unit tests for checkpoint module."""
from pathlib import Path

import pytest
from html_to_markdown.checkpoint import Checkpoint, CheckpointEntry


class TestCheckpointEntry:
    """Test CheckpointEntry dataclass."""

    def test_create_success_entry(self):
        """Should create successful entry."""
        entry = CheckpointEntry(
            file_path="test.html",
            status="success",
            timestamp="2025-11-12T10:00:00",
        )

        assert entry.file_path == "test.html"
        assert entry.status == "success"
        assert entry.error is None

    def test_create_failed_entry(self):
        """Should create failed entry with error."""
        entry = CheckpointEntry(
            file_path="test.html",
            status="failed",
            timestamp="2025-11-12T10:00:00",
            error="Conversion failed",
        )

        assert entry.status == "failed"
        assert entry.error == "Conversion failed"


class TestCheckpoint:
    """Test Checkpoint class."""

    def test_create_new_checkpoint(self):
        """Should create new checkpoint with defaults."""
        checkpoint = Checkpoint.create_new(total_files=10)

        assert checkpoint.total_files == 10
        assert checkpoint.processed_count == 0
        assert len(checkpoint.processed_files) == 0
        assert len(checkpoint.failed_files) == 0
        assert checkpoint.started_at is not None

    def test_mark_processed_success(self):
        """Should mark file as successfully processed."""
        checkpoint = Checkpoint.create_new(total_files=10)

        checkpoint.mark_processed("file1.html", success=True)

        assert checkpoint.processed_count == 1
        assert "file1.html" in checkpoint.processed_files
        assert len(checkpoint.failed_files) == 0

    def test_mark_processed_failure(self):
        """Should mark file as failed with error."""
        checkpoint = Checkpoint.create_new(total_files=10)

        checkpoint.mark_processed("file1.html", success=False, error="Test error")

        assert checkpoint.processed_count == 1
        assert "file1.html" in checkpoint.processed_files
        assert len(checkpoint.failed_files) == 1
        assert checkpoint.failed_files[0].error == "Test error"

    def test_is_processed(self):
        """Should check if file was processed."""
        checkpoint = Checkpoint.create_new(total_files=10)

        checkpoint.mark_processed("file1.html")

        assert checkpoint.is_processed("file1.html")
        assert not checkpoint.is_processed("file2.html")

    def test_get_remaining_files(self):
        """Should return unprocessed files."""
        checkpoint = Checkpoint.create_new(total_files=5)
        all_files = ["file1.html", "file2.html", "file3.html", "file4.html", "file5.html"]

        checkpoint.mark_processed("file1.html")
        checkpoint.mark_processed("file3.html")

        remaining = checkpoint.get_remaining_files(all_files)

        assert len(remaining) == 3
        assert "file2.html" in remaining
        assert "file4.html" in remaining
        assert "file5.html" in remaining
        assert "file1.html" not in remaining

    def test_save_and_load_checkpoint(self, tmp_path):
        """Should save and load checkpoint from file."""
        checkpoint_path = tmp_path / "checkpoint.json"
        checkpoint = Checkpoint.create_new(total_files=10)

        checkpoint.mark_processed("file1.html", success=True)
        checkpoint.mark_processed("file2.html", success=False, error="Test error")

        # Save
        checkpoint.save(checkpoint_path)
        assert checkpoint_path.exists()

        # Load
        loaded = Checkpoint.load(checkpoint_path)
        assert loaded is not None
        assert loaded.total_files == 10
        assert loaded.processed_count == 2
        assert "file1.html" in loaded.processed_files
        assert len(loaded.failed_files) == 1
        assert loaded.failed_files[0].file_path == "file2.html"

    def test_load_nonexistent_checkpoint(self, tmp_path):
        """Should return None for nonexistent checkpoint."""
        checkpoint_path = tmp_path / "nonexistent.json"

        loaded = Checkpoint.load(checkpoint_path)

        assert loaded is None

    def test_load_corrupted_checkpoint(self, tmp_path):
        """Should return None for corrupted checkpoint."""
        checkpoint_path = tmp_path / "corrupted.json"
        checkpoint_path.write_text("not valid json{", encoding="utf-8")

        loaded = Checkpoint.load(checkpoint_path)

        assert loaded is None

    def test_checkpoint_creates_parent_directory(self, tmp_path):
        """Should create parent directory when saving."""
        checkpoint_path = tmp_path / "subdir" / "checkpoint.json"
        checkpoint = Checkpoint.create_new(total_files=5)

        checkpoint.save(checkpoint_path)

        assert checkpoint_path.exists()
        assert checkpoint_path.parent.exists()

    def test_multiple_mark_processed_updates_count(self):
        """Should update processed count correctly."""
        checkpoint = Checkpoint.create_new(total_files=10)

        checkpoint.mark_processed("file1.html")
        checkpoint.mark_processed("file2.html")
        checkpoint.mark_processed("file3.html")

        assert checkpoint.processed_count == 3
        assert len(checkpoint.processed_files) == 3
