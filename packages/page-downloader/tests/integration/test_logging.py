"""Test logging output meets FR-017 requirements."""

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
    """Verify logs contain timestamp, URL, file size, and file path per FR-017."""
    url = "https://help.alteryx.com/current/en/designer/tools.html"
    html_content = b"<html><body>Test content</body></html>"

    respx.get(url).mock(
        return_value=Response(
            status_code=200,
            headers={"content-type": "text/html"},
            content=html_content,
        )
    )

    # Capture logger output
    log_stream = StringIO()
    log_id = logger.add(
        log_stream,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
    )

    try:
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = runner.invoke(
                app,
                [url, "--output-dir", tmp_dir],
            )

            assert result.exit_code == 0

            # Get log output
            log_output = log_stream.getvalue()

            # Verify required fields per FR-017
            # 1. Timestamp - loguru format: YYYY-MM-DD HH:mm:ss.SSS
            timestamp_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}"
            assert re.search(timestamp_pattern, log_output), "Log missing timestamp"

            # 2. URL
            assert url in log_output, "Log missing URL"

            # 3. File size (in bytes)
            assert (
                f"{len(html_content)} bytes" in log_output
                or f"({len(html_content)} bytes)" in log_output
            ), "Log missing file size"

            # 4. File path
            expected_path_fragment = "current/en/designer/tools.html"
            assert expected_path_fragment in log_output, (
                f"Log missing file path (expected fragment: {expected_path_fragment})"
            )

            # Verify log level is INFO for successful download
            assert "INFO" in log_output, "Log should use INFO level"

    finally:
        logger.remove(log_id)


@respx.mock
def test_logging_format():
    """Test that log format includes all standard fields."""
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
            _ = runner.invoke(
                app,
                [url, "--output-dir", tmp_dir],
            )

            log_output = log_stream.getvalue()

            # Verify structured format: timestamp | level | module:function:line - message
            # Module can contain dots (e.g., page_downloader.downloader)
            log_line_pattern = (
                r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3} \| \w+ +\| [\w_.]+:[\w_]+:\d+ - .+"
            )
            assert re.search(log_line_pattern, log_output), (
                f"Log format doesn't match expected pattern. Got:\n{log_output}"
            )

    finally:
        logger.remove(log_id)
