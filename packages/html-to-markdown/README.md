# html-to-markdown

Convert Alteryx help HTML into clean, semantically-structured Markdown suitable for LLM ingestion, with batch processing, checkpoint/resume capability, and quality evaluation.

**Status**: ??? Complete - All three user stories implemented with 132 tests passing

## Features

### ??? Single-File Conversion (US1)
- **Structure Preservation**: Headings, lists, links, images (with alt text), code blocks, tables
- **YAML Front Matter**: Source URL, title, last modified timestamp
- **Code Language Detection**: Automatic inference from CSS classes (`language-python`, `lang-js`, etc.)
- **Hybrid Table Handling**: Markdown pipe tables for simple tables, HTML fallback for complex spans
- **Multiple Strategies**: Markdownify (default), Docling, Pandoc support
- **Performance**: <2s per standard page, <1s average

### ??? Batch Conversion (US2)
- **Directory Processing**: Recursive conversion with structure preservation
- **Progress Tracking**: Updates every 10 files with rate calculation (files/min)
- **Error Handling**: Continues processing after individual failures, tracks all errors
- **Summary JSON**: Complete audit trail with timing, rates, success/failure details
- **Checkpoint/Resume**: Automatic checkpoints every 10 files for long-running jobs
- **Custom Checkpoint Path**: `--checkpoint` flag for custom checkpoint locations
- **Exclusion Patterns**: Glob patterns to skip unwanted files/directories
- **Configuration Support**: External JSON config for thresholds and settings
- **Performance**: ???25 files/min throughput validated

### ??? Quality Evaluation (US3)
- **Comprehensive Metrics**: Heading fidelity, link preservation, table preservation, code block integrity, image alt coverage
- **Weighted Scoring**: Configurable weights with automatic normalization
- **Multiple Report Formats**: JSON (detailed), CSV (tabular), Markdown (human-readable)
- **Threshold Gating**: Customizable per-metric thresholds with failure flagging
- **Aggregate Statistics**: Overall mean scores and per-file breakdowns
- **Manual Review Calculation**: Percentage of files needing review (<5% target)
- **Timestamped Output**: Optional `--timestamped` flag for persistent history

## Installation

This package is part of the uv-ayx-rag workspace:

