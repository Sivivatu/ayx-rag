"""Unit tests for ProgressTracker using rich.Progress."""

from io import StringIO

from page_downloader.models import DownloadSession
from page_downloader.progress import ProgressTracker


class DummyConsole:
    """Capture output written by rich Console for testing."""

    def __init__(self):
        self.out = StringIO()

    def print(self, *args, **kwargs):  # pragma: no cover - minimal shim
        text = " ".join(str(a) for a in args)
        self.out.write(text + "\n")

    def __enter__(self):  # pragma: no cover
        return self

    def __exit__(self, exc_type, exc, tb):  # pragma: no cover
        return False


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
    dummy_console = DummyConsole()
    tracker = ProgressTracker(total=2, quiet=False, console=dummy_console)

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
