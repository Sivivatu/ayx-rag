"""Integration tests for CLI interface - single URL mode."""

import respx
from httpx import Response
from page_downloader.cli import app
from typer.testing import CliRunner
from pathlib import Path
import re

runner = CliRunner()


class TestCLISingleURLSuccess:
    """Test successful single URL downloads via CLI."""

    @respx.mock
    def test_cli_download_single_url_success(self, tmp_path):
        """Test CLI downloads single URL successfully."""
        url = "https://help.alteryx.com/current/en/designer/tools.html"
        html_content = b"<html><body><h1>Test Page</h1></body></html>"

        respx.get(url).mock(
            return_value=Response(
                status_code=200,
                headers={"content-type": "text/html; charset=utf-8"},
                content=html_content,
            )
        )

        result = runner.invoke(
            app,
            [url, "--output-dir", str(tmp_path)],
        )

        assert result.exit_code == 0
        assert "Success" in result.stdout or "Downloaded" in result.stdout

        # Verify file was created
        downloaded_files = list(tmp_path.rglob("*.html"))
        assert len(downloaded_files) == 1
        assert downloaded_files[0].read_bytes() == html_content

    @respx.mock
    def test_cli_creates_nested_directory_structure(self, tmp_path):
        """Test that CLI creates nested directories matching URL structure."""
        url = "https://help.alteryx.com/current/en/designer/tools.html"

        respx.get(url).mock(
            return_value=Response(
                status_code=200,
                headers={"content-type": "text/html"},
                content=b"<html><body>test</body></html>",
            )
        )

        result = runner.invoke(
            app,
            [url, "--output-dir", str(tmp_path)],
        )

        assert result.exit_code == 0

        # Check that nested path exists
        expected_path = tmp_path / "current" / "en" / "designer" / "tools.html"
        assert expected_path.exists()

    @respx.mock
    def test_cli_uses_default_output_dir(self, tmp_path, monkeypatch):
        """Test that CLI uses default output directory when not specified."""
        monkeypatch.chdir(tmp_path)

        url = "https://help.alteryx.com/current/en/designer/tools.html"

        respx.get(url).mock(
            return_value=Response(
                status_code=200,
                headers={"content-type": "text/html"},
                content=b"<html><body>test</body></html>",
            )
        )

        result = runner.invoke(app, [url])

        assert result.exit_code == 0

        # Should create in default 'downloads' directory
        default_dir = tmp_path / "downloads"
        assert default_dir.exists()


class TestCLISingleURLErrors:
    """Test CLI error handling for single URL downloads."""

    @respx.mock
    def test_cli_handles_network_error(self, tmp_path):
        """Test CLI handles network errors gracefully."""
        url = "https://help.alteryx.com/current/en/designer/tools.html"

        respx.get(url).mock(side_effect=Exception("Connection refused"))

        result = runner.invoke(
            app,
            [url, "--output-dir", str(tmp_path)],
        )

        assert result.exit_code != 0
        assert "error" in result.stdout.lower() or "failed" in result.stdout.lower()

    def test_cli_handles_invalid_url(self, tmp_path):
        """Test CLI handles invalid URLs gracefully."""
        invalid_url = "not-a-valid-url"

        result = runner.invoke(
            app,
            [invalid_url, "--output-dir", str(tmp_path)],
        )

        assert result.exit_code != 0
        assert "error" in result.stdout.lower() or "invalid" in result.stdout.lower()

    @respx.mock
    def test_cli_skips_non_html_content(self, tmp_path):
        """Test CLI skips non-HTML content and reports it."""
        url = "https://help.alteryx.com/current/en/document.pdf"

        respx.get(url).mock(
            return_value=Response(
                status_code=200,
                headers={"content-type": "application/pdf"},
                content=b"%PDF-1.4 fake pdf",
            )
        )

        result = runner.invoke(
            app,
            [url, "--output-dir", str(tmp_path)],
        )

        # Should exit with non-zero (validation error)
        assert result.exit_code == 2
        assert "skipped" in result.stdout.lower() or "non-HTML" in result.stdout

    @respx.mock
    def test_cli_handles_404_error(self, tmp_path):
        """Test CLI handles 404 errors."""
        url = "https://help.alteryx.com/current/en/missing.html"

        respx.get(url).mock(
            return_value=Response(
                status_code=404,
                content=b"Not Found",
            )
        )

        result = runner.invoke(
            app,
            [url, "--output-dir", str(tmp_path)],
        )

        assert result.exit_code == 1
        assert "404" in result.stdout or "not found" in result.stdout.lower()


