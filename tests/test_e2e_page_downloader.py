"""End-to-end integration test for page-downloader CLI via main.py."""

import tempfile
from pathlib import Path

import respx
from httpx import Response
from typer.testing import CliRunner

from main import app

runner = CliRunner()


@respx.mock
def test_e2e_page_downloader_via_main():
    """Test complete flow: main.py -> page-downloader -> download URL."""
    url = "https://help.alteryx.com/current/en/designer/tools.html"
    html_content = b"<html><head><title>Test Page</title></head><body><h1>Tools</h1><p>Test content</p></body></html>"

    # Mock the HTTP request
    respx.get(url).mock(
        return_value=Response(
            status_code=200,
            headers={"content-type": "text/html; charset=utf-8"},
            content=html_content,
        )
    )

    with tempfile.TemporaryDirectory() as tmp_dir:
        result = runner.invoke(
            app,
            ["page-downloader", url, "--output-dir", tmp_dir],
        )

        # Check exit code
        assert result.exit_code == 0, (
            f"Expected exit code 0, got {result.exit_code}. Output: {result.stdout}"
        )

        # Check output messages
        assert "Success" in result.stdout or "Downloaded" in result.stdout

        # Verify file was created with correct structure
        expected_path = Path(tmp_dir) / "current" / "en" / "designer" / "tools.html"
        assert expected_path.exists(), f"Expected file not found: {expected_path}"

        # Verify file content
        downloaded_content = expected_path.read_bytes()
        assert downloaded_content == html_content, "Downloaded content doesn't match expected"


@respx.mock
def test_e2e_page_downloader_verbose_mode():
    """Test verbose mode shows detailed logging."""
    url = "https://help.alteryx.com/current/en/designer/test.html"
    html_content = b"<html><body>Test</body></html>"

    respx.get(url).mock(
        return_value=Response(
            status_code=200,
            headers={"content-type": "text/html"},
            content=html_content,
        )
    )

    with tempfile.TemporaryDirectory() as tmp_dir:
        result = runner.invoke(
            app,
            ["page-downloader", url, "--output-dir", tmp_dir, "--verbose"],
        )

        assert result.exit_code == 0
        # Verbose output should show URL and success message
        assert url in result.stdout or "test.html" in result.stdout


def test_e2e_page_downloader_dry_run():
    """Test dry-run mode via main.py."""
    url = "https://help.alteryx.com/current/en/designer/test.html"

    result = runner.invoke(
        app,
        ["page-downloader", url, "--dry-run"],
    )

    assert result.exit_code == 0
    assert "DRY RUN" in result.stdout
    assert "Would download" in result.stdout
    assert url in result.stdout


@respx.mock
def test_e2e_page_downloader_handles_errors():
    """Test error handling through complete stack."""
    url = "https://help.alteryx.com/current/en/designer/missing.html"

    respx.get(url).mock(return_value=Response(status_code=404, content=b"Not Found"))

    with tempfile.TemporaryDirectory() as tmp_dir:
        result = runner.invoke(
            app,
            ["page-downloader", url, "--output-dir", tmp_dir],
        )

        # Should exit with code 1 (download failure)
        assert result.exit_code == 1
        assert "Failed" in result.stdout or "404" in result.stdout
