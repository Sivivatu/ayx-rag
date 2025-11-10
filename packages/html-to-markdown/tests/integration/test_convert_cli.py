from pathlib import Path
from typer.testing import CliRunner

from html_to_markdown.cli import app


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
