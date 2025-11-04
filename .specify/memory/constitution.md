<!--
Sync Impact Report:
- Version change: 1.1.0 → 1.2.0
- Updated constitution with new principle
- Principles defined:
  1. Modular Architecture (updated - workspace structure)
  2. Data Pipeline Integrity (existing)
  3. Test-Driven Development (existing)
  4. Incremental Processing (existing)
  5. Observability & Monitoring (existing)
  6. Package Management (existing)
  7. Git Commit Standards (existing)
  8. Release Documentation (existing - NON-NEGOTIABLE)
  9. Main Entry Point (NEW - NON-NEGOTIABLE)
- Changes:
  - Added Principle IX: Main Entry Point (mandatory main.py dispatcher)
  - Updated Principle I: Modular Architecture (workspace structure requirements)
  - Updated Governance section to reference 9 principles
  - Version bump: MINOR (new principle added)
- Templates status:
  - ✅ plan-template.md (aligned - includes constitution checks)
  - ✅ spec-template.md (aligned - requirements include documentation)
  - ✅ tasks-template.md (aligned - Phase 8 includes documentation tasks)
- Follow-up items: Update any documentation that references principle count
-->

# uv-ayx-rag Constitution

## Core Principles

The uv-ayx-rag project is governed by **9 core principles**, four of which are NON-NEGOTIABLE and cannot be violated under any circumstances.

### I. Modular Architecture

All components MUST be organized as independently testable modules with clear separation of concerns. Each feature MUST be organized as a uv workspace package with isolated dependencies. The project uses uv workspaces to manage multiple packages within a monorepo structure.

**Rationale**: RAG systems involve complex data pipelines. Modular design with workspace isolation enables parallel development, easier testing, component replacement without system-wide refactoring, and clean dependency management.

**Requirements**:
- Each feature is a separate workspace package under `packages/`
- Each package has its own `pyproject.toml` with isolated dependencies
- Workspace root `pyproject.toml` declares workspace members
- Packages expose clear interfaces (protocols/abstract base classes)
- Cross-package dependencies are explicit and documented
- Each package has its own test directory with independent unit tests
- Workspace structure:
  ```
  /workspaces/uv-ayx-rag/
  ├── main.py (entry point dispatcher)
  ├── pyproject.toml (workspace root)
  └── packages/
      ├── feature-name/
      │   ├── pyproject.toml (feature dependencies)
      │   ├── src/
      │   │   └── feature_name/
      │   │       ├── __init__.py
      │   │       ├── cli.py
      │   │       └── modules/
      │   └── tests/
      └── another-feature/
          └── ...
  ```

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

All Python dependencies MUST be managed exclusively through **uv**. Never use pip directly. All dependencies MUST be declared in `pyproject.toml` with version constraints. All workspace packages MUST use the **uv_build** build backend.

**Rationale**: uv provides fast, reproducible dependency resolution. Consistent tooling prevents version conflicts and "works on my machine" issues. The uv_build backend provides zero-config defaults, tight integration with uv, and fast builds for pure Python packages.

**Requirements**:
- Use `uv add <package>` to add dependencies
- Use `uv run <script>` to execute Python scripts
- Use `uv sync` to synchronize environment
- Lock file (`uv.lock`) MUST be committed
- Dev dependencies separated from runtime dependencies
- Each workspace package MUST include in `pyproject.toml`:
  ```toml
  [build-system]
  requires = ["uv_build>=0.9.6,<0.10.0"]
  build-backend = "uv_build"
  ```
- Upper bound on uv_build version ensures build stability across uv releases

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

### VIII. Release Documentation (NON-NEGOTIABLE)

Every feature MUST complete comprehensive documentation updates before being considered complete. No feature is ready for merge without updated user-facing documentation.

**Rationale**: Documentation drift creates confusion, prevents feature discovery, and wastes time as users cannot find or understand capabilities. Mandatory documentation ensures the project remains accessible and maintainable.

**Requirements**:
- **README.md** MUST be updated with:
  - Feature capabilities and overview
  - Installation/setup instructions for new dependencies
  - Usage examples demonstrating key functionality
  - Updated feature list showing current status
- **CHANGELOG.md** MUST include entry for the feature version:
  - Categorized changes (Added/Changed/Fixed/etc.)
  - Version number following semantic versioning
  - Release date in YYYY-MM-DD format
- **Release Notes** MUST be generated from conventional commits:
  - Use `.github/RELEASE_NOTES_TEMPLATE.md` as guide
  - Group by feature/fix/performance/documentation
  - Include usage examples and migration notes if applicable
- **Final Documentation Commit** MUST use format:
  - `docs(<feature>): update README and create release notes for vX.Y.Z`

**Enforcement**:
- Documentation tasks are final phase in every feature workflow
- Pull requests without documentation updates will be rejected
- Code review checklist includes documentation verification
- CI pipeline checks for CHANGELOG entry (when implemented)

### IX. Main Entry Point (NON-NEGOTIABLE)

The project MUST have a single main entry point at `main.py` in the repository root. All CLI functionality MUST be accessed through this entry point. Individual features MUST register their CLI commands with the main dispatcher.

**Rationale**: A single entry point provides users with a consistent interface to all project capabilities. As the RAG system grows to include scrapers, processors, embeddings, and query interfaces, a unified CLI prevents confusion and enables feature discovery through built-in help.

**Requirements**:
- `main.py` MUST be located at repository root
- `main.py` MUST use typer to create a main CLI application
- Feature packages MUST export their typer app in `__init__.py`
- `main.py` MUST register feature apps as subcommands using `app.add_typer()`
- Running `python main.py --help` MUST list all available subcommands
- Each subcommand MUST have clear help text describing its purpose
- Feature CLI modules MUST be named `cli.py` within their package
- Example structure:
  ```python
  # main.py
  import typer
  from feature_name import app as feature_app
  
  app = typer.Typer(name="uv-ayx-rag", help="...")
  app.add_typer(feature_app, name="feature-name", help="...")
  
  if __name__ == "__main__":
      app()
  ```

**User Experience**:
```bash
# Discover all features
python main.py --help

# Access specific feature
python main.py sitemap-filter --help

# Run feature command
python main.py sitemap-filter sitemap.xml --language en
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
- Code reviews verify TDD, commit standards, documentation (III, VII, VIII)
- PR checklists verify package management (VI)
- Monitoring dashboards verify observability (V)
- Documentation review verifies release documentation (VIII)
- Entry point review verifies main.py dispatcher pattern (IX)

**Complexity Justification**:
Any violation of these principles (e.g., skipping tests, tight coupling, manual pip usage, bypassing main.py) MUST be explicitly justified in code review with:
- Why the principle cannot be followed
- What simpler alternatives were considered and rejected
- What technical debt is created and plan to address it

**Runtime Guidance**: See `.github/copilot-instructions.md` for AI coding agent guidance aligned with this constitution.

**Version**: 1.2.0 | **Ratified**: 2025-10-30 | **Last Amended**: 2025-10-31
