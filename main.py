#!/usr/bin/env python3
"""
uv-ayx-rag: RAG system for Alteryx help documentation.

This is the main entry point for all CLI commands. Individual features are
organized as workspace packages with isolated dependencies.
"""

import sys
import warnings
from pathlib import Path

import typer

# Version from pyproject.toml
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


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


if __name__ == "__main__":
    app()
