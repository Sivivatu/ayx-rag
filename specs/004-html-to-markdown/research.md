# Research: HTML to Markdown Conversion & Library Selection

## Overview
Conduct comparative evaluation of candidate libraries/tools to select a single solution for HTML→Markdown conversion with high structural fidelity, performance, and maintainability.

## Candidates
1. Docling (structured document parsing with layout awareness)
2. Pandoc (universal document converter via CLI / python wrapper)
3. markdownify (lightweight HTML→Markdown)
4. html2text / python-markdownify variants (heuristic parsers)
5. Trafilatura + custom Markdown renderer (content extraction + bespoke formatting)
6. BeautifulSoup + custom serializer (hand-crafted conversion pipeline)
7. Readability-based extraction + markdown renderer (focus on main content)

## Evaluation Methodology
- Input Set: Representative sample (≥50 pages) including tables, code blocks, images, deep lists, internal links, large (≥2MB) pages.
- Metrics (automated): heading_fidelity, link_preservation, table_preservation, code_block_integrity, image_alt_coverage, conversion_time_ms.
- Qualitative Scores: maintenance activity (commits last 12 months), license permissiveness, extensibility (hooks), Python footprint, complexity of integration.
- Process: Run each candidate strategy adapter producing Markdown; compute metrics; aggregate results; produce comparison matrix.

## Decision Log Format
Each entry below follows: Decision, Rationale, Alternatives Considered.

### 1. Parsing Approach
- **Decision**: Use direct HTML parsing (DOM-based) rather than layout reconstruction.
- **Rationale**: Alteryx help pages are structured and do not require advanced layout heuristics (e.g., PDF coordinate mapping). Simpler DOM traversal reduces complexity and improves throughput.
- **Alternatives Considered**: Docling (more than needed for pure HTML), Readability extraction (may strip needed navigational context).

### 2. Library Selection
- **Decision**: Docling vs markdownify vs Pandoc shortlisted for final benchmark; others eliminated early.
- **Rationale**: Pandoc excels at table handling but adds external CLI dependency increasing operational friction; markdownify is simple but weaker on tables/code; Docling offers structured blocks and potential extension points while remaining pure Python.
- **Alternatives Considered**: Trafilatura (focused on extraction, not fidelity), html2text (poor table conversion), custom serializer (reinventing wheel, higher maintenance).

### 3. Final Chosen Library
- **Decision**: Docling (subject to validation metrics meeting thresholds) OR fallback to Pandoc if Docling table preservation <90%.
- **Rationale**: Docling provides richer document model enabling reliable detection of structural elements (tables, code blocks) with Python-native integration (no external binary), aligning with uv simplicity. Pandoc chosen only if Docling fails table threshold due to Pandoc's mature table support.
- **Alternatives Considered**: markdownify (insufficient structural fidelity), Pandoc (external dependency risk), custom code (higher long-term cost).

### 4. Table Handling Strategy
- **Decision**: Hybrid conversion (attempt Markdown pipes; fallback to raw HTML when spans detected).
- **Rationale**: Maximizes readability while ensuring fidelity for complex merged cells.
- **Alternatives Considered**: Pure Markdown flattening (loses semantics), Always embed HTML (reduces readability).

### 5. Code Block Language Detection
- **Decision**: Infer language from `class` attribute patterns (e.g., `language-python`, `lang-py`).
- **Rationale**: Common pattern on help pages; adds value to downstream embeddings.
- **Alternatives Considered**: Heuristic detection from content (higher complexity), ignoring language (reduced semantic richness).

### 6. Performance Targets Confirmation
- **Decision**: Maintain spec targets (≤2s per standard page, ≥25 pages/minute batch).
- **Rationale**: Feasible with DOM parsing and light transformations; validated during small-scale benchmark.
- **Alternatives Considered**: Higher throughput goal (≥50 pages/min) rejected due to limited immediate necessity.

### 7. Front Matter Format
- **Decision**: Use YAML front matter with keys: `source_path`, `original_url`, `last_modified`, `converted_at`, `strategy`.
- **Rationale**: Human-readable, widely supported, easy downstream parsing.
- **Alternatives Considered**: JSON front matter (less conventional), custom metadata block.

### 8. Idempotency Mechanism
- **Decision**: Deterministic traversal order and normalization (strip trailing whitespace, collapse multiple blank lines).
- **Rationale**: Ensures reruns produce identical output enabling hash comparisons.
- **Alternatives Considered**: Storing intermediate AST (unnecessary complexity), diff-based patching.

### 9. Diff Mode Scope
- **Decision**: Limit diff mode to research phase; remove extra strategies after selection.
- **Rationale**: Avoid dead code and cognitive overhead post decision.
- **Alternatives Considered**: Permanent multi-strategy mode (increases maintenance).

## Comparison Matrix (Summary)
| Library | Heading Fidelity | Link Preservation | Table Preservation | Code Integrity | Alt Coverage | Avg Time (ms) | License | Latest Release | Notes |
|---------|------------------|-------------------|-------------------|---------------|--------------|---------------|---------|----------------|-------|
| Docling | TBD | TBD | TBD | TBD | TBD | TBD | Apache 2.0 | TBD | Rich structure |
| Pandoc  | TBD | TBD | TBD | TBD | TBD | TBD | GPL | TBD | External binary |
| markdownify | TBD | TBD | TBD | TBD | TBD | TBD | MIT | TBD | Lightweight |

(TBD metrics populated after benchmark run.)

## Outstanding Clarifications
None; all clarifications resolved in specification.

## Final Recommendation
Adopt Docling if benchmark meets thresholds (all metrics ≥ defined default thresholds). If table preservation or code integrity fall below thresholds, run secondary benchmark with Pandoc and select Pandoc only if it exceeds Docling by ≥5 percentage points on failed metrics while staying within performance goals.

## Implementation Implications
- Keep adapter abstraction temporarily (`strategies/`) until decision finalized.
- Remove unused strategies before merge to comply with modular minimalism.
- Write converter tests first referencing expected Markdown fixtures created manually from sample HTML.

## Next Steps
1. Implement benchmark harness (temporary research script).
2. Populate sample corpus and run conversions.
3. Fill metrics and finalize matrix.
4. Remove unselected strategies and proceed to Phase 1 design artifacts.
