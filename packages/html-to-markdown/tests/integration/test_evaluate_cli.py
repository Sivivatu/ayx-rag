from pathlib import Path

from html_to_markdown.cli import app
from typer.testing import CliRunner

runner = CliRunner()


def test_evaluate_cli_generates_reports(tmp_path: Path):
    # Prepare synthetic source + converted pair
    source_dir = tmp_path / "src"
    converted_dir = tmp_path / "md"
    source_dir.mkdir()
    converted_dir.mkdir()
    html = (
        "<html><body><h1>T</h1><h2>S</h2>"
        '<a href="/x">x</a>'
        "<table><tr><td>1</td></tr></table>"
        "<img src='a.png' alt='A'/>"
        "<pre><code>print('hi')</code></pre>"
        "</body></html>"
    )
    md = "# T\n## S\n[x](/x)\n| c1 |\n| --- |\n| 1 |\n![A](a.png)\n```python\nprint('hi')\n```\n"
    (source_dir / "doc.html").write_text(html, encoding="utf-8")
    (converted_dir / "doc.md").write_text(md, encoding="utf-8")

    out_base = tmp_path / "eval"
    result = runner.invoke(
        app,
        [
            "evaluate",
            "--source-dir",
            str(source_dir),
            "--converted-dir",
            str(converted_dir),
            "--out-base",
            str(out_base),
        ],
    )
    assert result.exit_code == 0, result.output
    # Check artifacts
    assert (out_base / "evaluation.json").exists()
    assert (out_base / "evaluation.csv").exists()
    assert (out_base / "evaluation.md").exists()
    data = (out_base / "evaluation.json").read_text(encoding="utf-8")
    assert "file_count" in data and "aggregate" in data


def test_evaluate_cli_with_timestamped_output(tmp_path: Path):
    """Should generate timestamped output files when flag is set."""
    source_dir = tmp_path / "src"
    converted_dir = tmp_path / "md"
    source_dir.mkdir()
    converted_dir.mkdir()
    html = "<html><body><h1>Test</h1></body></html>"
    md = "# Test\n"
    (source_dir / "doc.html").write_text(html, encoding="utf-8")
    (converted_dir / "doc.md").write_text(md, encoding="utf-8")

    out_base = tmp_path / "eval"
    result = runner.invoke(
        app,
        [
            "evaluate",
            "--source-dir",
            str(source_dir),
            "--converted-dir",
            str(converted_dir),
            "--out-base",
            str(out_base),
            "--timestamped",
        ],
    )
    assert result.exit_code == 0, result.output
    
    # Check for timestamped files (pattern: evaluation_YYYYMMDD_HHMMSS.*)
    json_files = list(out_base.glob("evaluation_*.json"))
    csv_files = list(out_base.glob("evaluation_*.csv"))
    md_files = list(out_base.glob("evaluation_*.md"))
    
    assert len(json_files) == 1, f"Expected 1 JSON file, found {len(json_files)}"
    assert len(csv_files) == 1, f"Expected 1 CSV file, found {len(csv_files)}"
    assert len(md_files) == 1, f"Expected 1 MD file, found {len(md_files)}"
