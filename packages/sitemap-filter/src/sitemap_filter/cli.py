"""Main CLI entry point for sitemap filter."""

from pathlib import Path
from typing import List, Optional
import sys
import json

import typer
from loguru import logger

from sitemap_filter.filters.parser import parse_sitemap
from sitemap_filter.filters import FilterCriteria, apply_filters
from sitemap_filter.filters.output import format_json, format_txt, format_xml

# Configure loguru for the application
logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)

# Create typer app - use as a single command app
app = typer.Typer(
    name="sitemap-filter",
    help="Filter Alteryx help documentation sitemap by language and product",
    add_completion=False
)


def filter_sitemap(
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
    """Filter sitemap URLs by language and product."""
    try:
        logger.info(f"Processing sitemap: {sitemap_file}")
        
        # Parse sitemap
        entries = parse_sitemap(sitemap_file)
        total_count = len(entries)
        
        # Build filter criteria
        filter_languages = [] if (language and 'all' in language) else (language or [])
        filter_products = product or []
        
        criteria = FilterCriteria(languages=filter_languages, products=filter_products)
        
        # Apply combined filters
        if filter_languages or filter_products:
            logger.info(f"Applying filters: languages={filter_languages or 'all'}, products={filter_products or 'all'}")
            entries = apply_filters(entries, criteria)
        else:
            logger.info("No filters specified - returning all entries")
        
        filtered_count = len(entries)
        
        # Display statistics to stderr
        logger.info(f"Total URLs: {total_count}")
        logger.info(f"Filtered URLs: {filtered_count}")
        if language and 'all' in language:
            logger.info("Language: all")
        elif language:
            logger.info(f"Language: {', '.join(language)}")
        if product:
            logger.info(f"Products: {', '.join(product)}")
        
        # Output formatting will be added in Phase 6
        if dry_run:
            logger.info("Dry run complete - no output generated")
            return
        
        # Format output based on selected format
        if format == "json":
            output_data = format_json(entries, total_count)
            output_str = json.dumps(output_data, indent=2)
        elif format == "text":
            output_str = format_txt(entries)
        elif format == "xml":
            output_str = format_xml(entries)
        else:
            logger.error(f"Unknown format: {format}")
            raise typer.Exit(code=1)
        
        # Write to file or stdout
        if not output:
            print(output_str, end='' if format == "text" else '\n')
        else:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(output_str)
            logger.info(f"Output written to: {output}")
        
    except FileNotFoundError as e:
        logger.error(f"Error: {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()

