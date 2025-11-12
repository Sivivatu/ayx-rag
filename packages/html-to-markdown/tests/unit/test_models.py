"""Unit tests for data models."""

from datetime import datetime
from pathlib import Path

from html_to_markdown.models import (
    ConversionConfig,
    ConvertedDocument,
    EvaluationMetrics,
    EvaluationReport,
    SourceDocument,
)


class TestSourceDocument:
    """Tests for SourceDocument model."""

    def test_from_path_creates_document(self, tmp_path: Path):
        """Test creating SourceDocument from file path."""
        test_file = tmp_path / "test.html"
        test_file.write_text("<html><body>Test</body></html>")

        doc = SourceDocument.from_path(test_file)

        assert doc.path == test_file
        assert doc.size_bytes > 0
        assert isinstance(doc.modified_time, datetime)
        assert doc.original_url is None
        assert doc.inferred_title is None
        assert doc.hash is None

    def test_source_document_attributes(self):
        """Test SourceDocument attributes."""
        doc = SourceDocument(
            path=Path("/test.html"),
            size_bytes=1024,
            modified_time=datetime(2025, 1, 1),
            original_url="https://example.com/test.html",
            inferred_title="Test Page",
            hash="abc123",
        )

        assert doc.path == Path("/test.html")
        assert doc.size_bytes == 1024
        assert doc.modified_time == datetime(2025, 1, 1)
        assert doc.original_url == "https://example.com/test.html"
        assert doc.inferred_title == "Test Page"
        assert doc.hash == "abc123"


class TestConvertedDocument:
    """Tests for ConvertedDocument model."""

    def test_converted_document_creation(self):
        """Test ConvertedDocument creation."""
        doc = ConvertedDocument(
            path=Path("/output/test.md"),
            source_path=Path("/input/test.html"),
            strategy="markdownify",
            converted_at=datetime(2025, 1, 1, 12, 0),
        )

        assert doc.path == Path("/output/test.md")
        assert doc.source_path == Path("/input/test.html")
        assert doc.strategy == "markdownify"
        assert doc.converted_at == datetime(2025, 1, 1, 12, 0)
        assert doc.front_matter == {}
        assert doc.body_hash is None

    def test_to_front_matter_dict(self):
        """Test YAML front matter generation."""
        doc = ConvertedDocument(
            path=Path("/output/test.md"),
            source_path=Path("/input/test.html"),
            strategy="markdownify",
            converted_at=datetime(2025, 1, 1, 12, 0),
            front_matter={"title": "Test", "author": "John"},
        )

        fm = doc.to_front_matter_dict()

        assert fm["source_path"] == "/input/test.html"
        assert fm["strategy"] == "markdownify"
        assert fm["converted_at"] == "2025-01-01T12:00:00"
        assert fm["title"] == "Test"
        assert fm["author"] == "John"


class TestConversionConfig:
    """Tests for ConversionConfig model."""

    def test_default_config(self):
        """Test default configuration."""
        config = ConversionConfig()

        assert config.thresholds["heading_fidelity"] == 90.0
        assert config.thresholds["link_preservation"] == 95.0
        assert config.thresholds["table_preservation"] == 90.0
        assert config.thresholds["code_block_integrity"] == 80.0
        assert config.thresholds["image_alt_coverage"] == 90.0

        assert "**/node_modules/**" in config.exclusions
        assert config.hybrid_tables is True
        assert "language-python" in config.language_map
        assert config.language_map["language-python"] == "python"

    def test_custom_config(self):
        """Test custom configuration."""
        config = ConversionConfig(
            thresholds={"heading_fidelity": 85.0},
            exclusions=["**/test/**"],
            hybrid_tables=False,
            language_map={"custom-lang": "custom"},
        )

        assert config.thresholds["heading_fidelity"] == 85.0
        assert config.exclusions == ["**/test/**"]
        assert config.hybrid_tables is False
        assert config.language_map["custom-lang"] == "custom"


