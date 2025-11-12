from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import typer

# Import new converter
from .converter import HtmlConverter
from .evaluator import DEFAULT_THRESHOLDS
from .evaluator import evaluate as run_evaluation
from .metrics import extract_html_stats, score_conversion
from .strategies.docling_adapter import DoclingStrategy
from .strategies.markdownify_adapter import MarkdownifyStrategy

StrategyType = type[Any]


def _all_strategy_classes() -> list[StrategyType]:
    # Order: fast/lightweight first, then heavy lib
    return [
        MarkdownifyStrategy,
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
    strategy_name: str = typer.Option(
        "markdownify", "--strategy", show_default=True, help="Conversion strategy"
    ),
    config_file: str | None = typer.Option(None, "--config", help="Path to configuration JSON"),
):
    """Convert a single HTML file to Markdown with front matter and metadata."""
    from .config import load_config

    # Load configuration
    config = load_config(Path(config_file) if config_file else None)

    # Get strategy and create converter
    strategy = _get_strategy(strategy_name)
    if not strategy.available():
        typer.echo(f"Strategy '{strategy_name}' is not available", err=True)
        raise typer.Exit(code=2)

    converter = HtmlConverter(strategy=strategy, config=config)

    # Convert file
    input_file = Path(input_path)
    if not input_file.exists():
        typer.echo(f"Input file not found: {input_path}", err=True)
        raise typer.Exit(code=1)

    start = time.perf_counter()

    if output_dir:
        out_dir = Path(output_dir)
        result = converter.convert_file(input_file, out_dir / input_file.with_suffix(".md").name)
        duration = (time.perf_counter() - start) * 1000
        typer.echo(
            f"Converted {input_path} -> {result.path} in {duration:.1f}ms using {strategy.name}"
        )
        typer.echo(f"Title: {result.front_matter.get('title', 'N/A')}")
        if result.front_matter.get("original_url"):
            typer.echo(f"URL: {result.front_matter['original_url']}")
    else:
        result = converter.convert_file(input_file, None)
        duration = (time.perf_counter() - start) * 1000
        typer.echo(result.markdown_content)
        typer.echo(f"\n# Converted in {duration:.1f}ms using {strategy.name}", err=True)


