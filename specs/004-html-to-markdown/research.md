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

- **Decision**: **Markdownify** selected as the final conversion library.
- **Rationale**: 
  - **Highest overall score** (0.838 vs 0.477 for Pandoc, 0.566 for Docling)
  - **Perfect link preservation** (1.000) - critical for help documentation with extensive internal linking
  - **Perfect table preservation** (1.000) and image alt coverage (1.000)
  - **15.7x faster than Pandoc**, 5.7x faster than Docling (28.3ms avg vs 444.6ms and 162.4ms)
  - **Zero external dependencies** - pure Python, no CLI tools or ML models required
  - **MIT license** - most permissive, no GPL restrictions
  - **Simple integration** - straightforward API, minimal configuration
  - **Meets all performance targets** with huge margin (28ms << 2000ms spec)
- **Benchmark Results**: Markdownify achieved 90.5% heading fidelity, 100% link preservation, 100% table preservation, 100% image alt coverage, and 28.6% code integrity across 7 real Alteryx help pages.
- **Trade-offs Accepted**: Slightly lower heading fidelity (90.5% vs 100%) and code block language detection (28.6%) are acceptable given overwhelming advantages in speed, simplicity, and critical metrics (links, tables, images).
- **Alternatives Considered**: 
  - Pandoc rejected due to poor link preservation (38.6%), 15.7x slower performance, GPL license, and external binary dependency
  - Docling rejected due to poor link preservation (46.5%), 5.7x slower performance, heavy ML dependencies, and unnecessary complexity for HTML conversion

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

**Benchmark Date**: 2025-11-11  
**Test Corpus**: 7 Alteryx help pages from `downloads/current/en/server/`  
**Environment**: Python 3.14.0, Debian Trixie

| Metric | Markdownify | Pandoc | Docling | Winner |
|--------|-------------|--------|---------|--------|
| Heading Fidelity | 0.905 | 1.000 | 1.000 | pandoc/docling |
| Link Preservation | 1.000 | 0.386 | 0.465 | **markdownify** |
| Table Preservation | 1.000 | 0.714 | 1.000 | markdownify/docling |
| Image Alt Coverage | 1.000 | 0.000 | 0.000 | **markdownify** |
| Code Block Integrity | 0.286 | 0.286 | 0.367 | docling |
| **Overall Score** | **0.838** | 0.477 | 0.566 | **markdownify** |

| Performance | Markdownify | Pandoc | Docling | Winner |
|-------------|-------------|--------|---------|--------|
| Avg Time (ms) | **28.3** | 444.6 | 162.4 | **markdownify** |
| Max Time (ms) | **54.2** | 836.1 | 608.0 | **markdownify** |

| Library | License | Latest Release | Dependencies | Notes |
|---------|---------|----------------|--------------|-------|
| markdownify | MIT | 0.13.0+ | Pure Python | Lightweight, excellent link/table/image handling |
| Pandoc | GPL | 3.1.11.1 | External CLI binary | Requires system installation, GPL licensing |
| Docling | Apache 2.0 | 2.61.2 | Heavy (ML models) | Layout-aware, slow initialization, complex |

### Key Findings

1. **Markdownify Dominates**: Highest overall score (0.838), 15.7x faster than Pandoc, 5.7x faster than Docling
2. **Link Preservation Critical**: Markdownify achieves 100% link preservation vs 38.6% (Pandoc) and 46.5% (Docling)
3. **Table Handling**: Markdownify and Docling both achieve 100% table preservation
4. **Performance**: Markdownify avg 28.3ms meets spec target (≤2000ms) with huge margin
5. **Simplicity**: Markdownify is pure Python with no external dependencies or ML models
6. **Code Blocks**: All three struggle with code language detection (28-37% integrity)

### Analysis

**Markdownify Strengths**:
- Excellent structural fidelity for HTML→Markdown (90.5-100% on 4/5 metrics)
- Blazing fast performance (28ms avg, 54ms max)
- Zero external dependencies (pure Python)
- MIT license (permissive)
- Proven reliability on Alteryx help pages
- Simple integration and maintenance

**Pandoc Weaknesses**:
- Very poor link preservation (38.6%) - critical failure for help documentation
- 15.7x slower than markdownify
- Requires external binary installation (operational friction)
- GPL license (more restrictive)
- Failed to extract image alt text (0%)

**Docling Weaknesses**:
- Poor link preservation (46.5%) - unacceptable for help docs
- 5.7x slower than markdownify
- Heavy dependencies (ML models, ONNX runtime)
- Complex initialization overhead
- Failed to extract image alt text (0%)
- Overkill for HTML→Markdown (designed for PDFs/complex layouts)

## Outstanding Clarifications
None; all clarifications resolved in specification.

## Final Recommendation

**SELECTED: Markdownify (default strategy)**

Adopt **markdownify** as the default conversion library for HTML→Markdown transformation. Benchmark results demonstrate clear superiority across critical metrics:

1. **Highest Overall Quality** (0.838 score) - 75% higher than Pandoc, 48% higher than Docling
2. **Perfect Link Preservation** (100%) - essential for interconnected help documentation
3. **Perfect Table & Image Handling** (100% each) - preserves critical structural elements
4. **Exceptional Performance** (28.3ms avg) - exceeds spec by 70x margin, enables real-time workflows
5. **Zero Dependencies** - pure Python, no external tools, minimal operational friction
6. **Permissive License** (MIT) - no GPL restrictions on distribution or commercial use

### Strategy Retention Decision

**Two strategies (markdownify, docling) are retained** in the codebase:
- **markdownify**: Default strategy for Alteryx help HTML (lightweight, fast, excellent fidelity)
- **docling**: Available for future PDF/complex layout documents requiring layout awareness

Pandoc has been removed due to:
- Poor link preservation (38.6%) - critical failure for help documentation
- External binary dependency (operational friction)
- GPL license restrictions
- 15.7x slower than markdownify

This dual-strategy approach provides:
- Flexibility for future expansion to PDF and complex layout documents
- Ability to compare outputs during quality assurance
- Fast, lightweight default (markdownify) for HTML
- Advanced option (docling) for structured document extraction

### Implementation Path

1. ✅ **Keep selected strategies**: Retain markdownify (default) and docling (future expansion)
2. ✅ **Remove pandoc**: Deleted pandoc_adapter.py and pypandoc dependency
3. ✅ **Set default**: Markdownify is the default strategy (already configured in CLI)
4. ✅ **Document decision**: Add decision rationale to spec.md and research.md
5. ⏭️ **Proceed to Phase 3**: Begin foundational implementation with markdownify as primary

### Addressing Code Block Weakness

All three libraries showed poor code block language detection (28-37%). This will be addressed in Phase 3 via:
- Custom post-processing to detect language from CSS classes (`language-python`, `lang-js`, etc.)
- Heuristic detection from content patterns if class attributes absent
- Separate task in foundational phase (T021)

## Implementation Implications
- Keep adapter abstraction temporarily (`strategies/`) until decision finalized.
- Remove unused strategies before merge to comply with modular minimalism.
- Write converter tests first referencing expected Markdown fixtures created manually from sample HTML.

## Next Steps
1. Implement benchmark harness (temporary research script).
2. Populate sample corpus and run conversions.
3. Fill metrics and finalize matrix.
4. Remove unselected strategies and proceed to Phase 1 design artifacts.
