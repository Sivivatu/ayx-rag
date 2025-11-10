from __future__ import annotations

from typing import Optional

try:
    import markdownify as md
    _MD_AVAILABLE = True
    _MD_VERSION: Optional[str] = getattr(md, "__version__", "unknown")
except Exception:  # pragma: no cover - optional dep detection
    md = None  # type: ignore
    _MD_AVAILABLE = False
    _MD_VERSION = None


class MarkdownifyStrategy:
    name = "markdownify"

    def available(self) -> bool:
        return _MD_AVAILABLE

    def version(self) -> str:
        return _MD_VERSION or "unknown"

    def convert(self, html: str) -> str:
        if not _MD_AVAILABLE:
            raise RuntimeError("markdownify not available")
        # Configure markdownify to preserve links/images/code blocks reasonably
        return md.markdownify(html, heading_style="ATX", strip="script|style")

    def supports_tables(self) -> bool:
        # markdownify has limited table support; treat as False for fidelity benchmark
        return False

    def supports_code_lang(self) -> bool:
        # Does not infer language from class; treat as False
        return False
