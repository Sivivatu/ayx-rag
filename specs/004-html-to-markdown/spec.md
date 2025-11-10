# Feature Specification: HTML to Markdown Conversion & Quality Evaluation

**Feature Branch**: `004-html-to-markdown`  
**Created**: 2025-11-10  
**Status**: Draft  
**Input**: User description: "Convert downloaded HTML files into Markdown suitable for LLMs. Research Docling vs alternatives to choose best approach."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Convert Single HTML File (Priority: P1)

An internal data engineer selects a previously downloaded help HTML file and runs a conversion command to produce a clean, semantically structured Markdown file containing headings, paragraphs, lists, tables, code blocks, links, and retained alt text for images (image binaries excluded) suitable for downstream chunking and embedding.

**Why this priority**: Establishes the minimal viable path from raw HTML to usable Markdown for RAG ingestion.

**Independent Test**: Provide a representative HTML file, run conversion, verify resulting Markdown against acceptance scenarios without any batch or evaluation features.

**Acceptance Scenarios**:
1. **Given** a valid help HTML file with headings and lists, **When** converted, **Then** Markdown preserves heading hierarchy (H1-H3 at least) and list numbering/bullets.
2. **Given** a file containing code blocks wrapped in `<pre><code>` tags, **When** converted, **Then** Markdown includes fenced code blocks with language if specified via class attribute.
3. **Given** a file containing internal cross-reference links, **When** converted, **Then** Markdown retains link text and relative/absolute URL correctly.
4. **Given** a file containing images with `alt` attributes, **When** converted, **Then** Markdown includes `![alt text](original-url)` or a placeholder if the image is a sprite.

### User Story 2 - Batch Conversion with Progress (Priority: P2)

An internal data engineer points the system at a directory tree of downloaded HTML help files and receives converted Markdown outputs with a progress indicator and summary report of successes/failures.

**Why this priority**: Enables scalable processing of the full documentation corpus.

**Independent Test**: Run batch conversion on a fixture directory with mixed valid/invalid HTML and verify per-file results and summary statistics.

**Acceptance Scenarios**:
1. **Given** a directory with N HTML files, **When** batch conversion runs, **Then** output directory contains N Markdown files (minus any invalid) with consistent naming (`original-name.md`).
2. **Given** at least one malformed HTML file, **When** batch conversion completes, **Then** summary report lists the file with an error classification and the process continues for others.
3. **Given** batch conversion of >50 files, **When** executed, **Then** a progress indicator (percentage or file count) updates at least every 1 second.

### User Story 3 - Quality Evaluation & Scoring (Priority: P3)

An internal reviewer runs an evaluation command that compares converted Markdown against heuristics (structure completeness, link preservation, heading fidelity, code block integrity) and produces a per-file score plus aggregated metrics.

**Why this priority**: Ensures objective measurement to choose/adjust conversion approach/library.

**Independent Test**: Feed a curated evaluation set with expected structural elements; verify generated scores match baseline thresholds.

**Acceptance Scenarios**:
1. **Given** a converted Markdown file missing a table present in source HTML, **When** evaluated, **Then** score reflects a penalty and table omission is flagged.
2. **Given** a file with all links preserved, **When** evaluated, **Then** link preservation metric reports 100%.
3. **Given** a file with heading depth reduced (e.g. H3 collapsed), **When** evaluated, **Then** heading fidelity metric < 100% with diagnostic note.

### User Story 4 - Comparative Library Research (Priority: P4)

An internal architect runs a research/report command generating a comparative matrix for candidate libraries (e.g., Docling, Readability-based extraction + Markdown renderer, Pandoc, html2text/markdownify variants, custom parser). The output is a decision document that selects exactly one library to implement in the package. No runtime strategy switching is required post-decision.

**Why this priority**: Enables an informed, pre-implementation selection to minimize rework and ensure quality.

**Independent Test**: Populate candidate list, execute report, verify output matrix includes required columns and scores and concludes with a single selected library.

### Edge Cases

