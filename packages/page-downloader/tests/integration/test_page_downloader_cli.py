"""Integration tests for page-downloader CLI interface - single URL and batch modes."""

import re
from pathlib import Path

import respx
from httpx import Response
from page_downloader.cli import app
from typer.testing import CliRunner

runner = CliRunner()


class TestSingleURLSuccess:
    """Test successful single URL downloads via CLI."""

    @respx.mock
    def test_download_single_url_success(self, tmp_path):
        url = "https://help.alteryx.com/current/en/designer/tools.html"
        html_content = b"<html><body><h1>Test Page</h1></body></html>"
        respx.get(url).mock(
            return_value=Response(
                status_code=200,
                headers={"content-type": "text/html; charset=utf-8"},
                content=html_content,
            )
        )
        result = runner.invoke(app, [url, "--output-dir", str(tmp_path)])
        assert result.exit_code == 0
        downloaded_files = list(tmp_path.rglob("*.html"))
        assert len(downloaded_files) == 1
        assert downloaded_files[0].read_bytes() == html_content

    @respx.mock
    def test_creates_nested_directory_structure(self, tmp_path):
        url = "https://help.alteryx.com/current/en/designer/tools.html"
        respx.get(url).mock(
            return_value=Response(
                status_code=200,
                headers={"content-type": "text/html"},
                content=b"<html><body>test</body></html>",
            )
        )
        result = runner.invoke(app, [url, "--output-dir", str(tmp_path)])
        assert result.exit_code == 0
        expected_path = tmp_path / "current" / "en" / "designer" / "tools.html"
        assert expected_path.exists()

    @respx.mock
    def test_uses_default_output_dir(self, tmp_path, monkeypatch):
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
        assert (tmp_path / "downloads").exists()


class TestSingleURLErrors:
    """Test error handling for single URL downloads."""

    @respx.mock
    def test_handles_network_error(self, tmp_path):
        url = "https://help.alteryx.com/current/en/designer/tools.html"
        respx.get(url).mock(side_effect=Exception("Connection refused"))
        result = runner.invoke(app, [url, "--output-dir", str(tmp_path)])
        assert result.exit_code != 0
        assert "error" in result.stdout.lower() or "failed" in result.stdout.lower()

    def test_handles_invalid_url(self, tmp_path):
        invalid_url = "not-a-valid-url"
        result = runner.invoke(app, [invalid_url, "--output-dir", str(tmp_path)])
        assert result.exit_code != 0
        assert "error" in result.stdout.lower() or "invalid" in result.stdout.lower()

    @respx.mock
    def test_skips_non_html_content(self, tmp_path):
        url = "https://help.alteryx.com/current/en/document.pdf"
        respx.get(url).mock(
            return_value=Response(
                status_code=200,
                headers={"content-type": "application/pdf"},
                content=b"%PDF-1.4 fake pdf",
            )
        )
        result = runner.invoke(app, [url, "--output-dir", str(tmp_path)])
        assert result.exit_code == 2
        assert "skipped" in result.stdout.lower() or "non-html" in result.stdout.lower()

    @respx.mock
    def test_handles_404_error(self, tmp_path):
        url = "https://help.alteryx.com/current/en/missing.html"
        respx.get(url).mock(return_value=Response(status_code=404, content=b"Not Found"))
        result = runner.invoke(app, [url, "--output-dir", str(tmp_path)])
        assert result.exit_code == 1
        assert "404" in result.stdout or "not found" in result.stdout.lower()


class TestOptions:
    """Test configuration options."""

    @respx.mock
    def test_respects_max_file_size_option(self, tmp_path):
        url = "https://help.alteryx.com/current/en/designer/tools.html"
        large_content = b"x" * 1000
        respx.get(url).mock(
            return_value=Response(
                status_code=200,
                headers={"content-type": "text/html"},
                content=large_content,
            )
        )
        result = runner.invoke(app, [url, "--output-dir", str(tmp_path), "--max-file-size", "500"])
        assert result.exit_code != 0
        assert "size" in result.stdout.lower()

    @respx.mock
    def test_force_option_redownloads(self, tmp_path):
        url = "https://help.alteryx.com/current/en/designer/tools.html"
        original_content = b"<html><body>original</body></html>"
        new_content = b"<html><body>updated</body></html>"
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
        result = runner.invoke(app, [url, "--output-dir", str(tmp_path), "--force"])
        assert result.exit_code == 0
        assert file_path.read_bytes() == new_content

    def test_dry_run_mode(self, tmp_path):
        url = "https://help.alteryx.com/current/en/designer/tools.html"
        result = runner.invoke(app, [url, "--output-dir", str(tmp_path), "--dry-run"])
        assert result.exit_code == 0
        assert "dry run" in result.stdout.lower() or "would download" in result.stdout.lower()
        assert len(list(tmp_path.rglob("*.html"))) == 0


