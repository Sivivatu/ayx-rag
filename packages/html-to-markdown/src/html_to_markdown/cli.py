from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import typer

from .strategies.docling_adapter import DoclingStrategy
from .strategies.markdownify_adapter import MarkdownifyStrategy
from .strategies.pandoc_adapter import PandocStrategy
from .metrics import extract_html_stats, score_conversion
from .evaluator import evaluate as run_evaluation, DEFAULT_THRESHOLDS


StrategyType = type[Any]


def _all_strategy_classes() -> list[StrategyType]:
    # Order: fast/lightweight first, then external binary, then heavy lib
    return [
        MarkdownifyStrategy,
        PandocStrategy,
        DoclingStrategy,
    ]


def _get_strategy(name: str):
    for cls in _all_strategy_classes():
        if getattr(cls, "name", "") == name:
            return cls()
    raise typer.BadParameter(f"Unknown strategy '{name}'")

app = typer.Typer(name="html-to-markdown", help="Convert HTML to Markdown with evaluation tools")


@app.command("convert")
def convert(
    input_path: str = typer.Argument(..., help="Path to input HTML file"),
    output_dir: str | None = typer.Option(None, "--out", help="Output directory for Markdown"),
    strategy_name: str = typer.Option("markdownify", "--strategy", show_default=True, help="Conversion strategy"),
):
    """Convert a single HTML file to Markdown using selected strategy."""
    strategy = _get_strategy(strategy_name)
    if not strategy.available():
        raise typer.Exit(code=2)
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
    strategy_name: str = typer.Option("markdownify", "--strategy", show_default=True, help="Conversion strategy"),
):
    """Batch convert HTML files with simple timing using selected strategy."""
    strategy = _get_strategy(strategy_name)
    if not strategy.available():
        raise typer.Exit(code=2)
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
    source_dir: str = typer.Option(..., "--source-dir", help="Directory containing original HTML files"),
    converted_dir: str = typer.Option(..., "--converted-dir", help="Directory containing converted Markdown files"),
    out_base: str = typer.Option("evaluation", "--out-base", help="Directory to write evaluation artifacts (JSON/CSV/MD)"),
    heading_threshold: float = typer.Option(DEFAULT_THRESHOLDS["heading_fidelity"], "--thr-headings", help="Heading fidelity threshold"),
    link_threshold: float = typer.Option(DEFAULT_THRESHOLDS["link_preservation"], "--thr-links", help="Link preservation threshold"),
    table_threshold: float = typer.Option(DEFAULT_THRESHOLDS["table_preservation"], "--thr-tables", help="Table preservation threshold"),
    code_threshold: float = typer.Option(DEFAULT_THRESHOLDS["code_block_integrity"], "--thr-code", help="Code block integrity threshold"),
    image_threshold: float = typer.Option(DEFAULT_THRESHOLDS["image_alt_coverage"], "--thr-images", help="Image alt coverage threshold"),
):
    """Evaluate converted Markdown against original HTML and generate JSON/CSV/Markdown reports."""
    thresholds = {
        "heading_fidelity": heading_threshold,
        "link_preservation": link_threshold,
        "table_preservation": table_threshold,
        "code_block_integrity": code_threshold,
        "image_alt_coverage": image_threshold,
    }
    report = run_evaluation(Path(source_dir), Path(converted_dir), Path(out_base), thresholds)
    flagged = report.get("flagged_count", 0)
    total = report.get("file_count", 0)
    typer.echo(f"Evaluated {total} files. Flagged {flagged} below thresholds. Reports in {out_base}/")


@app.command("benchmark")
def benchmark(
    input_dir: str = typer.Argument(..., help="Directory containing representative HTML files"),
    strategy_name: str | None = typer.Option(None, "--strategy", help="Single strategy to benchmark; defaults to all"),
    json_out: str | None = typer.Option(None, "--json", help="Path to write JSON benchmark report"),
):
    """Run timing + fidelity benchmark for one or all strategies and optionally persist JSON."""
    classes = _all_strategy_classes() if strategy_name is None else [
        _get_strategy(strategy_name).__class__  # type: ignore[misc]
    ]
    files = list(Path(input_dir).rglob("*.html"))
    if not files:
        typer.echo("No HTML files found for benchmark.")
        raise typer.Exit(code=1)
    report: dict[str, Any] = {"total_files": len(files), "strategies": []}
    for cls in classes:
        strategy = cls()
        if not strategy.available():
            typer.echo(f"Strategy {strategy.name}: unavailable")
            report["strategies"].append({"name": strategy.name, "available": False})
            continue
        timings = []
        aggregated_scores: dict[str, list[float]] = {}
        for f in files:
            html = f.read_text(encoding="utf-8")
            stats = extract_html_stats(html)
            start = time.perf_counter()
            md = strategy.convert(html)
            elapsed_ms = (time.perf_counter() - start) * 1000
            timings.append(elapsed_ms)
            score = score_conversion(stats, md)
            for k, v in score.items():
                aggregated_scores.setdefault(k, []).append(v)
        avg = sum(timings) / len(timings)
        max_t = max(timings)
        # Aggregate metric means
        metric_means = {k: (sum(v) / len(v) if v else 0.0) for k, v in aggregated_scores.items()}
        overall = sum(metric_means.values()) / len(metric_means) if metric_means else 0.0
        typer.echo(
            f"Benchmark {strategy.name}: files={len(files)} avg={avg:.1f}ms max={max_t:.1f}ms overall={overall:.3f} version={strategy.version()}"
        )
        report["strategies"].append(
            {
                "name": strategy.name,
                "available": True,
                "version": strategy.version(),
                "avg_ms": avg,
                "max_ms": max_t,
                "metrics": metric_means,
                "overall": overall,
            }
        )
    if json_out:
        Path(json_out).write_text(json.dumps(report, indent=2), encoding="utf-8")
        typer.echo(f"Wrote benchmark JSON report to {json_out}")

@app.command("strategies")
def strategies():
    """List all known strategies with availability."""
    for cls in _all_strategy_classes():
        s = cls()
        typer.echo(
            f"{s.name}: available={s.available()} version={s.version()} tables={s.supports_tables()} code_lang={s.supports_code_lang()}"
        )