- HTML with deeply nested lists (>5 levels) should flatten or preserve without infinite indentation.
- Missing `<title>` tag should default document title to first H1 or file name.
- Empty or script-heavy pages (content primarily JavaScript) should yield a warning and minimal Markdown stub.
- Duplicate IDs in headings should not create conflicting anchors in generated Markdown.
- Non-UTF-8 encodings should be detected and converted to UTF-8 with logging.
- Very large HTML (>2 MB) should process without memory exhaustion by streaming/parsing incrementally.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: MUST support conversion of individual HTML file to Markdown preserving headings (H1-H6), paragraphs, lists, tables, code blocks, links, and images (as references, not binary).
- **FR-002**: MUST ignore or strip script/style elements, inline event handlers, and tracking pixels.
- **FR-003**: MUST capture source metadata (original URL if embedded, file path, last modified timestamp) into a front-matter block (YAML or JSON) at top of Markdown.
- **FR-004**: MUST preserve relative vs absolute link distinction exactly as in source.
- **FR-005**: MUST convert `<table>` elements to Markdown pipe tables retaining header rows and cell text order.
- **FR-006**: MUST convert `<pre><code>` blocks to fenced code blocks; include language if class attribute matches common language identifiers.
- **FR-007**: MUST handle images by inserting Markdown image syntax with alt text; if missing alt text, insert placeholder `[image]` and flag in evaluation.
- **FR-008**: MUST batch process a directory recursively with ability to specify output directory and dry-run mode (list would-be conversions only).
- **FR-009**: MUST produce a machine-readable summary (JSON) after batch conversion with counts: total, converted, errors, average time per file.
- **FR-010**: MUST provide evaluation command computing per-file metrics: heading_fidelity %, link_preservation %, table_preservation %, code_block_integrity %, image_alt_coverage %.
- **FR-011**: MUST output an aggregated evaluation report (CSV and Markdown) with per-file metrics and overall averages.
- **FR-012**: MUST produce a comparative evaluation and select a single library prior to implementation; the package will implement only the chosen library (no runtime strategy switching). Include a shortlist of candidates in the research phase documentation.
- **FR-013**: MUST define default thresholds that trigger re-processing or manual review: Headings ≥ 95%, Links ≥ 98%, Tables ≥ 90%, Code ≥ 95%, Image Alt ≥ 90%. Files below any threshold are flagged for manual review; optional re-processing may be attempted with tuned parameters during research.
- **FR-014**: MUST handle tables using a hybrid approach: attempt Markdown pipe tables first; if row/col spans or complex cells are detected, fallback to embedded HTML for those tables to preserve fidelity.
- **FR-015**: MUST log warnings for omitted structural elements (e.g., unsupported SVG diagrams) without failing conversion.
- **FR-016**: MUST complete conversion of a standard-size help page (<200 KB HTML) within <=2 seconds on baseline environment.
- **FR-017**: MUST support exclusion patterns (glob) to skip certain files (e.g., release notes if not needed).
- **FR-018**: MUST ensure idempotency: re-running conversion on unchanged HTML produces identical Markdown output.
- **FR-019**: MUST provide a diff mode to compare two conversion results from different strategies for the same file (for research phase; not required in the final runtime CLI).
- **FR-020**: MUST record evaluation results for traceability in a `evaluation/` directory with timestamped filenames.

### Key Entities

- **SourceDocument**: Represents an input HTML file (attributes: path, size, modified_time, inferred_title).
- **ConvertedDocument**: Represents output Markdown (attributes: path, source_path, conversion_strategy, metrics_stub, front_matter).
- **ConversionStrategy**: Abstract descriptor of chosen library/approach (attributes: name, version, supports_tables, supports_code_lang, license).
- **EvaluationMetrics**: Numeric metrics per file (heading_fidelity, link_preservation, table_preservation, code_block_integrity, image_alt_coverage, overall_score, warnings_count).
- **EvaluationReport**: Aggregated collection of EvaluationMetrics plus metadata (timestamp, strategy_list, summary_stats).
- **ConversionConfig**: Configuration choices (strategy shortlist, thresholds, exclusion_patterns, front_matter_fields).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Heading fidelity ≥ 95% (correct hierarchy and count) across full corpus evaluation set.
- **SC-002**: Link preservation ≥ 98% (same URL and anchor text) on evaluation set of at least 500 pages.
- **SC-003**: Table preservation ≥ 90% (all tables converted without structural loss) for documents containing tables.
- **SC-004**: Code block integrity ≥ 95% (number of code blocks and language tags where available) vs source.
- **SC-005**: Image alt coverage ≥ 90% (images with alt text either preserved or flagged) on pages containing images.
- **SC-006**: Batch conversion throughput ≥ 25 pages/minute on baseline environment for average 100 KB pages.
- **SC-007**: Overall evaluation score (weighted composite) achieves ≥ 92/100 for chosen strategy.
- **SC-008**: Manual review required for <5% of pages (below thresholds) after initial run.
- **SC-009**: Re-run idempotency: hash of Markdown body unchanged for ≥ 99% of unchanged source pages.
- **SC-010**: Research comparison matrix includes at least 5 candidate strategies with ≥ 8 qualitative/quantitative attributes each.

## Assumptions

- Help site HTML is well-formed enough for standard parsing; catastrophic malformed HTML is rare (<1%).
- Interactive scripts provide no essential textual content; safe to strip.
- Complex tables with merged cells are uncommon; acceptable to approximate with repeated cells or fallback to HTML snippet.
- License compatibility considered (preference for permissive licenses).

## Dependencies

- Requires existing downloaded HTML files produced by `page-downloader` feature.
- Requires file system access for batch directories and output paths.

## Out of Scope

- Embedding generation, chunking, and vector store insertion (handled by later features).
- OCR of images or extraction from PDFs (only HTML).
- Multi-language normalization or translation.

## Risks

- Chosen library may have maintenance or performance limitations leading to future migration.
- Structural fidelity metrics may be costly to compute for very large documents.
- Edge HTML constructs (tables with row/col spans) may degrade Markdown readability if not clarified.

## Open Questions

None at this time.

## Glossary

- **Fidelity**: Degree to which Markdown preserves structure and content of source HTML.
- **Overall Score**: Weighted composite of key evaluation metrics.

