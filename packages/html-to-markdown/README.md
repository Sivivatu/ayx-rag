# html-to-markdown (stub)

Convert Alteryx help HTML into clean, semantically-structured Markdown suitable for LLM ingestion, with batch processing and quality evaluation.

Status: scaffolded (Phase 1). Commands are stubbed; implementation will land after research and foundational tasks.

## Why a separate package?

- Follows the workspace pattern: each feature is an isolated package with its own tests.
- Registered as a nested Typer app under the main CLI (`app.add_typer(...)`) because it exposes multiple subcommands (`convert`, `batch`, `evaluate`).
- `typer` and `loguru` are provided at the root workspace (not repeated as package deps).

## Planned Capabilities

- Single-file conversion preserving headings, lists, links, images (alt), code blocks, and tables.
- Batch conversion with progress, exclusions, summary JSON, checkpoint/resume.
- Hybrid table handling: Markdown pipe tables first, fallback to HTML on complex spans.
- Evaluation with metrics (headings, links, tables, code, images), CSV/Markdown reports, and thresholds.
- Idempotency by deterministic normalization and hashing.

Key requirements and success criteria are defined in `specs/004-html-to-markdown/spec.md`.

## CLI Usage (planned)

These commands are registered under the root CLI. Run them via `uv run python main.py ...`.

```bash
# Convert a single HTML file → Markdown
uv run python main.py html-to-markdown convert downloads/current/en/server/install.html \
  --out converted/

# Batch convert a directory recursively with summary and resume
uv run python main.py html-to-markdown batch downloads/current/en/server/ \
  --out converted/ --summary evaluation/summary.json --resume

# Evaluate converted outputs and write reports
uv run python main.py html-to-markdown evaluate converted/ \
  --report evaluation/report.json

# Research-only (during selection phase): compare strategies
uv run python main.py html-to-markdown diff path/to/file.html \
  --strategy-a docling --strategy-b pandoc
```

Notes:
- `--resume` enables checkpointed batch runs (Principle IV: Incremental Processing).
- Performance targets are measured within the dev container baseline (Debian 13).

## Package Layout

```text
packages/html-to-markdown/
├── pyproject.toml
├── README.md               # This file
├── src/html_to_markdown/
│   ├── __init__.py         # Exports Typer app; logger disabled by default
│   └── cli.py              # Stub commands: convert, batch, evaluate
└── tests/
    ├── unit/
    └── integration/
```

## Implementation Roadmap (high level)

1. Research (Docling vs alternatives), benchmark, and select single library.
2. Foundational modules: models, config, I/O helpers, table handler.
3. Implement single-file conversion (MVP) with tests.
4. Add batch processing with progress, summary, and checkpoint/resume.
5. Add evaluation metrics, reports, and threshold gating.
6. Polish: docs, CHANGELOG, release notes.

See `specs/004-html-to-markdown/tasks.md` for the detailed task list.

## Development

```bash
# Sync workspace packages
uv sync

# Discover commands
uv run python main.py --help
uv run python main.py html-to-markdown --help
```

## Design Notes

- Nested CLI: Registered via `app.add_typer(...)` in `main.py` to support multiple subcommands while keeping the top-level CLI tidy.
- Dependencies: `typer` and `loguru` are declared at the workspace root; this package adds only the final chosen conversion library after research.
- Idempotency: Deterministic traversal and whitespace normalization ensure stable Markdown output.
- Table strategy: Prefer readable Markdown; fall back to embedded HTML for fidelity when spans are detected.
