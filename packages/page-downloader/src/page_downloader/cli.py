"""CLI interface for page-downloader using Typer."""

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
    url: str = typer.Argument(..., help="URL to download"),
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
        help="Preview download without actually downloading",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output",
    ),
) -> None:
    """Download a single HTML page from URL.

    Implements FR-002: Accept single URL as command-line argument.
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
        logger.info(f"Starting download of {url}")
        logger.info(f"Output directory: {output_dir}")

    try:
        # Convert output_dir string to Path (may raise ValueError for invalid paths)
        output_path = Path(output_dir)
    except ValueError as e:
        typer.echo(f"✗ Configuration error: Invalid output directory: {e}")
        raise typer.Exit(3)

    # Handle dry-run mode per FR-025
    if dry_run:
        typer.echo(f"[DRY RUN] Would download: {url}")
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
        )

        # Initialize downloader
        downloader = HTTPDownloader(config)

        # Perform download
        result = downloader.download_page(url)

        if result.success:
            typer.echo(f"✓ Success: Downloaded {url}")
            typer.echo(f"  File: {result.file_path}")
            typer.echo(f"  Size: {result.bytes_downloaded} bytes")

            if verbose:
                logger.info(f"Download complete: {result.file_path}")
                logger.info(f"Bytes downloaded: {result.bytes_downloaded}")

            raise typer.Exit(0)

        elif result.skipped:
            # Validation failure per FR-026 (exit code 2)
            typer.echo(f"⚠ Skipped: {url}")
            typer.echo(f"  Reason: {result.error_message}")

            if verbose:
                logger.warning(f"Skipped {url}: {result.error_message}")

            raise typer.Exit(2)

        else:
            # Download failure per FR-026 (exit code 1)
            typer.echo(f"✗ Failed: {url}")
            typer.echo(f"  Error: {result.error_message}")

            if verbose:
                logger.error(f"Download failed for {url}: {result.error_message}")

            raise typer.Exit(1)

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
