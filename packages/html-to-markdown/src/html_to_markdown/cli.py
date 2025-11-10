from __future__ import annotations

import time
from pathlib import Path

import typer

from .strategies.markdownify_adapter import MarkdownifyStrategy

app = typer.Typer(name="html-to-markdown", help="Convert HTML to Markdown with evaluation tools")


@app.command("convert")
def convert(
    input_path: str = typer.Argument(..., help="Path to input HTML file"),
    output_dir: str | None = typer.Option(None, "--out", help="Output directory for Markdown"),
):
    """Convert a single HTML file to Markdown (markdownify stub)."""
    strategy = MarkdownifyStrategy()
    html = Path(input_path).read_text(encoding="utf-8")
    start = time.perf_counter()
    md = strategy.convert(html)
    duration = (time.perf_counter() - start) * 1000
    if output_dir:
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / (Path(input_path).stem + ".md")
        out_path.write_text(md, encoding="utf-8")
        typer.echo(f"Converted {input_path} -> {out_path} in {duration:.1f}ms using {strategy.name}")
    else:
        typer.echo(md)


@app.command("batch")
def batch(
    input_dir: str = typer.Argument(..., help="Directory of HTML files to convert recursively"),
    output_dir: str = typer.Option(..., "--out", help="Output directory for Markdown"),
    summary_path: str | None = typer.Option(None, "--summary", help="Path to write JSON summary"),
    resume: bool = typer.Option(False, "--resume", help="Resume from checkpoint if available"),
):
    """Batch convert HTML files with simple timing (markdownify stub)."""
    strategy = MarkdownifyStrategy()
    in_dir = Path(input_dir)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    html_files = list(in_dir.rglob("*.html"))
    total = len(html_files)
    if total == 0:
        typer.echo("No HTML files found.")
        raise typer.Exit(code=0)
    converted = 0
    t_start = time.perf_counter()
    for idx, f in enumerate(html_files, 1):
        html = f.read_text(encoding="utf-8")
        md = strategy.convert(html)
        out_path = out_dir / (f.stem + ".md")
        out_path.write_text(md, encoding="utf-8")
        converted += 1
        if idx % 10 == 0 or idx == total:
            elapsed = time.perf_counter() - t_start
            typer.echo(f"Progress: {idx}/{total} ({(idx/total)*100:.1f}%) elapsed={elapsed:.1f}s")
    duration = time.perf_counter() - t_start
    typer.echo(f"Batch complete: {converted}/{total} in {duration:.2f}s (strategy={strategy.name})")


@app.command("evaluate")
def evaluate(
    input_dir: str = typer.Argument(..., help="Directory of converted Markdown files"),
    report_path: str = typer.Option(..., "--report", help="Path to write evaluation report"),
):
    """Evaluate converted Markdown files (stub)."""
    typer.echo(f"[stub] Evaluate: {input_dir} -> report={report_path}")


@app.command("benchmark")
def benchmark(
    input_dir: str = typer.Argument(..., help="Directory containing representative HTML files"),
):
    """Run a lightweight benchmark on markdownify strategy (timing only)."""
    strategy = MarkdownifyStrategy()
    if not strategy.available():
        typer.echo("markdownify not available")
        raise typer.Exit(code=2)
    files = list(Path(input_dir).rglob("*.html"))
    if not files:
        typer.echo("No HTML files found for benchmark.")
        raise typer.Exit(code=1)
    timings = []
    for f in files:
        html = f.read_text(encoding="utf-8")
        start = time.perf_counter()
        _ = strategy.convert(html)
        elapsed_ms = (time.perf_counter() - start) * 1000
        timings.append(elapsed_ms)
    avg = sum(timings) / len(timings)
    max_t = max(timings)
    typer.echo(f"Benchmark markdownify: files={len(files)} avg={avg:.1f}ms max={max_t:.1f}ms")