\`\`\`bash
# Sync workspace packages
uv sync
\`\`\`

## CLI Usage

All commands are accessible through the main CLI entry point:

### Convert Single File

\`\`\`bash
# Basic conversion with front matter
uv run python main.py html-to-markdown convert \\
  downloads/current/en/server/install.html \\
  --out converted/

# With specific strategy
uv run python main.py html-to-markdown convert \\
  input.html --out converted/ --strategy docling
\`\`\`

### Batch Convert Directory

\`\`\`bash
# Basic batch conversion
uv run python main.py html-to-markdown batch \\
  downloads/current/en/server/ \\
  --out converted/

# With all options
uv run python main.py html-to-markdown batch \\
  downloads/current/en/server/ \\
  --out converted/ \\
  --exclude "*/archive/*" "*/old/*" \\
  --config config.json \\
  --summary evaluation/summary.json \\
  --resume \\
  --checkpoint .checkpoints/batch.json

# Resume interrupted batch
uv run python main.py html-to-markdown batch \\
  downloads/current/en/server/ \\
  --out converted/ \\
  --resume
\`\`\`

### Evaluate Quality

\`\`\`bash
# Basic evaluation with default thresholds
uv run python main.py html-to-markdown evaluate \\
  --source-dir downloads/current/en/server/ \\
  --converted-dir converted/ \\
  --out-base evaluation/

# With custom thresholds and timestamped output
uv run python main.py html-to-markdown evaluate \\
  --source-dir downloads/current/en/server/ \\
  --converted-dir converted/ \\
  --out-base evaluation/ \\
  --thr-headings 0.98 \\
  --thr-links 0.99 \\
  --thr-tables 0.95 \\
  --timestamped
\`\`\`

### List Available Strategies

\`\`\`bash
uv run python main.py html-to-markdown strategies
\`\`\`

### Benchmark Strategies

\`\`\`bash
# Benchmark all strategies
uv run python main.py html-to-markdown benchmark \\
  downloads/current/en/server/ \\
  --json evaluation/benchmark.json

# Benchmark specific strategy
uv run python main.py html-to-markdown benchmark \\
  downloads/current/en/server/ \\
  --strategy markdownify
\`\`\`

## Configuration

### External Configuration File

Create a JSON configuration file for batch conversion settings:

\`\`\`json
{
  "thresholds": {
    "heading_fidelity": 0.95,
    "link_preservation": 0.98,
    "table_preservation": 0.90,
    "code_block_integrity": 0.95,
    "image_alt_coverage": 0.90
  },
  "exclusions": [
    "*/archive/*",
    "*/temp/*",
    "**/test_*.html"
  ],
  "hybrid_tables": true,
  "language_map": {
    "py": "python",
    "js": "javascript",
    "sh": "bash"
  }
}
\`\`\`

Use with `--config config.json` flag.

### Checkpoint/Resume

Batch processing automatically creates checkpoints every 10 files at `{output_dir}/.checkpoint.json`. To resume an interrupted batch:

\`\`\`bash
uv run python main.py html-to-markdown batch \\
  input/ --out output/ --resume
\`\`\`

The checkpoint tracks:
- Total files discovered
- Successfully processed files
- Failed files with error messages
- Processing timestamps

On successful completion, the checkpoint is automatically removed.

## Metrics & Scoring

### Evaluation Metrics

1. **Heading Fidelity** (weight: 0.25): Proportion of HTML headings preserved in Markdown
2. **Link Preservation** (weight: 0.25): Proportion of HTML links converted to Markdown
3. **Table Preservation** (weight: 0.20): Proportion of HTML tables converted to Markdown
4. **Code Block Integrity** (weight: 0.15): Proportion of code blocks preserved with fencing
5. **Image Alt Coverage** (weight: 0.15): Proportion of images with alt text preserved

### Weighted Overall Score

Overall score uses configurable weights (default shown above) with automatic normalization. Custom weights can be implemented by modifying `DEFAULT_WEIGHTS` in `metrics.py`.

### Default Thresholds

- Heading fidelity: 0.95
- Link preservation: 0.98
- Table preservation: 0.90
- Code block integrity: 0.95
- Image alt coverage: 0.90

Files falling below thresholds are flagged for manual review.

## Package Architecture

\`\`\`text
packages/html-to-markdown/
????????? pyproject.toml
????????? README.md               # This file
????????? src/html_to_markdown/
???   ????????? __init__.py         # Exports Typer app
???   ????????? cli.py              # CLI commands (convert, batch, evaluate, benchmark, strategies)
???   ????????? converter.py        # Core HTML???Markdown conversion logic
???   ????????? evaluator.py        # Quality evaluation and report generation
???   ????????? metrics.py          # Metric computation and weighted scoring
???   ????????? checkpoint.py       # Checkpoint persistence for batch resume
???   ????????? config.py           # Configuration loading and validation
???   ????????? models.py           # Dataclasses (SourceDocument, ConvertedDocument, etc.)
???   ????????? io_utils.py         # File discovery, I/O helpers, path mapping
???   ????????? table_handler.py    # Hybrid table conversion (Markdown/HTML)
???   ????????? strategies/         # Conversion strategy adapters
???       ????????? base.py         # Strategy interface
???       ????????? markdownify_adapter.py  # Markdownify (default)
???       ????????? docling_adapter.py      # Docling
???       ????????? pandoc_adapter.py       # Pandoc (via pypandoc)
????????? tests/
    ????????? unit/               # 94 unit tests
    ???   ????????? test_checkpoint.py
    ???   ????????? test_config.py
    ???   ????????? test_converter.py
    ???   ????????? test_io_utils.py
    ???   ????????? test_metrics.py
    ???   ????????? test_models.py
    ???   ????????? test_table_handler.py
    ????????? integration/        # 38 integration tests
    ???   ????????? test_batch_cli.py
    ???   ????????? test_convert_cli.py
    ???   ????????? test_evaluate_cli.py
    ???   ????????? test_performance.py
    ???   ????????? test_strategies_cli.py
    ????????? fixtures/           # Test data (HTML samples, expected Markdown)
\`\`\`

## Testing

\`\`\`bash
# Run all tests
cd packages/html-to-markdown
uv run pytest

# Run with coverage
uv run pytest --cov=html_to_markdown --cov-report=term-missing

# Run specific test category
uv run pytest tests/unit/
uv run pytest tests/integration/
uv run pytest tests/integration/test_batch_cli.py -v
\`\`\`

**Test Coverage**: 132 tests passing
- 94 unit tests (checkpoint, config, converter, I/O, metrics, models, tables)
- 38 integration tests (CLI workflows, performance validation)
- Performance tests validate <2s single file, ???25 files/min batch

## Design Decisions

### Nested CLI Architecture
Registered via `app.add_typer(...)` in `main.py` to support multiple subcommands while keeping the top-level CLI organized.

### Strategy Pattern
Multiple conversion libraries supported through adapter interface:
- **Markdownify**: Default (lightweight, 100% fidelity on benchmarks, 28ms avg)
- **Docling**: Advanced document understanding, useful for complex layouts
- **Pandoc**: Industry standard, mature conversion library

### Hybrid Table Handling
- Simple tables ??? Markdown pipe tables (readable, version control friendly)
- Complex tables (rowspan/colspan) ??? Embedded HTML (preserves fidelity)
- Configurable complexity threshold

### Checkpoint-Based Resume
- JSON-based state persistence for batch operations
- Tracks processed files, failures, timestamps
- Enables resumption of multi-hour batch jobs
- Automatic cleanup on successful completion

### Weighted Scoring
- Configurable metric weights reflecting importance
- Automatic normalization ensures weights sum to 1.0
- More sophisticated than simple averaging

## Performance Characteristics

- **Single file**: <2s per standard page (<200KB), <1s average
- **Batch throughput**: ???25 files/min validated with 30-file test
- **Memory efficiency**: Streaming parse for large HTML files
- **Progress updates**: Every 10 files with rate calculation
- **Checkpoint frequency**: Every 10 files during batch processing

## Development Notes

### Adding a New Strategy

1. Create adapter in `strategies/` implementing `StrategyInterface`
2. Add to `_all_strategy_classes()` in `cli.py`
3. Add unit tests for availability and conversion
4. Document in benchmark results

### Extending Metrics

1. Add extraction logic to `extract_html_stats()` in `metrics.py`
2. Add scoring logic to `score_conversion()` in `metrics.py`
3. Update `DEFAULT_WEIGHTS` and `DEFAULT_THRESHOLDS`
4. Add unit tests in `test_metrics.py`

## Future Enhancements

Deferred tasks (can be implemented anytime):
- **T041-T042**: Idempotency with deterministic normalization and body hashing
- **T055**: Encoding detection and normalization to UTF-8
- **T056**: Warning logging for omitted/unsupported elements (SVG, complex diagrams)
- **T039**: Additional edge case tests (deeply nested lists, very large HTML)

See `specs/004-html-to-markdown/tasks.md` for complete task tracking.

## References

- **Specification**: `specs/004-html-to-markdown/spec.md`
- **Implementation Plan**: `specs/004-html-to-markdown/plan.md`
- **Research & Benchmarks**: `specs/004-html-to-markdown/research.md`
- **Tasks**: `specs/004-html-to-markdown/tasks.md`
