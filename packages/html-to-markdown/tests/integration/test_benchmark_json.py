from pathlib import Path

from html_to_markdown.cli import app
from typer.testing import CliRunner

runner = CliRunner()


def test_benchmark_writes_json(tmp_path: Path):
    # Use fixtures folder containing small HTML
    input_dir = Path(__file__).parent.parent / "fixtures"
    json_out = tmp_path / "bench.json"
    result = runner.invoke(
        app,
        [
            "benchmark",
            str(input_dir),
            "--strategy",
            "markdownify",
            "--json",
            str(json_out),
        ],
    )
    assert result.exit_code == 0
    assert json_out.exists(), result.output
    data = json_out.read_text(encoding="utf-8")
    assert "strategies" in data and "total_files" in data
