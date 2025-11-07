"""Pytest configuration and shared fixtures for page-downloader tests."""

from collections.abc import Generator
from pathlib import Path

import pytest
import respx
from httpx import Response
from page_downloader.models import DownloadConfig


@pytest.fixture
def sample_config(tmp_path: Path) -> DownloadConfig:
    """Create a basic DownloadConfig with temporary output directory.

    Args:
        tmp_path: Pytest temporary directory fixture

    Returns:
        DownloadConfig instance configured for testing
    """
    return DownloadConfig(
        output_dir=tmp_path / "downloads",
        rate_limit=0.0,  # No delay for faster tests
        connection_timeout=5.0,
        read_timeout=10.0,
        max_retries=2,
        max_file_size=5 * 1024 * 1024,  # 5MB
        force=False,
        dry_run=False,
        ignore_robots=True,  # Skip robots.txt in tests by default
    )


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    """Create a temporary output directory for test downloads.

    Args:
        tmp_path: Pytest temporary directory fixture

    Returns:
        Path to temporary output directory
    """
    output_dir = tmp_path / "test_downloads"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


@pytest.fixture
def mock_html_response() -> Response:
    """Create a mock HTTP response with HTML content.

    Returns:
        httpx.Response with sample HTML content
    """
    html_content = """<!DOCTYPE html>
<html>
<head><title>Test Page</title></head>
<body><h1>Test Content</h1></body>
</html>"""

    return Response(
        status_code=200,
        headers={
            "content-type": "text/html; charset=utf-8",
            "content-length": str(len(html_content)),
            "last-modified": "Wed, 05 Nov 2024 12:00:00 GMT",
        },
        content=html_content.encode("utf-8"),
    )


@pytest.fixture
def mock_non_html_response() -> Response:
    """Create a mock HTTP response with non-HTML content (PDF).

    Returns:
        httpx.Response with PDF content-type
    """
    return Response(
        status_code=200,
        headers={
            "content-type": "application/pdf",
            "content-length": "1024",
        },
        content=b"%PDF-1.4 fake pdf content",
    )


@pytest.fixture
def mock_large_response() -> Response:
    """Create a mock HTTP response exceeding max file size.

    Returns:
        httpx.Response with >5MB content
    """
    large_content = b"x" * (6 * 1024 * 1024)  # 6MB

    return Response(
        status_code=200,
        headers={
            "content-type": "text/html; charset=utf-8",
            "content-length": str(len(large_content)),
        },
        content=large_content,
    )


@pytest.fixture
def sample_valid_html(tmp_path: Path) -> Path:
    """Path to valid.html fixture file.

    Args:
        tmp_path: Not used, but kept for consistency

    Returns:
        Path to sample valid HTML file
    """
    fixtures_dir = Path(__file__).parent / "fixtures" / "sample_pages"
    return fixtures_dir / "valid.html"


@pytest.fixture
def sample_large_html(tmp_path: Path) -> Path:
    """Path to large.html fixture file (>5MB), generated on-demand.

    Creates the large.html file if it doesn't exist to avoid committing
    6MB+ files to git. File is generated once per test session and reused.

    Args:
        tmp_path: Not used, but kept for consistency

    Returns:
        Path to sample large HTML file
    """
    fixtures_dir = Path(__file__).parent / "fixtures" / "sample_pages"
    large_html_path = fixtures_dir / "large.html"

    # Generate file if it doesn't exist (not in git)
    if not large_html_path.exists():
        content_base = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Large HTML File for Testing</title>
</head>
<body>
    <h1>Large HTML File - File Size Validation Test</h1>
    <p>This file exceeds the default 5MB limit for testing max file size enforcement.</p>
"""
        padding = (
            '<div class="content-block"><p>'
            + ("Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 100)
            + "</p></div>\n"
        )

        with open(large_html_path, "w") as f:
            f.write(content_base)
            target_size = 6 * 1024 * 1024  # 6MB
            current_size = len(content_base)
            while current_size < target_size:
                f.write(padding)
                current_size += len(padding)
            f.write("</body>\n</html>")

    return large_html_path


@pytest.fixture
def respx_mock() -> Generator:
    """Enable respx mocking for httpx requests.

    Yields:
        respx.mock context manager for HTTP mocking
    """
    with respx.mock:
        yield respx
