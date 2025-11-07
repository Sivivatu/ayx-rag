"""CLI interface for page-downloader using Typer."""

import sys
from pathlib import Path

import typer
from loguru import logger

from page_downloader.downloader import HTTPDownloader
from page_downloader.exceptions import ConfigurationError, ValidationError
from page_downloader.models import DownloadConfig

app = typer.Typer(
    name="page-downloader",
    help="Download HTML pages from URLs for RAG pipeline content collection.",
    no_args_is_help=True,
)


@app.command()
def main(
    url_or_file: str = typer.Argument(
        ..., help="URL to download OR path to a text file containing one URL per line"
    ),
    output_dir: str = typer.Option(
        "downloads",
        "--output-dir",
        "-o",
        help="Output directory for downloaded pages",
    ),
    max_file_size: int = typer.Option(
        5 * 1024 * 1024,
        "--max-file-size",
        help="Maximum file size in bytes (default: 5MB)",
    ),
    connection_timeout: float = typer.Option(
        30.0,
        "--connection-timeout",
        help="Connection timeout in seconds",
    ),
    read_timeout: float = typer.Option(
        300.0,
        "--read-timeout",
        help="Read timeout in seconds",
    ),
    max_retries: int = typer.Option(
        3,
        "--max-retries",
        help="Maximum retry attempts for failed downloads",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force re-download even if file exists",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Preview download without executing",
    ),
    no_verify_ssl: bool = typer.Option(
        False,
        "--no-verify-ssl",
        help="Disable SSL certificate verification (use for dev/testing only)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        help="Suppress progress bar output (summary still shown)",
    ),
    delay: float = typer.Option(
        0.5,
        "--delay",
        help="Delay (seconds) between requests for rate limiting (FR-006).",
    ),
) -> None:
    """Download a single page or batch from a URL list file.

    Implements FR-002: Accept single URL as command-line argument.
    Implements FR-001: Accept text file with one URL per line for batch processing.
    Implements FR-017: Log download operations.
    Implements FR-026: Exit with standard exit codes.

    Exit codes:
        0: Success
        1: Download failure
        2: Validation failure (non-HTML content)
        3: Configuration error
    """
    # Configure logging based on verbose flag
    if verbose:
        # Add a DEBUG-level handler for verbose output
        # We don't remove existing handlers to avoid fragile ID assumptions
        # This means both default and DEBUG handlers will output in verbose mode
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level="DEBUG",
        )
        logger.info(f"Starting download target: {url_or_file}")
        logger.info(f"Output directory: {output_dir}")
        logger.info(f"SSL verification: {'disabled' if no_verify_ssl else 'enabled'}")

    try:
        # Convert output_dir string to Path (may raise ValueError for invalid paths)
        output_path = Path(output_dir)
    except ValueError as e:
        typer.echo(f"✗ Configuration error: Invalid output directory: {e}")
        raise typer.Exit(3)

    # Detect batch mode: if the argument is a path to an existing file
    arg_path = Path(url_or_file)
    is_batch = arg_path.exists() and arg_path.is_file()

    # Handle dry-run mode per FR-025
    if dry_run and not is_batch:
        typer.echo(f"[DRY RUN] Would download: {url_or_file}")
        typer.echo(f"[DRY RUN] Output directory: {output_path}")
        typer.echo("[DRY RUN] No files will be downloaded")
        raise typer.Exit(0)
    elif dry_run and is_batch:
        from page_downloader.models import URLList

        url_list = URLList.from_file(arg_path)
        typer.echo(f"[DRY RUN] Would batch download {url_list.valid_count} URLs from: {arg_path}")
        typer.echo(f"[DRY RUN] Output directory: {output_path}")
        typer.echo("[DRY RUN] No files will be downloaded")
        raise typer.Exit(0)

    try:
        # Create download configuration
        config = DownloadConfig(
            output_dir=output_path,
            max_file_size=max_file_size,
            connection_timeout=connection_timeout,
            read_timeout=read_timeout,
            max_retries=max_retries,
            force=force,
            dry_run=dry_run,
            verify_ssl=not no_verify_ssl,  # Invert the flag
            rate_limit=delay,
        )

        downloader = HTTPDownloader(config)

        if not is_batch:
            # Single URL path
            result = downloader.download_page(url_or_file)

            if result.success:
                typer.echo(f"✓ Success: Downloaded {url_or_file}")
                typer.echo(f"  File: {result.file_path}")
                typer.echo(f"  Size: {result.bytes_downloaded} bytes")
                if verbose:
                    logger.info(f"Download complete: {result.file_path}")
                    logger.info(f"{result.bytes_downloaded} bytes downloaded to {result.file_path}")
                raise typer.Exit(0)

            elif result.skipped:
                typer.echo(f"⚠ Skipped: {url_or_file}")
                typer.echo(f"  Reason: {result.error_message}")
                if verbose:
                    logger.warning(f"Skipped {url_or_file}: {result.error_message}")
                raise typer.Exit(2)
            else:
                typer.echo(f"✗ Failed: {url_or_file}")
                typer.echo(f"  Error: {result.error_message}")
                if verbose:
                    logger.error(f"Download failed for {url_or_file}: {result.error_message}")
                raise typer.Exit(1)
        else:
            # Batch mode processing
            from page_downloader.models import DownloadSession, URLList
            from page_downloader.progress import ProgressTracker

            url_list = URLList.from_file(arg_path)
            session = DownloadSession(total=url_list.valid_count)
            tracker = ProgressTracker(total=url_list.valid_count, quiet=quiet)
            tracker.start(session)
            tracker.set_message("Starting batch...")

            for url in url_list.urls:
                tracker.set_message(url)
                result = downloader.download_page(url)
                if result.success:
                    tracker.update_success(url, bytes_downloaded=result.bytes_downloaded)
                elif result.skipped:
                    tracker.update_skipped(url)
                else:
                    tracker.update_failure(url)

                # Rate limiting (simple sleep) only if delay > 0
                if config.rate_limit > 0:
                    import time as _t

                    _t.sleep(config.rate_limit)

            tracker.finish(session)

            summary = session.summary()
            typer.echo("Batch Summary:")
            typer.echo(f"  Total:    {summary['total']}")
            typer.echo(f"  Success:  {summary['success']}")
            typer.echo(f"  Failed:   {summary['failed']}")
            typer.echo(f"  Skipped:  {summary['skipped']}")
            if url_list.invalid_count:
                typer.echo(f"  Invalid:  {url_list.invalid_count}")
            typer.echo(f"  Duration: {summary['duration_sec']}s")

            # Exit code logic: failures -> 1, skipped (validation) -> 2, else 0
            if session.failure_count > 0:
                raise typer.Exit(1)
            elif session.skipped_count > 0 or url_list.invalid_count > 0:
                raise typer.Exit(2)
            else:
                raise typer.Exit(0)

    except ConfigurationError as e:
        # Configuration error per FR-026 (exit code 3)
        typer.echo(f"✗ Configuration error: {e}")

        if verbose:
            logger.error(f"Configuration error: {e}")

        raise typer.Exit(3)

    except ValueError as e:
        # Path/configuration validation errors - treat as configuration error
        typer.echo(f"✗ Configuration error: {e}")

        if verbose:
            logger.error(f"Configuration error: {e}")

        raise typer.Exit(3)

    except ValidationError as e:
        # Validation error per FR-026 (exit code 2)
        typer.echo(f"✗ Validation error: {e}")

        if verbose:
            logger.error(f"Validation error: {e}")

        raise typer.Exit(2)

    except typer.Exit:
        # Re-raise Exit exceptions (don't treat as unexpected errors)
        raise

    except Exception as e:
        # Unexpected error - treat as download failure
        typer.echo(f"✗ Unexpected error: {e}")

        if verbose:
            logger.exception(f"Unexpected error during download: {e}")

        raise typer.Exit(1)


if __name__ == "__main__":
    app()
