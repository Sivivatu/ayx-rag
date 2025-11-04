# Copilot Instructions for uv-ayx-rag

## Project Overview
This is a RAG (Retrieval Augmented Generation) system for Alteryx help documentation. The project uses **uv workspaces** to organize features as independent packages with isolated dependencies. The single entry point is `main.py` which routes commands to feature packages.

## Development Environment

### Package Management
- Uses **uv** (fast Python package manager) exclusively - never use pip
- Project uses **uv workspaces** - root manages workspace and global dependencies, packages have isolated deps
- Root `pyproject.toml` declares workspace members with `[tool.uv.workspace]`
- Commands: `uv add <package>`, `uv run <script>`, `uv sync`

### Workspace Structure
```
/workspaces/uv-ayx-rag/
├── main.py                      # Single CLI entry point (routes to features)
├── pyproject.toml               # Workspace root configuration
├── packages/                    # Feature packages
│   └── sitemap-filter/          # Sitemap filtering feature
│       ├── pyproject.toml       # Package-specific dependencies
│       ├── src/
│       │   └── sitemap_filter/
│       │       ├── __init__.py  # Exports CLI function
│       │       ├── cli.py       # Feature CLI implementation
│       │       └── filters/     # Feature modules
│       └── tests/               # Feature-specific tests
└── data/                        # Shared data files
```

### Dev Container Setup
- Debian-based container with Python extensions
- Pre-configured with Oh My Zsh, spaceship prompt, and helpful plugins
- User: `developer` with sudo access

## Data Architecture

### Primary Data Source
- `alteryx-help-current-sitemap.xml`: Contains 8,864 Alteryx help URLs (filtered from 35,460)
- URLs follow pattern: `https://help.alteryx.com/current/{locale}/{product}/path.html`
- Supported locales: `en`, `de`, `es`, `fr`, `it`, `ja`, `pt`, `zh-CHS`
- Each URL has `lastmod` timestamp for change tracking

### Current Features
1. **sitemap-filter** (v0.2.0): Filter sitemap URLs by language and product
   - Languages: en/de/es/fr/it/ja/pt/zh-CHS or 'all'
   - Products: designer/server/connect/etc.
   - Output formats: JSON (metadata), text (plain), XML (sitemap)
   - Combined filters with AND/OR logic

### Expected Components (to be built)
2. **Web scraper**: Extract content from sitemap URLs
3. **Document processor**: Clean HTML, chunk text, extract metadata
4. **Embedding service**: Generate vector embeddings
5. **Vector store**: Index and search document chunks
6. **Query interface**: RAG-powered Q&A system

## Key Development Patterns

### Workspace Package Pattern
- Each feature is a separate workspace package under `packages/`
- Package structure:
  ```
  packages/feature-name/
  ├── pyproject.toml           # Feature dependencies (typer, loguru, etc.)
  ├── src/
  │   └── feature_name/
  │       ├── __init__.py      # Export CLI function/app
  │       ├── cli.py           # CLI implementation
  │       └── modules/         # Feature-specific modules
  └── tests/                   # Feature tests
  ```
- `main.py` imports and registers feature CLI commands
- Use `@app.command("feature-name")` decorator in main.py
- Feature function should match CLI signature and delegate to actual implementation

### CLI Entry Point Pattern
```python
# main.py
import typer
from feature_name.cli import feature_function

app = typer.Typer(...)

@app.command("feature-name")
def feature_command(...):
    """Wrapper for feature."""
    from feature_name.cli import feature_function as do_feature
    do_feature(...)
```

### Data Processing Pipeline
- Respect `lastmod` dates for incremental updates
- Preserve URL structure for source attribution
- Consider rate limiting when scraping help.alteryx.com
- Use FilterCriteria dataclass for combined filters (AND across types, OR within)

### Environment Commands
```bash
# Sync workspace (installs all package dependencies)
uv sync

# Add dependency to specific package
cd packages/feature-name && uv add <package>

# Run tests for specific package
cd packages/feature-name && uv run pytest tests/

# Run main CLI
uv run python main.py --help
uv run python main.py feature-name --help
```

## Integration Considerations
- Alteryx documentation URLs may require specific headers or session handling
- Consider caching strategies for the large document corpus
- Plan for multilingual content handling (German + English) in long term project roadmap
- Design for incremental updates based on sitemap timestamps

## Testing Strategy
- Unit tests for document processing functions
- Integration tests for scraping pipeline
- End-to-end tests for RAG query accuracy
- Performance tests for large-scale document processing

## Git Commit Conventions
- **Always use Conventional Commits** format: `<type>(<scope>): <description>`
- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`, `ci`, `build`
- **Simple commits** (1-2 files): Use subject line only
  - Example: `feat(scraper): add rate limiting support`
  - Example: `fix(embeddings): handle empty document chunks`
- **Complex commits** (3+ files): Add extended message with bullet points
  - Example:
    ```
    feat(pipeline): implement document processing pipeline
    
    - Add HTML content extractor
    - Implement text chunking with overlap
    - Create metadata extraction module
    - Add unit tests for each component
    ```

## Feature Completion Requirements
Every feature MUST complete these documentation steps before being considered done:
1. **Update README.md**: Add feature capabilities, usage examples, installation instructions
2. **Update CHANGELOG.md**: Add entry for the new version with categorized changes
3. **Generate Release Notes**: Create release notes from conventional commits using `.github/RELEASE_NOTES_TEMPLATE.md`
4. **Final Commit**: Use format `docs(<feature>): update README and create release notes for vX.Y.Z`

These steps ensure the project documentation stays current and users can discover new capabilities.

When implementing features, prioritize incremental development with clear separation of concerns between scraping, processing, storage, and query components.

## Active Technologies
- **Python 3.10+**: Core language (workspace requires >=3.10)
- **uv**: Package manager and workspace orchestrator
- **typer**: CLI framework with type hints and auto-documentation
- **loguru**: Structured logging with zero-config
- **pytest & pytest-cov**: Testing framework with coverage
- **xml.etree.ElementTree**: Standard library XML parsing/generation
- Local filesystem (default: `alteryx-help-current-sitemap.xml` at project root) (002-sitemap-download)

## Current Package Status
- **sitemap-filter** (v0.2.0): Complete with 57 passing tests
  - Language filtering (8 languages + 'all')
  - Product filtering (12+ products)
  - Combined filters with AND/OR logic
  - Output formats: JSON, text, XML
  - File output support

## Recent Changes
- 002-sitemap-download: Added Python 3.10+
- 2025-10-31: Restructured to uv workspaces with main.py entry point (Constitution v1.2.0)
- 2025-10-31: Added Principle IX: Main Entry Point (NON-NEGOTIABLE)