@app.command("batch")
def batch(
    input_dir: str = typer.Argument(..., help="Directory of HTML files to convert recursively"),
    output_dir: str = typer.Option(..., "--out", help="Output directory for Markdown"),
    summary_path: str | None = typer.Option(None, "--summary", help="Path to write JSON summary"),
    resume: bool = typer.Option(False, "--resume", help="Resume from checkpoint if available"),
    checkpoint_path: str | None = typer.Option(
        None, "--checkpoint", help="Path to checkpoint file (default: output_dir/.checkpoint.json)"
    ),
    strategy_name: str = typer.Option(
        "markdownify", "--strategy", show_default=True, help="Conversion strategy"
    ),
    config_file: str | None = typer.Option(None, "--config", help="Path to configuration JSON"),
    exclusions: str | None = typer.Option(
        None, "--exclude", help="Comma-separated glob patterns to exclude"
    ),
):
    """Batch convert HTML files with progress tracking, error handling, and resume capability."""
    from .checkpoint import Checkpoint
    from .config import load_config
    from .io_utils import discover_html_files

    # Load configuration
    config = load_config(Path(config_file) if config_file else None)

    # Get strategy and create converter
    strategy = _get_strategy(strategy_name)
    if not strategy.available():
        typer.echo(f"Strategy '{strategy_name}' is not available", err=True)
        raise typer.Exit(code=2)

    converter = HtmlConverter(strategy=strategy, config=config)

    # Parse exclusion patterns
    exclusion_patterns = exclusions.split(",") if exclusions else []

    # Setup directories
    in_dir = Path(input_dir)
    out_dir = Path(output_dir)

    if not in_dir.exists():
        typer.echo(f"Input directory not found: {input_dir}", err=True)
        raise typer.Exit(code=1)

    out_dir.mkdir(parents=True, exist_ok=True)

    # Setup checkpoint path
    if checkpoint_path:
        chkpt_file = Path(checkpoint_path)
    else:
        chkpt_file = out_dir / ".checkpoint.json"

    # Discover HTML files
    html_files = list(discover_html_files(in_dir, exclusion_patterns))
    total = len(html_files)

    if total == 0:
        typer.echo("No HTML files found.")
        raise typer.Exit(code=0)

    # Convert to relative paths for checkpoint tracking
    file_paths = [str(f.relative_to(in_dir)) for f in html_files]

    # Load or create checkpoint
    checkpoint = None
    files_to_process = html_files

    if resume and chkpt_file.exists():
        checkpoint = Checkpoint.load(chkpt_file)
        if checkpoint:
            typer.echo(f"Resuming from checkpoint: {chkpt_file}")
            typer.echo(f"Previously processed: {checkpoint.processed_count}/{checkpoint.total_files}")
            typer.echo(f"Started at: {checkpoint.started_at}")
            typer.echo(f"Last updated: {checkpoint.last_updated}")
            typer.echo("")

            # Filter to only unprocessed files
            remaining_paths = checkpoint.get_remaining_files(file_paths)
            files_to_process = [
                html_files[file_paths.index(p)] for p in remaining_paths
            ]
            typer.echo(f"Remaining files to process: {len(files_to_process)}")
        else:
            typer.echo(f"Warning: Could not load checkpoint from {chkpt_file}", err=True)
            typer.echo("Starting fresh conversion")

    if checkpoint is None:
        checkpoint = Checkpoint.create_new(total)

    # Initialize counters
    converted = checkpoint.processed_count
    failed = len(checkpoint.failed_files)
    errors = [
        {"file": f.file_path, "error": f.error, "type": "Error"}
        for f in checkpoint.failed_files
    ]
    t_start = time.perf_counter()

    typer.echo(f"Starting batch conversion...")
    typer.echo(f"Strategy: {strategy_name}")
    typer.echo(f"Input: {in_dir}")
    typer.echo(f"Output: {out_dir}")
    typer.echo(f"Total files: {total}")
    typer.echo(f"Files to process: {len(files_to_process)}")
    typer.echo("")

    # Process files with progress updates
    for idx, html_file in enumerate(files_to_process, 1):
        rel_path = str(html_file.relative_to(in_dir))

        try:
            # Calculate output path maintaining directory structure
            out_path = (out_dir / Path(rel_path)).with_suffix(".md")

            # Convert file
            result = converter.convert_file(html_file, out_path)
            converted += 1

            # Update checkpoint
            checkpoint.mark_processed(rel_path, success=True)

        except Exception as e:
            failed += 1
            error_info = {
                "file": rel_path,
                "error": str(e),
                "type": type(e).__name__,
            }
            errors.append(error_info)

            # Update checkpoint with failure
            checkpoint.mark_processed(rel_path, success=False, error=str(e))

            typer.echo(f"ERROR: {html_file.name}: {e}", err=True)

        # Save checkpoint every 10 files or at completion
        if idx % 10 == 0 or idx == len(files_to_process):
            checkpoint.save(chkpt_file)

        # Progress update
        if idx % 10 == 0 or idx == len(files_to_process):
            elapsed = time.perf_counter() - t_start
            rate = idx / elapsed if elapsed > 0 else 0
            overall_progress = checkpoint.processed_count
            typer.echo(
                f"Progress: {overall_progress}/{total} ({(overall_progress / total) * 100:.1f}%) | "
                f"Converted: {converted} | Failed: {failed} | "
                f"Rate: {rate:.1f} files/s | Elapsed: {elapsed:.1f}s"
            )

    # Final timing
    duration = time.perf_counter() - t_start
    rate = len(files_to_process) / duration if duration > 0 else 0

    typer.echo("")
    typer.echo("=" * 60)
    typer.echo("Batch Conversion Complete")
    typer.echo("=" * 60)
    typer.echo(f"Total files: {total}")
    typer.echo(f"Converted: {converted}")
    typer.echo(f"Failed: {failed}")
    typer.echo(f"Duration: {duration:.2f}s")
    typer.echo(f"Rate: {rate:.2f} files/s ({rate * 60:.1f} files/min)")
    typer.echo(f"Strategy: {strategy_name}")

    # Clean up checkpoint on successful completion
    if failed == 0 and chkpt_file.exists():
        chkpt_file.unlink()
        typer.echo(f"\nCheckpoint removed (all files processed successfully)")

    # Generate summary JSON if requested
    if summary_path:
        summary = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "input_dir": str(in_dir),
            "output_dir": str(out_dir),
            "strategy": strategy_name,
            "total_files": total,
            "converted": converted,
            "failed": failed,
            "duration_seconds": round(duration, 2),
            "rate_files_per_second": round(rate, 2),
            "rate_files_per_minute": round(rate * 60, 1),
            "resumed_from_checkpoint": resume and checkpoint.processed_count > len(files_to_process),
            "errors": errors,
        }

        summary_file = Path(summary_path)
        summary_file.parent.mkdir(parents=True, exist_ok=True)
        summary_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        typer.echo(f"\nSummary written to: {summary_path}")

    # Exit with error code if any failures
    if failed > 0:
        typer.echo(f"\nWarning: {failed} file(s) failed to convert", err=True)
        typer.echo(f"Checkpoint saved to: {chkpt_file} (use --resume to retry)", err=True)
        raise typer.Exit(code=1)


