# Release Notes - v0.2.0

**Release Date**: October 31, 2025  
**Branch**: `001-sitemap-filter`

## 🎉 Sitemap Filter CLI - Initial Release

Filter Alteryx help documentation sitemap URLs by language and product with a high-performance command-line tool.

## ✨ New Features

### Language Filtering
- Support for 8 languages: English, German, Spanish, French, Italian, Japanese, Portuguese, and Chinese Simplified
- Use `--language` flag to filter by one or more languages
- Special `all` option to include all languages

### Product Filtering
- Filter by 12+ Alteryx products including Designer, Server, Connect, and more
- Use `--product` flag multiple times for OR logic
- Automatic product detection from URL paths

### Combined Filters
- Combine language AND product filters
- Smart logic: AND across filter types, OR within types
- Example: `--language en --language de --product designer` returns (English OR German) AND Designer URLs

### Output Formats
- **JSON**: Structured output with total/filtered counts and URL metadata
- **Text**: Plain text, one URL per line (default)
- **XML**: Valid sitemap format with filtered URLs
- Use `--format` flag to specify output type

### File Output
- Write to file with `--output` flag
- Or output to stdout for piping to other tools
- Preserves original `lastmod` timestamps

### Dry Run Mode
- Preview statistics without generating output
- Use `--dry-run` flag
- Shows total URLs, filtered count, and execution time

### Performance & Monitoring
- Processing performance logging (parsing, filtering, output phases)
- File size warnings for large sitemaps (>10MB)
- Total execution time tracking

## 📊 Performance

- **8,864 URLs**: ~0.1 seconds
- **1,200 URLs**: 0.014 seconds
- **Memory**: <50MB typical usage
- **Coverage**: 96% test coverage with 77 passing tests

## 🚀 Quick Start

```bash
# From workspace root
uv run python main.py sitemap.xml --language en --product designer

# From feature directory
cd packages/sitemap-filter
uv run python -m sitemap_filter.cli sitemap.xml --language en
```

## 📝 Examples

### Filter English Designer URLs
```bash
uv run python main.py alteryx-help-sitemap.xml \
  --language en \
  --product designer \
  --format json \
  --output designer-en.json
```

### Get All German Documentation
```bash
uv run python main.py alteryx-help-sitemap.xml \
  --language de \
  --format text \
  --output german-urls.txt
```

### Preview Statistics
```bash
uv run python main.py alteryx-help-sitemap.xml \
  --language en \
  --product designer \
  --product server \
  --dry-run
```

## 🧪 Testing

- **77 tests passing** (56 unit, 16 integration, 5 performance)
- **96% code coverage** across all modules
- Performance validation: all operations <3s
- Error handling validation for edge cases

## 📚 Documentation

- [Feature README](packages/sitemap-filter/README.md) - Complete usage guide
- [Specification](specs/001-sitemap-filter/spec.md) - User stories and requirements
- [Implementation Plan](specs/001-sitemap-filter/plan.md) - Design decisions
- [Task Breakdown](specs/001-sitemap-filter/tasks.md) - Development tracking

## 🔧 Technical Details

### Architecture
- **Parser**: XML sitemap parsing with URLEntry dataclass
- **Filters**: Modular language and product filters with combined logic
- **Formatters**: JSON, text, and XML output generators
- **CLI**: Typer-based interface with comprehensive validation

### Dependencies
- `typer>=0.20.0` - CLI framework
- `loguru>=0.7.3` - Structured logging
- Python 3.10+ - Core language

### Package Structure
- Organized as uv workspace package
- Isolated dependencies
- Independent testing
- Accessible via main.py or direct module invocation

## 🎯 Use Cases

1. **RAG Pipeline Preparation**: Filter to specific languages/products before content extraction
2. **Translation Workflows**: Extract multilingual URLs for comparison
3. **Content Auditing**: Identify documentation coverage by product/language
4. **Data Analysis**: Generate subsets for targeted analysis
5. **CI/CD Integration**: Automated filtering in documentation pipelines

## 🔜 What's Next

This release completes Phase 1 of the uv-ayx-rag project. Future phases include:
- Web scraper for content extraction
- Document processor for HTML cleaning and chunking
- Embedding service for vector generation
- Vector store for indexing
- Query interface for RAG-powered Q&A

## 📦 Installation

```bash
# Clone repository
git clone https://github.com/Sivivatu/ayx-rag.git
cd ayx-rag

# Checkout feature branch
git checkout 001-sitemap-filter

# Sync dependencies (automatic with uv)
uv sync

# Run tests
cd packages/sitemap-filter
uv run pytest tests/
```

## 🙏 Acknowledgments

- Built with [uv](https://github.com/astral-sh/uv) for fast package management
- CLI powered by [Typer](https://typer.tiangolo.com/)
- Logging with [Loguru](https://github.com/Delgan/loguru)
- Following [Conventional Commits](https://www.conventionalcommits.org/)

---

**Full Changelog**: [CHANGELOG.md](CHANGELOG.md)  
**Feature Documentation**: [packages/sitemap-filter/README.md](packages/sitemap-filter/README.md)
