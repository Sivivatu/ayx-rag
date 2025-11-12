"""Data models for HTML to Markdown conversion and evaluation."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class SourceDocument:
    """Represents an HTML source document to be converted."""

    path: Path
    size_bytes: int
    modified_time: datetime
    original_url: str | None = None
    inferred_title: str | None = None
    hash: str | None = None  # Content hash for idempotency

    @classmethod
    def from_path(cls, path: Path) -> SourceDocument:
        """Create SourceDocument from filesystem path."""
        stat = path.stat()
        return cls(
            path=path,
            size_bytes=stat.st_size,
            modified_time=datetime.fromtimestamp(stat.st_mtime),
        )


@dataclass
class ConvertedDocument:
    """Represents a converted Markdown document with metadata."""

    path: Path
    source_path: Path
    strategy: str
    converted_at: datetime
    front_matter: dict[str, Any] = field(default_factory=dict)
    body_hash: str | None = None  # Hash of Markdown body for idempotency
    markdown_content: str | None = None  # Full Markdown content with front matter

    def to_front_matter_dict(self) -> dict[str, Any]:
        """Generate YAML front matter dictionary."""
        return {
            "source_path": str(self.source_path),
            "converted_at": self.converted_at.isoformat(),
            "strategy": self.strategy,
            **self.front_matter,
        }


@dataclass
class ConversionConfig:
    """Configuration for HTML to Markdown conversion."""

    # Evaluation thresholds (0-100)
    thresholds: dict[str, float] = field(
        default_factory=lambda: {
            "heading_fidelity": 90.0,
            "link_preservation": 95.0,
            "table_preservation": 90.0,
            "code_block_integrity": 80.0,
            "image_alt_coverage": 90.0,
        }
    )

    # File exclusions (glob patterns)
    exclusions: list[str] = field(
        default_factory=lambda: ["**/node_modules/**", "**/.git/**", "**/dist/**"]
    )

    # Table handling
    hybrid_tables: bool = True  # Fallback to HTML for complex tables

    # Code language detection mapping (CSS class patterns → language)
    language_map: dict[str, str] = field(
        default_factory=lambda: {
            "language-python": "python",
            "language-javascript": "javascript",
            "language-typescript": "typescript",
            "language-bash": "bash",
            "language-shell": "shell",
            "language-sql": "sql",
            "language-json": "json",
            "language-yaml": "yaml",
            "language-xml": "xml",
            "language-html": "html",
            "language-css": "css",
            "lang-py": "python",
            "lang-js": "javascript",
            "lang-ts": "typescript",
        }
    )


@dataclass
class EvaluationMetrics:
    """Metrics for a single document evaluation."""

    source_path: Path
    heading_fidelity_pct: float
    link_preservation_pct: float
    table_preservation_pct: float | None  # None if no tables
    code_block_integrity_pct: float | None  # None if no code blocks
    image_alt_coverage_pct: float | None  # None if no images
    overall_score_pct: float
    warnings_count: int = 0
    conversion_time_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "source_path": str(self.source_path),
            "heading_fidelity": self.heading_fidelity_pct,
            "link_preservation": self.link_preservation_pct,
            "table_preservation": self.table_preservation_pct,
            "code_block_integrity": self.code_block_integrity_pct,
            "image_alt_coverage": self.image_alt_coverage_pct,
            "overall_score": self.overall_score_pct,
            "warnings_count": self.warnings_count,
            "conversion_time_ms": self.conversion_time_ms,
        }


@dataclass
class EvaluationReport:
    """Aggregated evaluation report for multiple documents."""

    generated_at: datetime
    strategy: str
    metrics: list[EvaluationMetrics]
    aggregate: dict[str, Any] = field(default_factory=dict)
    threshold_failures: list[Path] = field(default_factory=list)

    def compute_aggregate(self) -> None:
        """Compute aggregate statistics from individual metrics."""
        if not self.metrics:
            self.aggregate = {"file_count": 0}
            return

        total = len(self.metrics)
        self.aggregate = {
            "file_count": total,
            "avg_heading_fidelity": sum(m.heading_fidelity_pct for m in self.metrics) / total,
            "avg_link_preservation": sum(m.link_preservation_pct for m in self.metrics) / total,
            "avg_table_preservation": sum(
                m.table_preservation_pct
                for m in self.metrics
                if m.table_preservation_pct is not None
            )
            / sum(1 for m in self.metrics if m.table_preservation_pct is not None)
            if any(m.table_preservation_pct is not None for m in self.metrics)
            else None,
            "avg_code_block_integrity": sum(
                m.code_block_integrity_pct
                for m in self.metrics
                if m.code_block_integrity_pct is not None
            )
            / sum(1 for m in self.metrics if m.code_block_integrity_pct is not None)
            if any(m.code_block_integrity_pct is not None for m in self.metrics)
            else None,
            "avg_image_alt_coverage": sum(
                m.image_alt_coverage_pct
                for m in self.metrics
                if m.image_alt_coverage_pct is not None
            )
            / sum(1 for m in self.metrics if m.image_alt_coverage_pct is not None)
            if any(m.image_alt_coverage_pct is not None for m in self.metrics)
            else None,
            "avg_overall_score": sum(m.overall_score_pct for m in self.metrics) / total,
            "total_warnings": sum(m.warnings_count for m in self.metrics),
            "threshold_failures": len(self.threshold_failures),
        }

    def to_dict(self) -> dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "generated_at": self.generated_at.isoformat(),
            "strategy": self.strategy,
            "aggregate": self.aggregate,
            "file_count": len(self.metrics),
            "threshold_failures": [str(p) for p in self.threshold_failures],
            "metrics": [m.to_dict() for m in self.metrics],
        }


@dataclass
class DiffResult:
    """Result of comparing two conversion strategies (research phase only)."""

    source_path: Path
    strategy_a: str
    strategy_b: str
    added_lines: int
    removed_lines: int
    changed_sections: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert diff result to dictionary."""
        return {
            "source_path": str(self.source_path),
            "strategy_a": self.strategy_a,
            "strategy_b": self.strategy_b,
            "added_lines": self.added_lines,
            "removed_lines": self.removed_lines,
            "changed_sections": self.changed_sections,
        }