class TestEvaluationMetrics:
    """Tests for EvaluationMetrics model."""

    def test_metrics_creation(self):
        """Test EvaluationMetrics creation."""
        metrics = EvaluationMetrics(
            source_path=Path("/test.html"),
            heading_fidelity_pct=95.0,
            link_preservation_pct=98.0,
            table_preservation_pct=90.0,
            code_block_integrity_pct=85.0,
            image_alt_coverage_pct=100.0,
            overall_score_pct=93.6,
            warnings_count=2,
            conversion_time_ms=45.5,
        )

        assert metrics.source_path == Path("/test.html")
        assert metrics.heading_fidelity_pct == 95.0
        assert metrics.overall_score_pct == 93.6
        assert metrics.warnings_count == 2
        assert metrics.conversion_time_ms == 45.5

    def test_metrics_to_dict(self):
        """Test converting metrics to dictionary."""
        metrics = EvaluationMetrics(
            source_path=Path("/test.html"),
            heading_fidelity_pct=95.0,
            link_preservation_pct=98.0,
            table_preservation_pct=None,  # No tables
            code_block_integrity_pct=85.0,
            image_alt_coverage_pct=None,  # No images
            overall_score_pct=93.0,
        )

        d = metrics.to_dict()

        assert d["source_path"] == "/test.html"
        assert d["heading_fidelity"] == 95.0
        assert d["table_preservation"] is None
        assert d["image_alt_coverage"] is None


class TestEvaluationReport:
    """Tests for EvaluationReport model."""

    def test_report_creation(self):
        """Test EvaluationReport creation."""
        report = EvaluationReport(
            generated_at=datetime(2025, 1, 1),
            strategy="markdownify",
            metrics=[],
        )

        assert report.generated_at == datetime(2025, 1, 1)
        assert report.strategy == "markdownify"
        assert report.metrics == []
        assert report.aggregate == {}
        assert report.threshold_failures == []

    def test_compute_aggregate_empty(self):
        """Test aggregate computation with no metrics."""
        report = EvaluationReport(
            generated_at=datetime(2025, 1, 1),
            strategy="markdownify",
            metrics=[],
        )

        report.compute_aggregate()

        assert report.aggregate["file_count"] == 0

    def test_compute_aggregate_with_metrics(self):
        """Test aggregate computation with metrics."""
        metrics = [
            EvaluationMetrics(
                source_path=Path("/test1.html"),
                heading_fidelity_pct=90.0,
                link_preservation_pct=95.0,
                table_preservation_pct=85.0,
                code_block_integrity_pct=80.0,
                image_alt_coverage_pct=100.0,
                overall_score_pct=90.0,
            ),
            EvaluationMetrics(
                source_path=Path("/test2.html"),
                heading_fidelity_pct=95.0,
                link_preservation_pct=100.0,
                table_preservation_pct=None,  # No tables
                code_block_integrity_pct=None,  # No code
                image_alt_coverage_pct=90.0,
                overall_score_pct=95.0,
            ),
        ]

        report = EvaluationReport(
            generated_at=datetime(2025, 1, 1),
            strategy="markdownify",
            metrics=metrics,
        )

        report.compute_aggregate()

        assert report.aggregate["file_count"] == 2
        assert report.aggregate["avg_heading_fidelity"] == 92.5
        assert report.aggregate["avg_link_preservation"] == 97.5
        assert report.aggregate["avg_table_preservation"] == 85.0  # Only 1 file has tables
        assert report.aggregate["avg_code_block_integrity"] == 80.0  # Only 1 file has code
        assert report.aggregate["avg_image_alt_coverage"] == 95.0
        assert report.aggregate["avg_overall_score"] == 92.5

    def test_report_to_dict(self):
        """Test converting report to dictionary."""
        metrics = [
            EvaluationMetrics(
                source_path=Path("/test.html"),
                heading_fidelity_pct=90.0,
                link_preservation_pct=95.0,
                table_preservation_pct=85.0,
                code_block_integrity_pct=80.0,
                image_alt_coverage_pct=100.0,
                overall_score_pct=90.0,
            )
        ]

        report = EvaluationReport(
            generated_at=datetime(2025, 1, 1, 12, 0),
            strategy="markdownify",
            metrics=metrics,
            threshold_failures=[Path("/test.html")],
        )
        report.compute_aggregate()

        d = report.to_dict()

        assert d["generated_at"] == "2025-01-01T12:00:00"
        assert d["strategy"] == "markdownify"
        assert d["file_count"] == 1
        assert d["threshold_failures"] == ["/test.html"]
        assert len(d["metrics"]) == 1
