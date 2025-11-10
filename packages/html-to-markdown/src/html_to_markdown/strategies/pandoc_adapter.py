from __future__ import annotations

import shutil
import subprocess
from typing import Optional

try:  # Prefer pypandoc if available
    import pypandoc  # type: ignore

    _PYPANDOC_AVAILABLE = True
except Exception:  # pragma: no cover - optional dep detection
    pypandoc = None  # type: ignore
    _PYPANDOC_AVAILABLE = False


def _pandoc_binary() -> Optional[str]:
    return shutil.which("pandoc")


class PandocStrategy:
    name = "pandoc"

    def available(self) -> bool:
        # Available if either pypandoc or pandoc binary exists
        return _PYPANDOC_AVAILABLE or _pandoc_binary() is not None

    def version(self) -> str:
        if _PYPANDOC_AVAILABLE:
            try:
                # pypandoc exposes pandoc version
                v = pypandoc.get_pandoc_version()  # type: ignore[attr-defined]
                return str(v)
            except Exception:
                pass
        bin_path = _pandoc_binary()
        if bin_path:
            try:
                out = subprocess.run(
                    [bin_path, "--version"],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                first_line = (out.stdout or "").splitlines()[0] if out.stdout else ""
                return first_line.strip() or "unknown"
            except Exception:
                return "unknown"
        return "unknown"

    def convert(self, html: str) -> str:
        if _PYPANDOC_AVAILABLE:
            # Use GitHub-Flavored Markdown target for better tables/code fences
            return pypandoc.convert_text(html, to="gfm", format="html")  # type: ignore[attr-defined]
        bin_path = _pandoc_binary()
        if not bin_path:
            raise RuntimeError("pandoc not available (missing pypandoc and pandoc binary)")
        proc = subprocess.run(
            [bin_path, "-f", "html", "-t", "gfm"],
            input=html,
            text=True,
            capture_output=True,
            check=False,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"pandoc failed: {proc.stderr.strip()}")
        return proc.stdout

    def supports_tables(self) -> bool:
        return True

    def supports_code_lang(self) -> bool:
        return True
