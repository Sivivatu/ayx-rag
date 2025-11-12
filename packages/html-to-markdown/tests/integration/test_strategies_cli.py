from html_to_markdown.cli import app
from typer.testing import CliRunner

runner = CliRunner()


def test_strategies_cli_lists_known_strategies():
    result = runner.invoke(app, ["strategies"])  # no args
    assert result.exit_code == 0
    out = result.output
    # Should list each strategy by name regardless of availability
    assert "markdownify:" in out
    assert "pandoc:" in out
    assert "docling:" in out


def test_convert_cli_with_strategy_flag(tmp_path):
    html = "<html><body><h1>Hi</h1><p>World</p></body></html>"
    src = tmp_path / "in.html"
    src.write_text(html, encoding="utf-8")
    out_dir = tmp_path / "out"
    result = runner.invoke(
        app,
        [
            "convert",
            str(src),
            "--out",
            str(out_dir),
            "--strategy",
            "markdownify",
        ],
    )
    assert result.exit_code == 0
    out_file = out_dir / "in.md"
    assert out_file.exists(), result.output
    content = out_file.read_text(encoding="utf-8")
    assert "Hi" in content and "World" in content
