<!--
Sync Impact Report:
- Version change: [INITIAL] → 1.0.0
- New constitution created with 7 core principles
- Principles defined:
  1. Modular Architecture (NEW)
  2. Data Pipeline Integrity (NEW)
  3. Test-Driven Development (NEW)
  4. Incremental Processing (NEW)
  5. Observability & Monitoring (NEW)
  6. Package Management (NEW)
  7. Git Commit Standards (NEW)
- Added sections:
  - Technology Stack (NEW)
  - Development Workflow (NEW)
  - Governance (NEW)
- Templates status:
  - ✅ plan-template.md (reviewed - constitution gates aligned)
  - ✅ spec-template.md (reviewed - requirements alignment confirmed)
  - ✅ tasks-template.md (reviewed - task categorization aligned)
- Follow-up items: None
-->

# uv-ayx-rag Constitution

## Core Principles

### I. Modular Architecture

All components MUST be organized as independently testable modules with clear separation of concerns. Each module (scraper, processor, embeddings, storage, query) MUST have well-defined interfaces and minimal coupling.

**Rationale**: RAG systems involve complex data pipelines. Modular design enables parallel development, easier testing, and component replacement without system-wide refactoring.

**Requirements**:
- Each module resides in its own directory under `src/`
- Modules expose clear interfaces (protocols/abstract base classes)
- Cross-module dependencies are explicit and documented
- Each module has independent unit tests

### II. Data Pipeline Integrity

All data transformations MUST preserve source attribution and enable traceability from output back to original source URL. The `lastmod` timestamp from the sitemap MUST be respected for incremental updates.

**Rationale**: With 35,460 documentation URLs, tracking data lineage is critical for debugging, updating stale content, and maintaining accurate citations in RAG responses.

**Requirements**:
- Every processed document chunk retains source URL and timestamp
- Pipeline stages log transformation metadata
- Incremental updates check `lastmod` dates before reprocessing
- Failed processing preserves partial results with error context

### III. Test-Driven Development (NON-NEGOTIABLE)

Tests MUST be written before implementation. The development cycle is: Write test → Verify test fails → Implement feature → Verify test passes → Refactor.

**Rationale**: Data processing pipelines are error-prone. TDD catches edge cases early (empty documents, malformed HTML, encoding issues) and serves as executable documentation.

**Requirements**:
- Unit tests for all data transformation functions
- Integration tests for pipeline stages
- Contract tests for module interfaces
- End-to-end tests for complete RAG workflows
- Test coverage tracked and maintained above 80%

### IV. Incremental Processing

Processing pipelines MUST support incremental execution. Large batch operations MUST be checkpointed to enable resume after interruption.

**Rationale**: Processing 35,460 URLs is time-intensive. Incremental processing with checkpointing prevents data loss from network failures, rate limits, or system interruptions.

**Requirements**:
- Progress tracking persisted to disk/database
- Failed items logged separately for retry
- Resume capability from last checkpoint
- Rate limiting configurable for external API calls
- Batch sizes configurable for memory management

### V. Observability & Monitoring

All pipeline stages MUST emit structured logs with consistent schema. Progress metrics MUST be exposed for monitoring. Errors MUST include sufficient context for debugging without accessing production systems.

**Rationale**: Long-running data pipelines require visibility into progress, performance bottlenecks, and failure modes for effective troubleshooting.

**Requirements**:
- Structured logging (JSON format) with timestamps, module, severity
- Progress metrics: items processed, items failed, processing rate
- Performance metrics: processing time per item, memory usage
- Error logs include: source URL, stage, stack trace, input sample
- Logs distinguish transient errors (retry) from permanent failures

### VI. Package Management (NON-NEGOTIABLE)

All Python dependencies MUST be managed exclusively through **uv**. Never use pip directly. All dependencies MUST be declared in `pyproject.toml` with version constraints.

