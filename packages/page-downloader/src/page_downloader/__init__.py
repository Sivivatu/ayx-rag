"""Page downloader for RAG pipeline content collection.

This package downloads raw HTML pages from URLs and saves them to disk
with proper error handling, rate limiting, and incremental update support.
"""

__version__ = "0.1.0"

from .cli import app

__all__ = ["__version__", "app"]
