from __future__ import annotations

from loguru import logger

from .cli import app  # re-export Typer app

# Basic logger configuration for this package (can be extended later)
logger.disable("html_to_markdown")  # Disabled by default; enabled by main app if needed


__all__ = ["app", "logger"]
