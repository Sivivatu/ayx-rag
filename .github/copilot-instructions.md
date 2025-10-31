# Copilot Instructions for uv-ayx-rag

## Project Overview
This is a RAG (Retrieval Augmented Generation) system for Alteryx help documentation. The project processes ~35,000 help documentation URLs from the Alteryx sitemap to create a searchable knowledge base.

## Development Environment

### Package Management
- Uses **uv** (fast Python package manager) exclusively - never use pip
- All dependencies managed through `pyproject.toml` when created
- Commands: `uv add <package>`, `uv run <script>`, `uv sync`

### Dev Container Setup
- Debian-based container with Python extensions
- Pre-configured with Oh My Zsh, spaceship prompt, and helpful plugins
- User: `developer` with sudo access

## Data Architecture

### Primary Data Source
- `alteryx-help-current-sitemap.xml`: Contains 35,460 Alteryx help URLs
- URLs follow pattern: `https://help.alteryx.com/current/{locale}/{path}.html`
- Includes German (`de`) and English (implied default) locales
- Each URL has `lastmod` timestamp for change tracking

### Expected Components (to be built)
1. **Web scraper**: Extract content from sitemap URLs
2. **Document processor**: Clean HTML, chunk text, extract metadata
3. **Embedding service**: Generate vector embeddings
4. **Vector store**: Index and search document chunks
5. **Query interface**: RAG-powered Q&A system

## Key Development Patterns

### Data Processing Pipeline
- Respect `lastmod` dates for incremental updates
- Focus exclusively on English versions
- Preserve URL structure for source attribution
- Consider rate limiting when scraping help.alteryx.com

### Environment Commands
```bash
# Install dependencies
uv add <package-name>

# Run scripts
uv run python <script.py>

# Sync environment
uv sync
```

### File Organization (when built)
- `src/scrapers/`: Web scraping modules
- `src/processors/`: Document processing and chunking
- `src/embeddings/`: Vector embedding generation
- `src/storage/`: Vector database interactions
- `src/query/`: RAG query interface
- `data/`: Raw and processed document storage
- `config/`: Environment and model configurations

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
- Python 3.10+ with xml.etree.ElementTree (XML parsing), typer (CLI framework), loguru (logging) (001-sitemap-filter)
- N/A (stateless script, no persistence) (001-sitemap-filter)

## Recent Changes
- 001-sitemap-filter: Updated to Python 3.10+, using typer for CLI and loguru for logging
