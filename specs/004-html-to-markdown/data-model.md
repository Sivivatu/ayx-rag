# Data Model: HTML to Markdown Conversion & Evaluation

## Entities

### SourceDocument
- `path`: absolute filesystem path to HTML file
- `size_bytes`: file size
- `modified_time`: last modified timestamp (filesystem)
- `original_url`: extracted from HTML comment/meta if present
- `inferred_title`: first H1 or file name
- `hash`: content hash (for idempotency checks)

### ConvertedDocument
- `path`: output Markdown path
- `source_path`: link to SourceDocument
- `strategy`: chosen conversion library name
- `converted_at`: timestamp
- `front_matter`: dict of metadata (source_path, original_url, last_modified, converted_at, strategy)
- `body_hash`: hash of Markdown body for idempotency

### ConversionConfig
- `thresholds`: dict with keys (headings, links, tables, code, images)
- `exclusions`: list of glob patterns
- `hybrid_tables`: boolean flag (true for fallback HTML)
- `language_map`: mapping of class patterns to language identifiers

### EvaluationMetrics
- `source_path`
- `heading_fidelity_pct`
- `link_preservation_pct`
- `table_preservation_pct`
- `code_block_integrity_pct`
- `image_alt_coverage_pct`
- `overall_score_pct`
- `warnings_count`
- `conversion_time_ms`

### EvaluationReport
- `generated_at`: timestamp
- `strategy`: evaluated strategy name
- `metrics`: list[EvaluationMetrics]
- `aggregate`: summary statistics (averages, counts)
- `threshold_failures`: list of source paths failing thresholds

### DiffResult (research phase only)
- `source_path`
- `strategy_a`
- `strategy_b`
- `added_lines`
- `removed_lines`
- `changed_sections`: list of structural element diffs (headings/code/tables)

## Relationships
- SourceDocument 1..1 → ConvertedDocument (after successful conversion)
- EvaluationReport 1..N EvaluationMetrics
- ConvertedDocument may have 0..1 EvaluationMetrics (if evaluation performed)
- DiffResult references 1 SourceDocument and 2 strategies

## Validation Rules
- Threshold values must be integers 0–100.
- Headings fidelity requires at least one H1.
- Table preservation computed only if tables exist; otherwise marked N/A and excluded from overall score weighting.
- Overall score calculation: weighted average (headings 0.2, links 0.25, tables 0.15, code 0.2, images 0.2) excluding N/A metrics with weight redistribution.
- Hybrid table fallback triggers warning entry in EvaluationMetrics if HTML embed used.
- Idempotency: body_hash must remain identical for unchanged SourceDocument hash.

## State Transitions
1. `Raw` (HTML only) → `Converted` (ConvertedDocument created)
2. `Converted` → `Evaluated` (EvaluationMetrics attached)
3. `Converted` → `Diffed` (DiffResult produced for research) [optional]

## Derived Data
- `overall_score_pct` computed at evaluation time.
- `threshold_failures` derived from individual metrics vs thresholds.

## Open Items
None.
