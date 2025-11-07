"""Logging integration tests for page-downloader (FR-017)."""

import contextlib
import re
import tempfile
from io import StringIO

import respx
from httpx import Response
from loguru import logger
from page_downloader.cli import app
from typer.testing import CliRunner


@respx.mock
def test_logging_contains_required_fields():
    url = "https://help.alteryx.com/current/en/designer/tools.html"
    html_content = b"<html><body>Test content</body></html>"
    respx.get(url).mock(
        return_value=Response(
            status_code=200,
            headers={"content-type": "text/html"},
            content=html_content,
        )
    )
    log_stream = StringIO()
    log_id = logger.add(
        log_stream,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
    )
    try:
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = runner.invoke(app, [url, "--output-dir", tmp_dir, "--verbose"])
            assert result.exit_code == 0
            log_output = log_stream.getvalue()
            assert re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}", log_output)
            assert url in log_output
            assert (
                f"{len(html_content)} bytes" in log_output
                or f"({len(html_content)} bytes)" in log_output
            )
            assert "current/en/designer/tools.html" in log_output
            assert "INFO" in log_output or "DEBUG" in log_output
    finally:
        # Defensive removal: handler may auto-remove; ignore if missing
        with contextlib.suppress(ValueError):
            logger.remove(log_id)


@respx.mock
def test_logging_format():
    url = "https://help.alteryx.com/current/en/designer/test.html"
    html_content = b"<html><body>Test</body></html>"
    respx.get(url).mock(
        return_value=Response(
            status_code=200,
            headers={"content-type": "text/html"},
            content=html_content,
        )
    )
    log_stream = StringIO()
    log_id = logger.add(
        log_stream,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
    )
    try:
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmp_dir:
            _ = runner.invoke(app, [url, "--output-dir", tmp_dir, "--verbose"])
            log_output = log_stream.getvalue()
            pattern = (
                r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3} \| \w+ +\| [\w_.]+:[\w_]+:\d+ - .+"
            )
            assert re.search(pattern, log_output), f"Unexpected log format:\n{log_output}"
    finally:
        with contextlib.suppress(ValueError):
            logger.remove(log_id)
