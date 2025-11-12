from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser


@dataclass
class HtmlStats:
    headings: int
    links: int
    tables: int
    images: int
    code_blocks: int


class _StatsParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.headings = 0
        self.links = 0
        self.tables = 0
        self.images = 0
        self.code_blocks = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:  # noqa: D401
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.headings += 1
        elif tag == "a":
            self.links += 1
        elif tag == "table":
            self.tables += 1
        elif tag == "img":
            self.images += 1
        elif tag == "code":
            self.code_blocks += 1


def extract_html_stats(html: str) -> HtmlStats:
    parser = _StatsParser()
    parser.feed(html)
    return HtmlStats(
        headings=parser.headings,
        links=parser.links,
        tables=parser.tables,
        images=parser.images,
        code_blocks=parser.code_blocks,
    )


def score_conversion(original: HtmlStats, converted_md: str) -> dict[str, float]:
    """Heuristic fidelity scoring comparing counts in Markdown vs original HTML.

    Simplistic approach: count markers in Markdown and compare ratios.
    Headings: count lines starting with '#'
    Links: count '[' and '(' pattern occurrences (approximate)
    Tables: count '|' rows that appear table-like (>=2 pipes)
    Images: count '![' occurrences
    Code blocks: count fenced block delimiters ``` occurrences divided by 2
    Return ratios capped at 1.0.
    """
    lines = converted_md.splitlines()
    heading_md = sum(1 for ln in lines if ln.startswith("#"))
    link_md = converted_md.count("[")  # rough upper bound
    image_md = converted_md.count("![")
    table_md = sum(1 for ln in lines if ln.count("|") >= 2)
    fence_md = converted_md.count("```") // 2

    def ratio(found: int, expected: int) -> float:
        if expected == 0:
            return 1.0  # no expectation
        return min(found / expected, 1.0)

    return {
        "heading_fidelity": ratio(heading_md, original.headings),
        "link_preservation": ratio(link_md, original.links),
        "table_preservation": ratio(table_md, original.tables),
        "image_alt_coverage": ratio(image_md, original.images),
        "code_block_integrity": ratio(fence_md, original.code_blocks),
    }