**Rationale**: uv provides fast, reproducible dependency resolution. Consistent tooling prevents version conflicts and "works on my machine" issues.

**Requirements**:
- Use `uv add <package>` to add dependencies
- Use `uv run <script>` to execute Python scripts
- Use `uv sync` to synchronize environment
- Lock file (`uv.lock`) MUST be committed
- Dev dependencies separated from runtime dependencies

### VII. Git Commit Standards (NON-NEGOTIABLE)

All commits MUST follow Conventional Commits format: `<type>(<scope>): <description>`. Simple commits (1-2 files) use subject line only. Complex commits (3+ files) MUST include extended message with bullet points.

**Rationale**: Consistent commit messages enable automated changelog generation, semantic versioning, and efficient code archaeology.

**Requirements**:
- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`, `ci`, `build`
- Scope indicates component (e.g., `scraper`, `embeddings`, `pipeline`)
- Breaking changes MUST include `BREAKING CHANGE:` footer
- Simple example: `feat(scraper): add rate limiting support`
- Complex example:
  ```
  feat(pipeline): implement document processing pipeline
  
  - Add HTML content extractor
  - Implement text chunking with overlap
  - Create metadata extraction module
  - Add unit tests for each component
  ```

## Technology Stack

**Language**: Python 3.10+  
**Package Manager**: uv (exclusively)  
**Development Environment**: Dev container (Debian-based)  
**Primary Data Source**: `alteryx-help-current-sitemap.xml` (35,460 URLs)  
**Expected Components**:
- Web scraper (handles ~35k URLs with rate limiting)
- Document processor (HTML cleaning, text chunking, metadata extraction)
- Embedding service (vector generation)
- Vector store (indexing and similarity search)
- Query interface (RAG-powered Q&A)

**Constraints**:
- Focus on English documentation (German support in long-term roadmap)
- Respect `lastmod` timestamps for incremental updates
- Consider rate limiting for help.alteryx.com access
- Design for large corpus (caching, incremental updates)

## Development Workflow

**Branch Strategy**: Feature branches from main (`<issue-number>-feature-name`)  
**Code Review**: All changes require review before merge  
**Testing Gates**:
- All tests MUST pass before merge
- New features MUST include tests
- Test coverage MUST not decrease

**Documentation Requirements**:
- Public APIs documented with docstrings
- Complex algorithms include inline comments
- Major features include usage examples
- README updated when new components added

**Development Commands**:
```bash
# Install dependencies
uv add <package-name>

# Run scripts
uv run python <script.py>

# Sync environment
uv sync

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src --cov-report=term-missing
```

## Governance

This constitution supersedes all other development practices and coding conventions. All code reviews, design decisions, and implementation plans MUST verify compliance with these principles.

**Amendment Process**:
1. Propose amendment with justification in issue/PR
2. Document impact on existing code and templates
3. Update constitution with version bump (see versioning rules)
4. Migrate affected code to comply within 2 sprints
5. Update `.github/copilot-instructions.md` to reflect changes

**Versioning**:
- **MAJOR**: Backward incompatible changes (principle removal/redefinition)
- **MINOR**: New principles or materially expanded guidance
- **PATCH**: Clarifications, wording fixes, non-semantic refinements

**Compliance Review**:
- Design reviews verify architectural principles (I, II, IV)
- Code reviews verify TDD, commit standards (III, VII)
- PR checklists verify package management (VI)
- Monitoring dashboards verify observability (V)

**Complexity Justification**:
Any violation of these principles (e.g., skipping tests, tight coupling, manual pip usage) MUST be explicitly justified in code review with:
- Why the principle cannot be followed
- What simpler alternatives were considered and rejected
- What technical debt is created and plan to address it

**Runtime Guidance**: See `.github/copilot-instructions.md` for AI coding agent guidance aligned with this constitution.

**Version**: 1.0.0 | **Ratified**: 2025-10-30 | **Last Amended**: 2025-10-30
