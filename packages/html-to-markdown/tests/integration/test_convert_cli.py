from pathlib import Path

from html_to_markdown.cli import app
from typer.testing import CliRunner

runner = CliRunner()


def test_convert_cli_smoke(tmp_path: Path):
    # Use small fixture prepared under package tests
    fixture = Path(__file__).parent.parent / "fixtures" / "sample.html"
    if not fixture.exists():
        # create a tiny sample to keep test resilient
        fixture.write_text("<html><body><h1>Hi</h1><p>World</p></body></html>", encoding="utf-8")
    out_dir = tmp_path / "out"
    result = runner.invoke(app, ["convert", str(fixture), "--out", str(out_dir)])
    assert result.exit_code == 0
    # Verify output file created
    out_file = out_dir / (fixture.stem + ".md")
    assert out_file.exists(), result.output
    content = out_file.read_text(encoding="utf-8")
    # Accept either bundled fixture content or fallback minimal content
    assert "World" in content
    assert ("Hi" in content) or ("Title" in content)


def test_convert_with_front_matter(tmp_path: Path):
    """Should generate markdown with YAML front matter."""
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
    <meta property="og:url" content="https://example.com/test" />
</head>
<body>
    <h1>Test Title</h1>
    <p>Test content.</p>
</body>
</html>"""

    input_file = tmp_path / "test.html"
    input_file.write_text(html, encoding="utf-8")
    out_dir = tmp_path / "out"

    result = runner.invoke(app, ["convert", str(input_file), "--out", str(out_dir)])

    assert result.exit_code == 0
    out_file = out_dir / "test.md"
    assert out_file.exists()

    content = out_file.read_text(encoding="utf-8")
    # Check for front matter
    assert content.startswith("---\n")
    assert "title: Test Title" in content
    assert "original_url: https://example.com/test" in content
    assert "strategy: markdownify" in content
    # Check for body content
    assert "# Test Title" in content
    assert "Test content" in content


def test_convert_with_tables(tmp_path: Path):
    """Should handle simple tables correctly."""
    html = """<!DOCTYPE html>
<html>
<body>
    <h1>Table Test</h1>
    <table>
        <tr><th>Column A</th><th>Column B</th></tr>
        <tr><td>Value 1</td><td>Value 2</td></tr>
    </table>
</body>
</html>"""

    input_file = tmp_path / "table.html"
    input_file.write_text(html, encoding="utf-8")
    out_dir = tmp_path / "out"

    result = runner.invoke(app, ["convert", str(input_file), "--out", str(out_dir)])

    assert result.exit_code == 0
    out_file = out_dir / "table.md"
    content = out_file.read_text(encoding="utf-8")

    # Should contain table content
    assert "Column A" in content
    assert "Value 1" in content


def test_convert_with_complex_table(tmp_path: Path):
    """Should convert complex tables (markdownify handles rowspan)."""
    html = """<!DOCTYPE html>
<html>
<body>
    <h1>Complex Table</h1>
    <table>
        <tr><th>A</th><th>B</th></tr>
        <tr><td rowspan="2">Merged</td><td>1</td></tr>
        <tr><td>2</td></tr>
    </table>
</body>
</html>"""

    input_file = tmp_path / "complex.html"
    input_file.write_text(html, encoding="utf-8")
    out_dir = tmp_path / "out"

    result = runner.invoke(app, ["convert", str(input_file), "--out", str(out_dir)])

    assert result.exit_code == 0
    out_file = out_dir / "complex.md"
    content = out_file.read_text(encoding="utf-8")

    # Markdownify converts the table to Markdown (may lose rowspan semantics)
    # Just verify table data is present
    assert "Merged" in content
    assert "|" in content  # Pipe table format


def test_convert_without_output_dir(tmp_path: Path):
    """Should output to stdout when no output directory specified."""
    html = "<h1>Test</h1><p>Content</p>"
    input_file = tmp_path / "test.html"
    input_file.write_text(html, encoding="utf-8")

    result = runner.invoke(app, ["convert", str(input_file)])

    assert result.exit_code == 0
    # Check stdout contains markdown
    assert "# Test" in result.stdout or "Test" in result.stdout
    assert "Content" in result.stdout


def test_convert_with_strategy_option(tmp_path: Path):
    """Should accept strategy option."""
    html = "<h1>Test</h1><p>Content</p>"
    input_file = tmp_path / "test.html"
    input_file.write_text(html, encoding="utf-8")
    out_dir = tmp_path / "out"

    result = runner.invoke(
        app, ["convert", str(input_file), "--out", str(out_dir), "--strategy", "markdownify"]
    )

    assert result.exit_code == 0
    assert "markdownify" in result.stdout


def test_convert_nonexistent_file(tmp_path: Path):
    """Should fail gracefully for nonexistent file."""
    result = runner.invoke(app, ["convert", str(tmp_path / "nonexistent.html")])

    # Just verify it exits with error code
    assert result.exit_code == 1