class TestCLIOptions:
    """Test CLI configuration options."""

    @respx.mock
    def test_cli_respects_max_file_size_option(self, tmp_path):
        """Test that --max-file-size option is respected."""
        url = "https://help.alteryx.com/current/en/designer/tools.html"
        large_content = b"x" * 1000  # 1KB

        respx.get(url).mock(
            return_value=Response(
                status_code=200,
                headers={"content-type": "text/html"},
                content=large_content,
            )
        )

        # Set max size to 500 bytes (should reject 1KB file)
        result = runner.invoke(
            app,
            [url, "--output-dir", str(tmp_path), "--max-file-size", "500"],
        )

        assert result.exit_code != 0
        assert "size" in result.stdout.lower()

    @respx.mock
    def test_cli_force_option_redownloads(self, tmp_path):
        """Test that --force option re-downloads existing files."""
        url = "https://help.alteryx.com/current/en/designer/tools.html"
        original_content = b"<html><body>original</body></html>"
        new_content = b"<html><body>updated</body></html>"

        # Create existing file
        file_path = tmp_path / "current" / "en" / "designer" / "tools.html"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(original_content)

        respx.get(url).mock(
            return_value=Response(
                status_code=200,
                headers={"content-type": "text/html"},
                content=new_content,
            )
        )

        result = runner.invoke(
            app,
            [url, "--output-dir", str(tmp_path), "--force"],
        )

        assert result.exit_code == 0
        # File should be updated with new content
        assert file_path.read_bytes() == new_content

    def test_cli_dry_run_mode(self, tmp_path):
        """Test that --dry-run mode doesn't actually download."""
        url = "https://help.alteryx.com/current/en/designer/tools.html"

        result = runner.invoke(
            app,
            [url, "--output-dir", str(tmp_path), "--dry-run"],
        )

        assert result.exit_code == 0
        assert "dry run" in result.stdout.lower() or "would download" in result.stdout.lower()

        # No files should be created
        downloaded_files = list(tmp_path.rglob("*.html"))
        assert len(downloaded_files) == 0


class TestCLILogging:
    """Test CLI logging and output."""

    @respx.mock
    def test_cli_logs_download_details(self, tmp_path):
        """Test that CLI logs download details per FR-017."""
        url = "https://help.alteryx.com/current/en/designer/tools.html"

        respx.get(url).mock(
            return_value=Response(
                status_code=200,
                headers={"content-type": "text/html"},
                content=b"<html><body>test</body></html>",
            )
        )

        result = runner.invoke(
            app,
            [url, "--output-dir", str(tmp_path)],
        )

        assert result.exit_code == 0
        # Should contain URL in output
        assert url in result.stdout or "tools.html" in result.stdout

    @respx.mock
    def test_cli_verbose_mode_shows_details(self, tmp_path):
        """Test that --verbose mode shows detailed output."""
        url = "https://help.alteryx.com/current/en/designer/tools.html"

        respx.get(url).mock(
            return_value=Response(
                status_code=200,
                headers={"content-type": "text/html"},
                content=b"<html><body>test</body></html>",
            )
        )

        result = runner.invoke(
            app,
            [url, "--output-dir", str(tmp_path), "--verbose"],
        )

        assert result.exit_code == 0
        # Verbose mode should show more details
        output_lower = result.stdout.lower()
        assert "download" in output_lower or "success" in output_lower


class TestCLIExitCodes:
    """Test CLI exit codes per FR-026."""

    @respx.mock
    def test_cli_exit_code_0_on_success(self, tmp_path):
        """Test exit code 0 for successful download."""
        url = "https://help.alteryx.com/current/en/designer/tools.html"

        respx.get(url).mock(
            return_value=Response(
                status_code=200,
                headers={"content-type": "text/html"},
                content=b"<html><body>test</body></html>",
            )
        )

        result = runner.invoke(
            app,
            [url, "--output-dir", str(tmp_path)],
        )

        assert result.exit_code == 0

    @respx.mock
    def test_cli_exit_code_1_on_download_failure(self, tmp_path):
        """Test exit code 1 for download failures."""
        url = "https://help.alteryx.com/current/en/designer/tools.html"

        respx.get(url).mock(return_value=Response(status_code=500, content=b"Server Error"))

        result = runner.invoke(
            app,
            [url, "--output-dir", str(tmp_path)],
        )

        assert result.exit_code == 1

    @respx.mock
    def test_cli_exit_code_2_on_validation_failure(self, tmp_path):
        """Test exit code 2 for validation failures (non-HTML)."""
        url = "https://help.alteryx.com/current/en/document.pdf"

        respx.get(url).mock(
            return_value=Response(
                status_code=200,
                headers={"content-type": "application/pdf"},
                content=b"%PDF",
            )
        )

        result = runner.invoke(
            app,
            [url, "--output-dir", str(tmp_path)],
        )

        assert result.exit_code == 2

    def test_cli_exit_code_3_on_configuration_error(self):
        """Test exit code 3 for configuration errors."""
        url = "https://help.alteryx.com/current/en/designer/tools.html"

        # Invalid output directory path (contains null byte)
        invalid_path = "/tmp/invalid\x00path"

        result = runner.invoke(
            app,
            [url, "--output-dir", invalid_path],
        )

        assert result.exit_code == 3


