from __future__ import annotations

import csv
import json
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from .metrics import extract_html_stats, score_conversion

DEFAULT_THRESHOLDS = {
    "heading_fidelity": 0.95,
    "link_preservation": 0.98,
    "table_preservation": 0.90,
    "code_block_integrity": 0.95,
    "image_alt_coverage": 0.90,
}


@dataclass
class FileEvaluation:
    source_path: Path
    markdown_path: Path
    metrics: dict[str, float]
    overall: float
    failed_metrics: list[str]


def evaluate_pair(html_path: Path, md_path: Path, thresholds: dict[str, float]) -> FileEvaluation:
    html = html_path.read_text(encoding="utf-8")
    md = md_path.read_text(encoding="utf-8")
    stats = extract_html_stats(html)
    metrics = score_conversion(stats, md)
    overall = sum(metrics.values()) / len(metrics) if metrics else 0.0
    failed = [m for m, v in metrics.items() if v < thresholds.get(m, 0.0)]
    return FileEvaluation(
        source_path=html_path,
        markdown_path=md_path,
        metrics=metrics,
        overall=overall,
        failed_metrics=failed,
    )


def find_pairs(source_dir: Path, converted_dir: Path) -> Iterable[tuple[Path, Path]]:
    """Yield (html_path, md_path) pairs.

    Primary mapping preserves relative directory structure: foo/bar.html -> foo/bar.md.
    Fallback mapping supports flat outputs (legacy): bar.html -> bar.md at converted root.
    """
    for html_file in source_dir.rglob("*.html"):
        rel = html_file.relative_to(source_dir)
        md_candidate = (converted_dir / rel).with_suffix(".md")
        if md_candidate.exists():
            yield html_file, md_candidate
            continue
        flat_candidate = converted_dir / (html_file.stem + ".md")
        if flat_candidate.exists():
            yield html_file, flat_candidate


def aggregate(evals: list[FileEvaluation]) -> dict[str, Any]:
    if not evals:
        return {"count": 0}
    metric_names = list(evals[0].metrics.keys())
    agg: dict[str, Any] = {"count": len(evals), "metrics": {}, "overall_mean": 0.0}
    for name in metric_names:
        vals = [e.metrics[name] for e in evals]
        agg["metrics"][name] = sum(vals) / len(vals)
    agg["overall_mean"] = sum(e.overall for e in evals) / len(evals)
    return agg


def write_json(report_path: Path, data: dict[str, Any]) -> None:
    report_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def write_csv(csv_path: Path, evals: list[FileEvaluation]) -> None:
    fieldnames = (
        ["source_path", "markdown_path", "overall"]
        + list(evals[0].metrics.keys())
        + ["failed_metrics"]
        if evals
        else []
    )
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        if not evals:
            f.write("source_path,markdown_path,overall\n")
            return
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for e in evals:
            row = {
                "source_path": str(e.source_path),
                "markdown_path": str(e.markdown_path),
                "overall": f"{e.overall:.4f}",
                "failed_metrics": ";".join(e.failed_metrics),
            }
            for k, v in e.metrics.items():
                row[k] = f"{v:.4f}"
            writer.writerow(row)


def write_markdown(
    md_path: Path, evals: list[FileEvaluation], agg: dict[str, Any], thresholds: dict[str, float]
) -> None:
    lines = ["# Evaluation Report", "", f"Generated: {datetime.utcnow().isoformat()}Z", ""]
    if not evals:
        lines.append("No files evaluated.")
        md_path.write_text("\n".join(lines), encoding="utf-8")
        return
    lines.append("## Aggregated Metrics")
    for k, v in agg["metrics"].items():
        lines.append(f"- {k}: {v:.4f} (threshold {thresholds.get(k, 0):.2f})")
    lines.append(f"- overall_mean: {agg['overall_mean']:.4f}")
    flagged = [e for e in evals if e.failed_metrics]
    percent_flagged = (len(flagged) / len(evals)) * 100
    lines.append("")
    lines.append(f"Flagged files: {len(flagged)} ({percent_flagged:.2f}%)")
    lines.append("")
    lines.append("## Per-File Metrics")
    for e in evals[:50]:  # limit listing to 50 for brevity
        lines.append(f"### {e.markdown_path.name}")
        for k, v in e.metrics.items():
            lines.append(f"- {k}: {v:.4f}")
        lines.append(f"- overall: {e.overall:.4f}")
        if e.failed_metrics:
            lines.append(f"- failed_metrics: {', '.join(e.failed_metrics)}")
        lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")


def evaluate(
    source_dir: Path,
    converted_dir: Path,
    out_base: Path,
    thresholds: dict[str, float] | None = None,
) -> dict[str, Any]:
    thresholds = thresholds or DEFAULT_THRESHOLDS
    out_base.mkdir(parents=True, exist_ok=True)
    pairs = list(find_pairs(source_dir, converted_dir))
    evals = [evaluate_pair(h, m, thresholds) for h, m in pairs]
    agg = aggregate(evals)
    flagged = sum(1 for e in evals if e.failed_metrics)
    percent_flagged = (flagged / len(evals) * 100) if evals else 0.0
    report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "thresholds": thresholds,
        "file_count": len(evals),
        "flagged_count": flagged,
        "flagged_percent": percent_flagged,
        "aggregate": agg,
        "files": [
            {
                "source": str(e.source_path),
                "markdown": str(e.markdown_path),
                "metrics": e.metrics,
                "overall": e.overall,
                "failed_metrics": e.failed_metrics,
            }
            for e in evals
        ],
    }
    # Write artifacts
    json_path = out_base / "evaluation.json"
    md_path = out_base / "evaluation.md"
    csv_path = out_base / "evaluation.csv"
    write_json(json_path, report)
    write_markdown(md_path, evals, agg, thresholds)
    write_csv(csv_path, evals)
    return report
