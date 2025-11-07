"""Unit tests for DownloadSession statistics accumulation."""

from time import sleep

import pytest
from page_downloader.models import DownloadSession


class TestDownloadSession:
    def test_initial_state(self):
        session = DownloadSession(total=5)
        assert session.total == 5
        assert session.processed == 0
        assert session.duration == 0.0
        assert session.success_rate == 0.0

    def test_start_and_finish_updates_duration(self):
        session = DownloadSession(total=1)
        session.start()
        sleep(0.01)
        session.finish()
        assert session.duration > 0
        assert session.finished_at is not None

    def test_record_success_and_bytes(self):
        session = DownloadSession(total=2)
        session.start()
        session.record(success=True, bytes_downloaded=1000)
        session.record(success=True, bytes_downloaded=500)
        session.finish()
        assert session.success_count == 2
        assert session.bytes_downloaded == 1500
        assert session.failure_count == 0
        assert session.skipped_count == 0
        assert session.processed == 2
        assert session.success_rate == 1.0

    def test_record_failure_and_skipped(self):
        session = DownloadSession(total=3)
        session.start()
        session.record(success=False)
        session.record(success=True, bytes_downloaded=200)
        session.record(success=True, skipped=True)  # Should increment skipped, not success
        session.finish()
        assert session.success_count == 1
        assert session.failure_count == 1
        assert session.skipped_count == 1
        assert session.processed == 3
        assert session.remaining == 0
        assert session.success_rate == pytest.approx(1 / 3, rel=1e-6)

    def test_average_bytes_per_second_nonzero(self):
        session = DownloadSession(total=1)
        session.start()
        session.record(success=True, bytes_downloaded=5000)
        sleep(0.01)
        session.finish()
        assert session.average_bytes_per_second > 0

    def test_summary_contains_expected_keys(self):
        session = DownloadSession(total=2)
        session.start()
        session.record(success=True, bytes_downloaded=10)
        session.record(success=False)
        session.finish()
        summary = session.summary()
        assert summary["total"] == 2
        assert summary["processed"] == 2
        assert summary["success"] == 1
        assert summary["failed"] == 1
        assert summary["skipped"] == 0
        assert "duration_sec" in summary
        assert "avg_bytes_per_sec" in summary
        assert "success_rate" in summary
        assert summary["remaining"] == 0

    def test_record_skipped_only(self):
        session = DownloadSession(total=2)
        session.start()
        session.record(success=True, skipped=True)
        session.record(success=False, skipped=True)
        session.finish()
        assert session.skipped_count == 2
        assert session.success_count == 0
        assert session.failure_count == 0
        assert session.processed == 2
        assert session.success_rate == 0.0

    def test_no_double_start(self):
        session = DownloadSession(total=1)
        session.start()
        first_start = session.started_at
        session.start()  # Should do nothing
        assert session.started_at == first_start

    def test_finish_without_start(self):
        session = DownloadSession(total=1)
        session.finish()  # Should be harmless
        assert session.finished_at is None
        assert session.duration == 0.0
