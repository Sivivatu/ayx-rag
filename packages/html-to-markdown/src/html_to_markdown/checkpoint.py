"""Checkpoint management for resumable batch conversions."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class CheckpointEntry:
    """Single checkpoint entry for a processed file."""

    file_path: str
    status: str  # 'success' or 'failed'
    timestamp: str
    error: str | None = None


@dataclass
class Checkpoint:
    """Checkpoint state for batch conversion."""

    started_at: str
    last_updated: str
    total_files: int
    processed_count: int
    processed_files: list[str]
    failed_files: list[CheckpointEntry]

    @classmethod
    def create_new(cls, total_files: int) -> Checkpoint:
        """Create a new checkpoint."""
        now = datetime.now().isoformat()
        return cls(
            started_at=now,
            last_updated=now,
            total_files=total_files,
            processed_count=0,
            processed_files=[],
            failed_files=[],
        )

    def mark_processed(self, file_path: str, success: bool = True, error: str | None = None) -> None:
        """Mark a file as processed."""
        self.processed_files.append(file_path)
        self.processed_count = len(self.processed_files)
        self.last_updated = datetime.now().isoformat()

        if not success:
            entry = CheckpointEntry(
                file_path=file_path,
                status="failed",
                timestamp=datetime.now().isoformat(),
                error=error,
            )
            self.failed_files.append(entry)

    def is_processed(self, file_path: str) -> bool:
        """Check if file was already processed."""
        return file_path in self.processed_files

    def save(self, checkpoint_path: Path) -> None:
        """Save checkpoint to file."""
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to dict for JSON serialization
        data = {
            "started_at": self.started_at,
            "last_updated": self.last_updated,
            "total_files": self.total_files,
            "processed_count": self.processed_count,
            "processed_files": self.processed_files,
            "failed_files": [asdict(f) for f in self.failed_files],
        }

        checkpoint_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, checkpoint_path: Path) -> Checkpoint | None:
        """Load checkpoint from file."""
        if not checkpoint_path.exists():
            return None

        try:
            data = json.loads(checkpoint_path.read_text(encoding="utf-8"))

            # Convert failed_files back to CheckpointEntry objects
            failed_files = [CheckpointEntry(**f) for f in data.get("failed_files", [])]

            return cls(
                started_at=data["started_at"],
                last_updated=data["last_updated"],
                total_files=data["total_files"],
                processed_count=data["processed_count"],
                processed_files=data["processed_files"],
                failed_files=failed_files,
            )
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            # Return None if checkpoint is corrupted
            return None

    def get_remaining_files(self, all_files: list[str]) -> list[str]:
        """Get list of files that haven't been processed yet."""
        processed_set = set(self.processed_files)
        return [f for f in all_files if f not in processed_set]
