from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Optional

try:
    # Docling has a high-level API; fall back if not installed.
    from docling.document_converter import DocumentConverter  # type: ignore

    _DOCLING_AVAILABLE = True
    _DOCLING_VERSION = "2.61.2"  # Known installed version
except Exception:  # pragma: no cover - optional dep detection
    DocumentConverter = None  # type: ignore
    _DOCLING_AVAILABLE = False
    _DOCLING_VERSION = "unavailable"


class DoclingStrategy:
    name = "docling"

    def __init__(self) -> None:
        self._converter: Optional[DocumentConverter] = None
        if _DOCLING_AVAILABLE:
            try:  # Lazy init
                self._converter = DocumentConverter()
            except Exception:
                self._converter = None

    def available(self) -> bool:
        return _DOCLING_AVAILABLE and self._converter is not None

    def version(self) -> str:
        return _DOCLING_VERSION

    def convert(self, html: str) -> str:
        if not self.available():
            raise RuntimeError("docling not available")

        # Docling requires file input; write HTML to temp file and convert
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".html", delete=False, encoding="utf-8"
            ) as f:
                f.write(html)
                temp_path = f.name

            try:
                result = self._converter.convert(temp_path)  # type: ignore[union-attr]
                # Extract markdown from conversion result
                markdown = result.document.export_to_markdown()  # type: ignore[attr-defined]
                return markdown
            finally:
                # Clean up temp file
                Path(temp_path).unlink(missing_ok=True)
        except Exception as e:
            # If conversion fails, raise with context
            raise RuntimeError(f"Docling conversion failed: {e}") from e

    def supports_tables(self) -> bool:
        # Docling focuses on structured extraction; treat tables as supported.
        return True

    def supports_code_lang(self) -> bool:
        # Docling preserves code blocks but may not infer language
        return False
