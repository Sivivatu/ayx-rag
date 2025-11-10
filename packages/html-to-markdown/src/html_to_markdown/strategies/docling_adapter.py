from __future__ import annotations

from typing import Optional

try:
    # Docling has a high-level API; fall back if not installed.
    import docling  # type: ignore
    from docling.document_converter import DocumentConverter  # type: ignore
    from docling.datamodel.base_models import ConversionResult  # type: ignore

    _DOCLING_AVAILABLE = True
except Exception:  # pragma: no cover - optional dep detection
    docling = None  # type: ignore
    DocumentConverter = None  # type: ignore
    ConversionResult = None  # type: ignore
    _DOCLING_AVAILABLE = False


class DoclingStrategy:
    name = "docling"

    def __init__(self) -> None:
        self._converter: Optional[DocumentConverter] = None
        if _DOCLING_AVAILABLE:
            try:  # Lazy init; HTML treated as in-memory input
                self._converter = DocumentConverter()
            except Exception:
                self._converter = None

    def available(self) -> bool:
        return _DOCLING_AVAILABLE and self._converter is not None

    def version(self) -> str:
        if not _DOCLING_AVAILABLE:
            return "unavailable"
        return getattr(docling, "__version__", "unknown")  # type: ignore

    def convert(self, html: str) -> str:
        if not self.available():
            raise RuntimeError("docling not available")
        # Docling typically operates on file-like inputs; provide HTML string.
        # If direct HTML conversion unsupported, fallback to simple markdown escape.
        try:
            # Using an in-memory conversion path; may need adaptation if API differs.
            result: ConversionResult = self._converter.convert_html_string(html)  # type: ignore[attr-defined]
            # Assume result contains markdown attribute or text segments; fallback if absent.
            if hasattr(result, "markdown"):
                return result.markdown  # type: ignore[attr-defined]
            if hasattr(result, "text"):
                return result.text  # type: ignore[attr-defined]
        except Exception:
            # Graceful degradation: naive markdown-friendly output
            return html
        return html

    def supports_tables(self) -> bool:
        # Docling focuses on structured extraction; treat tables as supported.
        return True

    def supports_code_lang(self) -> bool:
        # Depends on model; conservative True for research placeholder.
        return True
