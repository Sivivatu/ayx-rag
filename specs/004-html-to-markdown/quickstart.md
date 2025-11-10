# Quickstart: HTML to Markdown Conversion (Planned)

## Installation (Workspace)
```bash
uv sync
```

## CLI Usage (Planned Commands)
```bash
uv run python main.py html-to-markdown convert path/to/file.html -o out/dir
uv run python main.py html-to-markdown batch downloads/current/en/server/ --out converted/ --summary summary.json
uv run python main.py html-to-markdown evaluate converted/ --report evaluation/report.json
uv run python main.py html-to-markdown diff path/to/file.html --strategy-a docling --strategy-b pandoc
```

## Front Matter Example
```yaml
---
source_path: downloads/current/en/server/install.html
original_url: https://help.alteryx.com/current/en/server/install.html
last_modified: 2025-11-01T12:00:00Z
converted_at: 2025-11-10T15:30:00Z
strategy: docling
---
```

## Evaluation Metrics (Example JSON Row)
```json
{
  "source_path": "downloads/.../install.html",
  "heading_fidelity_pct": 97.5,
  "link_preservation_pct": 100.0,
  "table_preservation_pct": 92.0,
  "code_block_integrity_pct": 95.0,
  "image_alt_coverage_pct": 93.0,
  "overall_score_pct": 95.8,
  "warnings_count": 1
}
```

## Workflow
1. Download HTML (existing page-downloader feature)
2. Convert single file (verify structure)
3. Batch convert corpus subset
4. Evaluate metrics & review threshold failures
5. Research diff (pre-selection only)
6. Remove unused strategies & finalize
7. Proceed to embedding pipeline (future feature)

## Next Steps After Planning
- Implement strategy adapter for Docling
- Create test fixtures & expected Markdown
- Build evaluation harness
