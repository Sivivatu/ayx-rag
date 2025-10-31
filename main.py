#!/usr/bin/env python3
"""
uv-ayx-rag: RAG system for Alteryx help documentation.

This is the main entry point for all CLI commands. Individual features are
organized as workspace packages with isolated dependencies.
"""

from pathlib import Path
from typing import List, Optional
import typer

# Create main CLI application
app = typer.Typer(
    name="uv-ayx-rag",
    help="RAG system for Alteryx help documentation",
    no_args_is_help=True,
    add_completion=False,
)


@app.command("sitemap-filter")
def sitemap_filter(
    sitemap_file: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Path to XML sitemap file to filter"
    ),
    language: Optional[List[str]] = typer.Option(
        ["en"],
        "--language", "-l",
        help="Filter by language code (en, de, es, fr, it, ja, pt, zh-CHS, all). Defaults to 'en'. Use 'all' for all languages."
    ),
    product: Optional[List[str]] = typer.Option(
        None,
        "--product", "-p",
        help="Filter by product path segment. Can specify multiple times."
    ),
    format: str = typer.Option(
        "text",
        "--format", "-f",
        help="Output format: json, text, or xml"
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Write output to file instead of stdout"
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show statistics without outputting URLs"
    ),
):
    """Filter Alteryx sitemap URLs by language and product."""
    # Import here to avoid circular imports and execution issues
    from sitemap_filter.cli import filter_sitemap as do_filter
    do_filter(sitemap_file, language, product, format, output, dry_run)


if __name__ == "__main__":
    app()
