"""Progress tracking utilities using rich.Progress for batch downloads."""

from __future__ import annotations

from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from .models import DownloadSession


class ProgressTracker:
    """A thin wrapper around rich.Progress to track batch downloads.

    - Supports quiet mode (no rendering)
    - Allows updating current message/URL
    - Integrates with DownloadSession for stats
    """

    def __init__(self, total: int, quiet: bool = False, console: Console | None = None) -> None:
        self.total = total
        self.quiet = quiet
        self.console = console or Console(stderr=True)
        self._progress: Progress | None = None
        self._task_id: int | None = None
        self._session: DownloadSession | None = None

    def _build_progress(self) -> Progress:
        return Progress(
            SpinnerColumn(style="cyan"),
            TextColumn("{task.description}", justify="left"),
            BarColumn(bar_width=None),
            TextColumn("{task.completed}/{task.total}", style="bold"),
            TimeElapsedColumn(),
            console=self.console,
            transient=True,
        )

    def start(self, session: DownloadSession) -> None:
        self._session = session
        if self.quiet:
            session.start()
            return
        self._progress = self._build_progress()
        self._progress.start()
        self._task_id = self._progress.add_task("Starting...", total=self.total)
        session.start()

    def set_message(self, message: str) -> None:
        if self.quiet or not self._progress or self._task_id is None:
            return
        self._progress.update(self._task_id, description=message)

    def update_success(self, url: str, *, bytes_downloaded: int = 0) -> None:
        # Update session stats first
        if self._session is not None:
            self._session.record(success=True, bytes_downloaded=bytes_downloaded)
        self._update_common(url)

    def update_failure(self, url: str) -> None:
        if self._session is not None:
            self._session.record(success=False)
        self._update_common(url)

    def update_skipped(self, url: str) -> None:
        if self._session is not None:
            self._session.record(success=False, skipped=True)
        self._update_common(url)

    def _update_common(self, url: str) -> None:
        if self.quiet or not self._progress or self._task_id is None:
            return
        # Advance by 1 and update current URL
        self._progress.update(self._task_id, advance=1, description=url)

    def finish(self, session: DownloadSession) -> None:
        session.finish()
        if self.quiet:
            return
        if self._progress:
            try:
                self._progress.stop()
            finally:
                self._progress = None
                self._task_id = None
        self._session = None