@app.command("evaluate")
def evaluate(
    source_dir: str = typer.Option(
        ..., "--source-dir", help="Directory containing original HTML files"
    ),
    converted_dir: str = typer.Option(
        ..., "--converted-dir", help="Directory containing converted Markdown files"
    ),
    out_base: str = typer.Option(
        "evaluation", "--out-base", help="Directory to write evaluation artifacts (JSON/CSV/MD)"
    ),
    timestamped: bool = typer.Option(
        False, "--timestamped", help="Add timestamp suffix to output filenames"
    ),
    heading_threshold: float = typer.Option(
        DEFAULT_THRESHOLDS["heading_fidelity"], "--thr-headings", help="Heading fidelity threshold"
    ),
    link_threshold: float = typer.Option(
        DEFAULT_THRESHOLDS["link_preservation"], "--thr-links", help="Link preservation threshold"
    ),
    table_threshold: float = typer.Option(
        DEFAULT_THRESHOLDS["table_preservation"],
        "--thr-tables",
        help="Table preservation threshold",
    ),
    code_threshold: float = typer.Option(
        DEFAULT_THRESHOLDS["code_block_integrity"],
        "--thr-code",
        help="Code block integrity threshold",
    ),
    image_threshold: float = typer.Option(
        DEFAULT_THRESHOLDS["image_alt_coverage"],
        "--thr-images",
        help="Image alt coverage threshold",
    ),
):
    """Evaluate converted Markdown against original HTML and generate JSON/CSV/Markdown reports."""
    thresholds = {
        "heading_fidelity": heading_threshold,
        "link_preservation": link_threshold,
        "table_preservation": table_threshold,
        "code_block_integrity": code_threshold,
        "image_alt_coverage": image_threshold,
    }
    report = run_evaluation(
        Path(source_dir), Path(converted_dir), Path(out_base), thresholds, timestamped
    )
    flagged = report.get("flagged_count", 0)
    total = report.get("file_count", 0)
    typer.echo(
        f"Evaluated {total} files. Flagged {flagged} below thresholds. Reports in {out_base}/"
    )


@app.command("benchmark")
def benchmark(
    input_dir: str = typer.Argument(..., help="Directory containing representative HTML files"),
    strategy_name: str | None = typer.Option(
        None, "--strategy", help="Single strategy to benchmark; defaults to all"
    ),
    json_out: str | None = typer.Option(None, "--json", help="Path to write JSON benchmark report"),
):
    """Run timing + fidelity benchmark for one or all strategies and optionally persist JSON."""
    classes = (
        _all_strategy_classes()
        if strategy_name is None
        else [
            _get_strategy(strategy_name).__class__  # type: ignore[misc]
        ]
    )
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
