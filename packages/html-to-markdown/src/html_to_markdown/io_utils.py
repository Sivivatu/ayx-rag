"""File I/O utilities for HTML to Markdown conversion."""

from __future__ import annotations

import hashlib
from collections.abc import Iterator
from pathlib import Path

from .models import SourceDocument


def discover_html_files(source_dir: Path, exclusions: list[str] | None = None) -> Iterator[Path]:
    """
    Discover HTML files in directory, respecting exclusions.

    Args:
        source_dir: Directory to search
        exclusions: List of glob patterns to exclude

    Yields:
        Path objects for HTML files
    """
    exclusions = exclusions or []

    for html_file in source_dir.rglob("*.html"):
        # Check if file matches any exclusion pattern
        if any(html_file.match(pattern) for pattern in exclusions):
            continue
        yield html_file


def read_html(path: Path, encoding: str = "utf-8") -> str:
    """
    Read HTML file content with encoding detection.

    Args:
        path: Path to HTML file
        encoding: Character encoding (default: utf-8)

    Returns:
        HTML content as string

    Raises:
        FileNotFoundError: If file doesn't exist
        UnicodeDecodeError: If encoding fails
    """
    return path.read_text(encoding=encoding)


def write_markdown(path: Path, content: str, encoding: str = "utf-8") -> None:
    """
    Write Markdown content to file.

    Args:
        path: Output path
        content: Markdown content
        encoding: Character encoding (default: utf-8)
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding=encoding)


def compute_hash(content: str) -> str:
    """
    Compute SHA-256 hash of content for idempotency checks.

    Args:
        content: String content to hash

    Returns:
        Hexadecimal hash string
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def map_output_path(
    source_path: Path, source_dir: Path, output_dir: Path, extension: str = ".md"
) -> Path:
    """
    Map source HTML path to output Markdown path, preserving directory structure.

    Args:
        source_path: Source HTML file path
        source_dir: Base source directory
        output_dir: Base output directory
        extension: Output file extension (default: .md)

    Returns:
        Output path with structure preserved

    Example:
        source: /data/docs/guide/install.html
        source_dir: /data/docs
        output_dir: /output
        -> /output/guide/install.md
    """
    relative_path = source_path.relative_to(source_dir)
    output_path = output_dir / relative_path.with_suffix(extension)
    return output_path


def load_source_document(path: Path) -> SourceDocument:
    """
    Load HTML file as SourceDocument with metadata.

    Args:
        path: Path to HTML file

    Returns:
        SourceDocument with filesystem metadata
    """
    doc = SourceDocument.from_path(path)

    # Compute content hash
    content = read_html(path)
    doc.hash = compute_hash(content)

    # Try to infer title from first H1 (basic implementation)
    # Full implementation would use HTML parser
    if "<h1>" in content.lower():
        start = content.lower().index("<h1>") + 4
        end = content.lower().index("</h1>", start)
        doc.inferred_title = content[start:end].strip()
    else:
        doc.inferred_title = path.stem

    return doc


def normalize_content(content: str) -> str:
    """
    Normalize content for deterministic output.

    - Strip trailing whitespace from lines
    - Collapse multiple blank lines to single blank line
    - Ensure single trailing newline

    Args:
        content: Raw content

    Returns:
        Normalized content
    """
    lines = content.splitlines()

    # Strip trailing whitespace from each line
    lines = [line.rstrip() for line in lines]

    # Collapse multiple blank lines
    normalized = []
    prev_blank = False
    for line in lines:
        is_blank = len(line) == 0
        if is_blank and prev_blank:
            continue
        normalized.append(line)
        prev_blank = is_blank

    # Join and ensure single trailing newline
    result = "\n".join(normalized)
    if result and not result.endswith("\n"):
        result += "\n"

    return result