class TestCLIBatchMode:
    """Batch mode tests: file input, progress, continue on errors, summary (T030)."""

    def _fixtures_dir(self) -> Path:
        return Path(__file__).resolve().parents[1] / "fixtures" / "url_lists"

    @respx.mock
    def test_batch_cli_downloads_all_urls_success(self, tmp_path):
        """Given a file of 10 URLs, process sequentially and succeed."""
        batch_file = self._fixtures_dir() / "batch.txt"

        # Mock all help.alteryx.com GETs to return HTML
        pattern = re.compile(r"^https://help\.alteryx\.com/.*")
        respx.get(pattern).mock(
            return_value=Response(
                status_code=200,
                headers={"content-type": "text/html; charset=utf-8"},
                content=b"<html><body>ok</body></html>",
            )
        )

        result = runner.invoke(app, [str(batch_file), "--output-dir", str(tmp_path), "--quiet"])

        # Expect success
        assert result.exit_code == 0

        # Verify 10 HTML files were created
        downloaded_files = list(tmp_path.rglob("*.html"))
        assert len(downloaded_files) == 10

        # Summary presence (implementation should include a summary line)
        assert "summary" in result.stdout.lower() or "success" in result.stdout.lower()

    @respx.mock
    def test_batch_cli_ignores_comments_and_blanks(self, tmp_path):
        """batch_with_comments should yield same count as plain batch."""
        batch_plain = self._fixtures_dir() / "batch.txt"
        batch_comments = self._fixtures_dir() / "batch_with_comments.txt"

        pattern = re.compile(r"^https://help\.alteryx\.com/.*")
        respx.get(pattern).mock(
            return_value=Response(
                status_code=200,
                headers={"content-type": "text/html"},
                content=b"<html>ok</html>",
            )
        )

        res_plain = runner.invoke(app, [str(batch_plain), "--output-dir", str(tmp_path / "plain"), "--quiet"])
        res_comments = runner.invoke(
            app, [str(batch_comments), "--output-dir", str(tmp_path / "comments"), "--quiet"]
        )

        assert res_plain.exit_code == 0
        assert res_comments.exit_code == 0

        count_plain = len(list((tmp_path / "plain").rglob("*.html")))
        count_comments = len(list((tmp_path / "comments").rglob("*.html")))
        assert count_plain == 10
        assert count_comments == 10

    @respx.mock
    def test_batch_cli_continues_on_errors_and_reports_summary(self, tmp_path):
        """Mixed file: skip invalid and non-HTML; continue others; non-zero exit and summary printed."""
        mixed_file = self._fixtures_dir() / "mixed_urls.txt"

        # Default: assume HTML OK
        pattern = re.compile(r"^https://help\.alteryx\.com/.*")
        respx.get(pattern).mock(
            return_value=Response(
                status_code=200,
                headers={"content-type": "text/html"},
                content=b"<html>ok</html>",
            )
        )

        # Non-HTML endpoints
        respx.get("https://help.alteryx.com/assets/image.png").mock(
            return_value=Response(status_code=200, headers={"content-type": "image/png"}, content=b"\x89PNG")
        )
        respx.get("https://help.alteryx.com/downloads/file.pdf").mock(
            return_value=Response(status_code=200, headers={"content-type": "application/pdf"}, content=b"%PDF")
        )
        respx.get("https://help.alteryx.com/static/script.js").mock(
            return_value=Response(status_code=200, headers={"content-type": "application/javascript"}, content=b"console.log(1)")
        )

        result = runner.invoke(app, [str(mixed_file), "--output-dir", str(tmp_path), "--quiet"])

        # Expect non-zero due to validation failures (or download failures)
        assert result.exit_code != 0

        # Expect only HTML pages downloaded (5 from fixture: install, workflow, search, whitespace, final)
        downloaded_files = list(tmp_path.rglob("*.html"))
        assert len(downloaded_files) == 5

        # Summary should mention success/failed/skipped counts
        out = result.stdout.lower()
        assert ("summary" in out) or ("success" in out and ("failed" in out or "skipped" in out))
