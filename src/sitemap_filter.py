"""Main CLI entry point for sitemap filter."""

from pathlib import Path
from typing import List, Optional
import sys

import typer
from loguru import logger

from src.filters.parser import parse_sitemap
from src.filters.language import filter_by_language

# Configure loguru for the application
logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)

# Create typer app
app = typer.Typer(
    name="sitemap-filter",
    help="Filter Alteryx help documentation sitemap by language and product",
    add_completion=False
)


@app.command()
def main(
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
        "json",
        "--format", "-f",
        help="Output format: json, txt, or xml"
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
    """Filter sitemap URLs by language and product."""
    try:
        logger.info(f"Processing sitemap: {sitemap_file}")
        
        # Parse sitemap
        entries = parse_sitemap(sitemap_file)
        total_count = len(entries)
        
        # Apply language filter
        if language and 'all' in language:
            logger.info("Returning all languages ('all' specified)")
            entries = filter_by_language(entries, [])  # Empty list returns all
        elif language:
            logger.info(f"Applying language filter: {language}")
            entries = filter_by_language(entries, language)
        
        # Product filter will be added in Phase 4
        if product:
            logger.warning("Product filtering not yet implemented")
        
        filtered_count = len(entries)
        
        # Display statistics to stderr
        logger.info(f"Total URLs: {total_count}")
        logger.info(f"Filtered URLs: {filtered_count}")
        if language and 'all' in language:
            logger.info("Language: all")
        elif language:
            logger.info(f"Language: {', '.join(language)}")
        
        # Output formatting will be added in Phase 6
        if dry_run:
            logger.info("Dry run complete - no output generated")
            return
        
        # For now, just print URLs (basic txt format)
        if not output:
            for entry in entries:
                print(entry.loc)
        else:
            with open(output, 'w') as f:
                for entry in entries:
                    f.write(entry.loc + '\n')
            logger.info(f"Output written to: {output}")
        
    except FileNotFoundError as e:
        logger.error(f"Error: {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()

