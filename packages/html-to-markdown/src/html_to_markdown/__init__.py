from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from typer import Typer

# Lazy load app - only import when actually accessed
def __getattr__(name: str):
    if name == "app":
        from .cli import app
        return app
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# Basic logger configuration for this package (can be extended later)
logger.disable("html_to_markdown")  # Disabled by default; enabled by main app if needed


__all__ = ["app", "logger"]
