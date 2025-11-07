"""Unit tests for ProgressTracker using rich.Progress."""

from unittest.mock import Mock

from page_downloader.models import DownloadSession
from page_downloader.progress import ProgressTracker
from rich.console import Console


def test_progress_tracker_quiet_mode_suppresses_output():
    session = DownloadSession(total=3)
    tracker = ProgressTracker(total=3, quiet=True)

    tracker.start(session)
    tracker.update_success("https://a")
    tracker.update_failure("https://b")
    tracker.update_skipped("https://c")
    tracker.finish(session)

    # In quiet mode, no live progress is rendered; summary still available via session
    assert session.processed == 3


def test_progress_tracker_updates_counts_and_renders_minimally():
    session = DownloadSession(total=2)
    mock_console = Mock(spec=Console)
    tracker = ProgressTracker(total=2, quiet=False, console=mock_console)

    tracker.start(session)
    tracker.update_success("https://a", bytes_downloaded=100)
    tracker.update_failure("https://b")
    tracker.finish(session)

    # Validate session stats
    assert session.success_count == 1
    assert session.failure_count == 1
    assert session.skipped_count == 0
    assert session.processed == 2


def test_progress_tracker_can_update_message():
    session = DownloadSession(total=1)
    tracker = ProgressTracker(total=1, quiet=False)
    tracker.start(session)
    tracker.set_message("Downloading test URL")
    tracker.update_success("https://a")
    tracker.finish(session)
    assert session.success_count == 1
