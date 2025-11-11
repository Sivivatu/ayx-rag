from __future__ import annotations

from loguru import logger

# Basic logger configuration for this package (can be extended later)
logger.disable("html_to_markdown")  # Disabled by default; enabled by main app if needed

from .cli import app  # re-export Typer app

__all__ = ["app", "logger"]
