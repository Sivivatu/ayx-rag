"""Command-line interface for sitemap download."""

import sys
from pathlib import Path

import typer

from .downloader import SitemapDownloader
from .exceptions import ConfigurationError
from .models import DownloadConfig, DownloadProgress
from .utils import archive_file, format_bytes

app = typer.Typer(
    name="sitemap-download",
    help="Download Alteryx sitemap with progress tracking and validation",
    no_args_is_help=False,
)


def format_progress_bar(progress: DownloadProgress, width: int = 40) -> str:
    """Format progress as visual bar.

    Args:
        progress: Download progress information
        width: Width of progress bar in characters

    Returns:
        Formatted progress bar string
    """
    percentage = progress.percentage
    filled = int(width * percentage / 100)
    bar = "█" * filled + "░" * (width - filled)

    downloaded = format_bytes(progress.downloaded_bytes)
    total = format_bytes(progress.total_bytes)
    speed = format_bytes(int(progress.bytes_per_second))
    eta = progress.eta_seconds

    eta_str = f"ETA: {int(eta)}s" if eta is not None and eta != float("inf") else "ETA: --"

    return f"[{bar}] {percentage:.0f}% | {downloaded} / {total} | {speed}/s | {eta_str}"


def display_progress(progress: DownloadProgress, quiet: bool = False) -> None:
    """Display progress to console.

    Args:
        progress: Download progress information
        quiet: Whether to suppress output
    """
    if quiet:
        return

    # Clear line and print progress
    sys.stdout.write("\r" + " " * 120 + "\r")  # Clear line
    sys.stdout.write(format_progress_bar(progress))
    sys.stdout.flush()


@app.callback(invoke_without_command=True)
def download_sitemap(
    ctx: typer.Context,
    url: str = typer.Option(
        "https://help.alteryx.com/current/sitemap.xml",
        help="URL of the sitemap to download",
    ),
    output: Path = typer.Option(
        Path("alteryx-help-current-sitemap.xml"),
        "--output",
        "-o",
        help="Path where the sitemap should be saved",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force download even if local file is up-to-date",
    ),
    archive: bool = typer.Option(
        False,
        "--archive",
        "-a",
        help="Archive existing sitemap with timestamp before downloading",
    ),
    connection_timeout: float = typer.Option(
        30.0,
        help="Connection timeout in seconds",
    ),
    read_timeout: float = typer.Option(
        300.0,
        help="Read timeout in seconds",
    ),
    max_retries: int = typer.Option(
        3,
        help="Maximum number of retry attempts",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress progress output",
    ),
) -> None:
    """Download the Alteryx help sitemap from a remote URL.

    By default, checks if the remote sitemap has been modified since the last
    download and skips downloading if unchanged. Use --force to bypass this check.
    """
    # Archive existing file if requested
    if archive:
        archive_path = archive_file(output)
        if archive_path and not quiet:
            typer.echo(f"Archived existing file to: {archive_path}")

    # Validate configuration
    try:
        config = DownloadConfig(
            url=url,
            destination=output,
            force=force,
            connection_timeout=connection_timeout,
            read_timeout=read_timeout,
            max_retries=max_retries,
        )
    except (ValueError, ConfigurationError) as e:
        typer.echo(f"✗ Configuration error: {e}", err=True)
        raise typer.Exit(code=3)

    # Create downloader
    downloader = SitemapDownloader(config)

    if not quiet:
        typer.echo("Downloading sitemap...")

    # Perform download with progress tracking
    def progress_callback(progress: DownloadProgress) -> None:
        display_progress(progress, quiet)

    result = downloader.download(progress_callback=progress_callback if not quiet else None)

    # Clear progress line
    if not quiet and result.success:
        sys.stdout.write("\r" + " " * 120 + "\r")  # Clear line
        sys.stdout.flush()

    # Handle result
    if result.success:
        if result.skipped:
            if not quiet:
                typer.echo("✓ Local sitemap is up-to-date (use --force to re-download)")
        else:
            if not quiet:
                size_str = format_bytes(result.file_size)
                duration_str = f"{result.duration_seconds:.1f}s"
                speed = (
                    result.file_size / result.duration_seconds if result.duration_seconds > 0 else 0
                )
                speed_str = format_bytes(int(speed))
                typer.echo(f"✓ Download complete: {size_str} in {duration_str} ({speed_str}/s)")
            else:
                typer.echo(f"✓ Sitemap downloaded: {format_bytes(result.file_size)}")

        # Show validation results
        if result.validation_result and not quiet:
            if result.validation_result.valid:
                typer.echo(
                    f"✓ Validation successful: {result.validation_result.url_count:,} URLs found"
                )
            else:
                typer.echo(
                    f"✗ Validation failed: {result.validation_result.error_message}", err=True
                )
                raise typer.Exit(code=2)

        if not quiet:
            typer.echo(f"\nSitemap saved to: {result.file_path}")

        raise typer.Exit(code=0)
    else:
        # Download failed
        typer.echo(f"✗ Download failed: {result.error_message}", err=True)

        if not quiet:
            typer.echo("\nTroubleshooting:", err=True)
            typer.echo("- Check network connection", err=True)
            typer.echo(
                f"- Try increasing timeouts (current: connect={connection_timeout}s, read={read_timeout}s)",
                err=True,
            )
            typer.echo(f"- Verify URL is accessible: {url}", err=True)

        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
