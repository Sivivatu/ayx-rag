"""HTML to Markdown conversion with front matter and metadata."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from .io_utils import compute_hash, normalize_content, read_html
from .models import ConversionConfig, ConvertedDocument, SourceDocument
from .strategies.markdownify_adapter import MarkdownifyStrategy


def detect_code_language(css_class: str) -> str | None:
    """
    Detect programming language from CSS class.

    Args:
        css_class: CSS class string (e.g., 'language-python', 'lang-js')

    Returns:
        Detected language name or None
    """
    if not css_class:
        return None

    # Common patterns: language-python, lang-js, python, py
    patterns = {
        "python": "python",
        "py": "python",
        "javascript": "javascript",
        "js": "javascript",
        "typescript": "typescript",
        "ts": "typescript",
        "bash": "bash",
        "sh": "bash",
        "shell": "bash",
        "json": "json",
        "yaml": "yaml",
        "yml": "yaml",
        "xml": "xml",
        "html": "html",
        "css": "css",
        "sql": "sql",
    }

    # Strip common prefixes
    lang = css_class.lower()
    for prefix in ["language-", "lang-"]:
        if lang.startswith(prefix):
            lang = lang[len(prefix) :]
            break

    return patterns.get(lang)


class HtmlConverter:
    """Convert HTML to Markdown with metadata and quality preservation."""

    def __init__(self, strategy: Any = None, config: ConversionConfig | None = None) -> None:
        """
        Initialize converter with strategy and configuration.

        Args:
            strategy: Conversion strategy (defaults to MarkdownifyStrategy)
            config: Conversion configuration
        """
        # If first arg is a ConversionConfig, treat it as config
        if isinstance(strategy, ConversionConfig):
            config = strategy
            strategy = None

        self.strategy = strategy or MarkdownifyStrategy()
        self.config = config or ConversionConfig()

        if not self.strategy.available():
            raise RuntimeError(f"Strategy {self.strategy.name} is not available")

    def convert_file(self, source_path: Path, output_path: Path | None = None) -> ConvertedDocument:
        """
        Convert HTML file to Markdown with front matter.

        Args:
            source_path: Path to HTML file
            output_path: Optional output path (if None, not written to disk)

        Returns:
            ConvertedDocument with metadata

        Raises:
            FileNotFoundError: If source file doesn't exist
            RuntimeError: If conversion fails
        """
        # Load source document
        source_doc = SourceDocument.from_path(source_path)
        html_content = read_html(source_path)
        source_doc.hash = compute_hash(html_content)

        # Try to extract title from HTML
        source_doc.inferred_title = self._extract_title(html_content)

        # Try to extract original URL from HTML comments or meta tags
        source_doc.original_url = self._extract_original_url(html_content)

        # Convert HTML to Markdown
        markdown_body = self._convert_html(html_content)

        # Normalize content for consistency
        markdown_body = normalize_content(markdown_body)

        # Generate front matter
        front_matter = self._generate_front_matter(source_doc)

        # Combine front matter and body
        full_markdown = self._combine_front_matter_and_body(front_matter, markdown_body)

        # Create converted document
        converted_doc = ConvertedDocument(
            path=output_path or source_path.with_suffix(".md"),
            source_path=source_path,
            strategy=self.strategy.name,
            converted_at=datetime.now(),
            front_matter=front_matter,
            body_hash=compute_hash(markdown_body),
            markdown_content=full_markdown,
        )

        # Write to disk if output path provided
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(full_markdown, encoding="utf-8")

        return converted_doc

    def _convert_html(self, html: str) -> str:
        """
        Convert HTML to Markdown using strategy.

        Args:
            html: HTML content

        Returns:
            Markdown content
        """
        try:
            markdown = self.strategy.convert(html)
            return markdown
        except Exception as e:
            raise RuntimeError(f"Conversion failed: {e}") from e

    def _extract_title(self, html: str) -> str:
        """
        Extract title from HTML (first H1 or <title> tag).

        Args:
            html: HTML content

        Returns:
            Extracted title or "Untitled"
        """
        # Try H1 first
        h1_match = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.IGNORECASE | re.DOTALL)
        if h1_match:
            title = h1_match.group(1)
            # Strip HTML tags from title
            title = re.sub(r"<[^>]+>", "", title)
            return title.strip()

        # Try title tag
        title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        if title_match:
            title = title_match.group(1)
            return title.strip()

        return "Untitled"

    def _extract_original_url(self, html: str) -> str | None:
        """
        Extract original URL from HTML comments or meta tags.

        Args:
            html: HTML content

        Returns:
            Original URL or None
        """
        # Try HTML comment with "source:" or "url:"
        comment_match = re.search(
            r"<!--\s*(?:source|url):\s*(https?://[^\s]+)\s*-->", html, re.IGNORECASE
        )
        if comment_match:
            return comment_match.group(1)

        # Try canonical link
        canonical_match = re.search(
            r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\'](https?://[^"\']+)["\']',
            html,
            re.IGNORECASE,
        )
        if canonical_match:
            return canonical_match.group(1)

        # Try og:url meta tag
        og_url_match = re.search(
            r'<meta[^>]+property=["\']og:url["\'][^>]+content=["\'](https?://[^"\']+)["\']',
            html,
            re.IGNORECASE,
        )
        if og_url_match:
            return og_url_match.group(1)

        return None

    def _generate_front_matter(self, source_doc: SourceDocument) -> dict[str, Any]:
        """
        Generate YAML front matter from source document.

        Args:
            source_doc: Source document metadata

        Returns:
            Front matter dictionary
        """
        front_matter: dict[str, Any] = {
            "source_path": str(source_doc.path),
            "converted_at": datetime.now().isoformat(),
            "strategy": self.strategy.name,
        }

        if source_doc.inferred_title:
            front_matter["title"] = source_doc.inferred_title

        if source_doc.original_url:
            front_matter["original_url"] = source_doc.original_url

        if source_doc.modified_time:
            front_matter["last_modified"] = source_doc.modified_time.isoformat()

        return front_matter

    def _combine_front_matter_and_body(self, front_matter: dict[str, Any], body: str) -> str:
        """
        Combine YAML front matter and Markdown body.

        Args:
            front_matter: Front matter dictionary
            body: Markdown body content

        Returns:
            Complete Markdown document with front matter
        """
        yaml_str = yaml.dump(front_matter, default_flow_style=False, sort_keys=False)
        return f"---\n{yaml_str}---\n\n{body}"

    def detect_code_language(self, code_element_html: str) -> str | None:
        """
        Detect code block language from HTML class attributes.

        Args:
            code_element_html: HTML for code element

        Returns:
            Detected language or None
        """
        # Extract class attribute
        class_match = re.search(r'class=["\']([^"\']+)["\']', code_element_html)
        if not class_match:
            return None

        classes = class_match.group(1).split()

        # Check against language map
        for class_name in classes:
            if class_name in self.config.language_map:
                return self.config.language_map[class_name]

        return None


def convert_html_to_markdown(
    html_path: Path,
    output_path: Path | None = None,
    strategy_name: str = "markdownify",
    config: ConversionConfig | None = None,
) -> ConvertedDocument:
    """
    Convenience function to convert HTML file to Markdown.

    Args:
        html_path: Path to HTML file
        output_path: Optional output path
        strategy_name: Strategy name (default: markdownify)
        config: Optional conversion configuration

    Returns:
        ConvertedDocument with metadata
    """
    from .cli import _get_strategy

    strategy = _get_strategy(strategy_name)
    converter = HtmlConverter(strategy=strategy, config=config)
    return converter.convert_file(html_path, output_path)
