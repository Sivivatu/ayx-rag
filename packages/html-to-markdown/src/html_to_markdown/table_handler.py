"""Table handling for HTML to Markdown conversion."""

from __future__ import annotations

from html.parser import HTMLParser


class TableAnalyzer(HTMLParser):
    """Analyze HTML table structure to determine conversion strategy."""

    def __init__(self):
        super().__init__()
        self.has_rowspan = False
        self.has_colspan = False
        self.has_nested_tags = False
        self.current_tag = None
        self.tag_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Track table complexity indicators."""
        if tag in ("td", "th"):
            self.current_tag = tag
            # Check for rowspan/colspan
            for attr_name, attr_value in attrs:
                if attr_name == "rowspan" and attr_value and attr_value != "1":
                    self.has_rowspan = True
                elif attr_name == "colspan" and attr_value and attr_value != "1":
                    self.has_colspan = True
        elif self.current_tag in ("td", "th"):
            # Track nested tags within cells
            self.tag_depth += 1
            if self.tag_depth > 1 or tag not in ("a", "code", "strong", "em", "b", "i"):
                self.has_nested_tags = True

    def handle_endtag(self, tag: str) -> None:
        """Track tag depth."""
        if tag in ("td", "th"):
            self.current_tag = None
            self.tag_depth = 0
        elif self.current_tag in ("td", "th"):
            self.tag_depth = max(0, self.tag_depth - 1)

    def is_complex(self) -> bool:
        """Determine if table is too complex for Markdown pipes."""
        return self.has_rowspan or self.has_colspan or self.has_nested_tags


def should_use_html_fallback(table_html: str, hybrid_mode: bool = True) -> bool:
    """
    Determine if table should use HTML fallback instead of Markdown pipes.

    Args:
        table_html: HTML table markup
        hybrid_mode: Whether to use hybrid approach (fallback for complex tables)

    Returns:
        True if HTML fallback should be used
    """
    if not hybrid_mode:
        return False

    analyzer = TableAnalyzer()
    analyzer.feed(table_html)
    return analyzer.is_complex()


def convert_table_to_markdown(table_html: str) -> str:
    """
    Convert simple HTML table to Markdown pipe format.

    This is a basic implementation. The markdownify library handles this better,
    so in practice we'll delegate to the strategy. This function is here for
    documentation and as a fallback.

    Args:
        table_html: HTML table markup

    Returns:
        Markdown table or HTML (if complex)

    Note:
        Complex tables (with rowspan, colspan, or nested elements) are returned
        as-is in HTML format. Simple tables are converted to Markdown pipes.
    """
    # For now, delegate to markdownify strategy
    # This is a placeholder for the hybrid approach
    # Actual implementation will be in converter.py using the strategy
    return table_html


def extract_table_cells(table_html: str) -> list[list[str]]:
    """
    Extract cell contents from HTML table for analysis.

    Args:
        table_html: HTML table markup

    Returns:
        List of rows, where each row is a list of cell contents
    """

    class CellExtractor(HTMLParser):
        """Extract cell text content from table."""

        def __init__(self):
            super().__init__()
            self.rows: list[list[str]] = []
            self.current_row: list[str] = []
            self.current_cell: list[str] = []
            self.in_cell = False

        def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
            if tag == "tr":
                self.current_row = []
            elif tag in ("td", "th"):
                self.current_cell = []
                self.in_cell = True

        def handle_endtag(self, tag: str) -> None:
            if tag == "tr" and self.current_row:
                self.rows.append(self.current_row)
            elif tag in ("td", "th"):
                self.current_row.append("".join(self.current_cell).strip())
                self.current_cell = []
                self.in_cell = False

        def handle_data(self, data: str) -> None:
            if self.in_cell:
                self.current_cell.append(data)

    extractor = CellExtractor()
    extractor.feed(table_html)
    return extractor.rows