class TestBatchMode:
    """Batch mode tests: file input, progress, errors, summary."""

    def _fixtures_dir(self) -> Path:
        return Path(__file__).resolve().parents[1] / "fixtures" / "url_lists"

    @respx.mock
    def test_batch_downloads_all_urls_success(self, tmp_path):
        batch_file = self._fixtures_dir() / "batch.txt"
        pattern = re.compile(r"^https://help\.alteryx\.com/.*")
        respx.get(pattern).mock(
            return_value=Response(
                status_code=200,
                headers={"content-type": "text/html; charset=utf-8"},
                content=b"<html><body>ok</body></html>",
            )
        )
        result = runner.invoke(app, [str(batch_file), "--output-dir", str(tmp_path), "--quiet"])
        assert result.exit_code == 0
        assert len(list(tmp_path.rglob("*.html"))) == 10

    @respx.mock
    def test_batch_ignores_comments_and_blanks(self, tmp_path):
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
        res_plain = runner.invoke(
            app, [str(batch_plain), "--output-dir", str(tmp_path / "plain"), "--quiet"]
        )
        res_comments = runner.invoke(
            app, [str(batch_comments), "--output-dir", str(tmp_path / "comments"), "--quiet"]
        )
        assert res_plain.exit_code == 0
        assert res_comments.exit_code == 0
        assert len(list((tmp_path / "plain").rglob("*.html"))) == 10
        assert len(list((tmp_path / "comments").rglob("*.html"))) == 10

    @respx.mock
    def test_batch_continues_on_errors_and_reports_summary(self, tmp_path):
        mixed_file = self._fixtures_dir() / "mixed_urls.txt"
        pattern = re.compile(r"^https://help\.alteryx\.com/.*")
        respx.get(pattern).mock(
            return_value=Response(
                status_code=200,
                headers={"content-type": "text/html"},
                content=b"<html>ok</html>",
            )
        )
        respx.get("https://help.alteryx.com/assets/image.png").mock(
            return_value=Response(
                status_code=200, headers={"content-type": "image/png"}, content=b"\x89PNG"
            )
        )
        respx.get("https://help.alteryx.com/downloads/file.pdf").mock(
            return_value=Response(
                status_code=200, headers={"content-type": "application/pdf"}, content=b"%PDF"
            )
        )
        respx.get("https://help.alteryx.com/static/script.js").mock(
            return_value=Response(
                status_code=200,
                headers={"content-type": "application/javascript"},
                content=b"console.log(1)",
            )
        )
        result = runner.invoke(app, [str(mixed_file), "--output-dir", str(tmp_path), "--quiet"])
        assert result.exit_code != 0
        assert len(list(tmp_path.rglob("*.html"))) == 5


class TestExitCodes:
    """Test exit codes per FR-026."""

    @respx.mock
    def test_exit_code_0_on_success(self, tmp_path):
        url = "https://help.alteryx.com/current/en/designer/tools.html"
        respx.get(url).mock(
            return_value=Response(
                status_code=200,
                headers={"content-type": "text/html"},
                content=b"<html><body>test</body></html>",
            )
        )
        result = runner.invoke(app, [url, "--output-dir", str(tmp_path)])
        assert result.exit_code == 0

    @respx.mock
    def test_exit_code_1_on_download_failure(self, tmp_path):
        url = "https://help.alteryx.com/current/en/designer/tools.html"
        respx.get(url).mock(return_value=Response(status_code=500, content=b"Server Error"))
        result = runner.invoke(app, [url, "--output-dir", str(tmp_path)])
        assert result.exit_code == 1

    @respx.mock
    def test_exit_code_2_on_validation_failure(self, tmp_path):
        url = "https://help.alteryx.com/current/en/document.pdf"
        respx.get(url).mock(
            return_value=Response(
                status_code=200,
                headers={"content-type": "application/pdf"},
                content=b"%PDF",
            )
        )
        result = runner.invoke(app, [url, "--output-dir", str(tmp_path)])
        assert result.exit_code == 2

    def test_exit_code_3_on_configuration_error(self):
        url = "https://help.alteryx.com/current/en/designer/tools.html"
        invalid_path = "/tmp/invalid\x00path"
        result = runner.invoke(app, [url, "--output-dir", invalid_path])
        assert result.exit_code == 3
