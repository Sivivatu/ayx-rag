#!/usr/bin/env python3
"""
uv-ayx-rag: RAG system for Alteryx help documentation.

This is the main entry point for all CLI commands. Individual features are
organized as workspace packages with isolated dependencies.
"""

import sys

# Version from pyproject.toml
import tomllib
import warnings
from pathlib import Path

import typer


def _get_version() -> str:
    """Read version from pyproject.toml."""
    try:
        pyproject_path = Path(__file__).parent / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        return data["project"]["version"]
    except FileNotFoundError:
        warnings.warn("pyproject.toml not found, version unknown", stacklevel=2)
        return "unknown"
    except KeyError:
        warnings.warn("Version field not found in pyproject.toml", stacklevel=2)
        return "unknown"
    except tomllib.TOMLDecodeError as e:
        warnings.warn(f"Failed to parse pyproject.toml: {e}", stacklevel=2)
        return "unknown"


__version__ = _get_version()

# Create main CLI application
app = typer.Typer(
    name="uv-ayx-rag",
    help="RAG system for Alteryx help documentation",
    no_args_is_help=True,
    add_completion=False,
)


def version_callback(value: bool):
    """Callback for --version flag."""
    if value:
        typer.echo(f"uv-ayx-rag version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool | None = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
):
    """RAG system for Alteryx help documentation."""
    pass


@app.command("sitemap-filter")
def sitemap_filter(
    sitemap_file: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Path to XML sitemap file to filter",
    ),
    language: list[str] | None = typer.Option(
        ["en"],
        "--language",
        "-l",
        help="Filter by language code (en, de, es, fr, it, ja, pt, zh-CHS, all). Defaults to 'en'. Use 'all' for all languages.",
    ),
    product: list[str] | None = typer.Option(
        None, "--product", "-p", help="Filter by product path segment. Can specify multiple times."
    ),
    format: str = typer.Option("text", "--format", "-f", help="Output format: json, text, or xml"),
    output: Path | None = typer.Option(
        None, "--output", "-o", help="Write output to file instead of stdout"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show statistics without outputting URLs"
    ),
):
    """Filter Alteryx sitemap URLs by language and product."""
    # Import here to avoid circular imports and execution issues
    from sitemap_filter.cli import filter_sitemap as do_filter

    do_filter(sitemap_file, language, product, format, output, dry_run)


@app.command("page-downloader")
def page_downloader(
    url: str = typer.Argument(..., help="URL to download or path to URL list file"),
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
        "-q",
        help="Suppress progress output in batch mode",
    ),
    delay: float = typer.Option(
        0.5,
        "--delay",
        help="Delay (seconds) between requests in batch mode",
    ),
):
    """Download HTML pages from URLs for RAG pipeline content collection."""
    # Import here to avoid circular imports and execution issues
    from page_downloader.cli import main as do_download

    # Forward to package CLI. The underlying function expects the first positional
    # argument to be the URL or a path to a file of URLs (batch mode).
    do_download(
        url,  # url_or_file positional
        output_dir=output_dir,
        max_file_size=max_file_size,
        connection_timeout=connection_timeout,
        read_timeout=read_timeout,
        max_retries=max_retries,
        force=force,
        dry_run=dry_run,
        no_verify_ssl=no_verify_ssl,
        verbose=verbose,
        quiet=quiet,
        delay=delay,
    )


@app.command("sitemap-download")
def sitemap_download(
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
):
    """Download Alteryx sitemap with progress tracking."""
    # Import here to avoid circular imports and execution issues
    from sitemap_download.downloader import SitemapDownloader
    from sitemap_download.exceptions import ConfigurationError
    from sitemap_download.models import DownloadConfig, DownloadProgress
    from sitemap_download.utils import archive_file

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
        if not quiet:
            from sitemap_download.cli import display_progress

            display_progress(progress, quiet)

    result = downloader.download(progress_callback=progress_callback if not quiet else None)

    # Clear progress line
    if not quiet and result.success:
        sys.stdout.write("\r" + " " * 120 + "\r")  # Clear line
        sys.stdout.flush()

    # Handle result
    if result.success:
        from sitemap_download.cli import format_bytes

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
                    f"⚠ Validation warning: {result.validation_result.error_message}", err=True
                )

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


# Register html-to-markdown CLI (Phase 1 scaffold)
# Note: This feature exposes multiple nested subcommands (convert, batch, evaluate),
# so we register it as a Typer sub-app via `app.add_typer(...)` instead of using
# a single `@app.command` wrapper. Other features here are single top-level commands
# and thus use `@app.command` for a flatter CLI. This follows Typer's recommended
# pattern for nested CLIs and aligns with Constitution Principle IX (single main
# entry point with feature apps registered as subcommands).
try:
    from html_to_markdown import app as html_to_markdown_app

    app.add_typer(
        html_to_markdown_app, name="html-to-markdown", help="Convert HTML to Markdown"
    )
except Exception as e:  # pragma: no cover - safeguard during scaffold
    # Defer import errors until feature fully implemented
    warnings.warn(f"Failed to load html-to-markdown CLI: {e}", stacklevel=2)


if __name__ == "__main__":
    app()
