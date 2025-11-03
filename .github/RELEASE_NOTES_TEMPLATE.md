# Release Notes Template

## How to Generate Release Notes

Release notes should be generated from conventional commits at the end of each feature development cycle.

### Automatic Generation

```bash
# Generate release notes for current feature branch
git log main..HEAD --pretty=format:"%s" | grep -E "^(feat|fix|perf|refactor|docs|test|chore|ci|build)" > release-notes-draft.md

# Or for a specific version tag
git log v0.1.0..v0.2.0 --pretty=format:"- %s (%h)" --reverse > release-notes-v0.2.0.md
```

### Manual Curation

Review the generated commits and organize into sections:

## Version X.Y.Z - D Month YYYY

### ✨ Features
- List all `feat:` commits
- Describe new capabilities
- Include user-facing improvements

### 🐛 Bug Fixes
- List all `fix:` commits
- Describe what was broken and how it's fixed

### ⚡ Performance
- List all `perf:` commits
- Quantify improvements where possible

### 📚 Documentation
- List all `docs:` commits
- Note major documentation improvements

### 🔧 Internal Changes
- List `refactor:`, `test:`, `chore:` commits
- Group by impact area

### 🏗️ Build & CI
- List `build:`, `ci:` commits
- Note infrastructure improvements

### ⚠️ Breaking Changes
- Extract from commit bodies with `BREAKING CHANGE:` footer
- Explain migration path

### 🙏 Contributors
- List contributors for this release
- Thank external contributors

---

## Example Release Notes

# Release v0.2.0 - Sitemap Filter CLI

**Released**: 31 October 2025

## ✨ Features

### Sitemap Filter CLI Tool
A powerful command-line tool for filtering Alteryx help documentation URLs from the sitemap XML file.

**Language Filtering** (`feat(sitemap-filter): add language filtering`)
- Filter sitemap URLs by language code (English/German)
- Automatic language detection from URL paths
- Support for multiple language selections

**Product Filtering** (`feat(sitemap-filter): add product path filtering`)
- Filter URLs by product path segments (designer, server, connect, etc.)
- Support multiple product filters with OR logic
- Extract product information from URL structure

**Combined Filters** (`feat(sitemap-filter): implement filter combination logic`)
- Combine language and product filters
- AND logic across filter types
- OR logic within filter types

**Multiple Output Formats** (`feat(sitemap-filter): add JSON/txt/xml output formats`)
- JSON format with metadata (default)
- Plain text format for piping to other tools
- XML sitemap format for filtered results
- File output support with `--output` flag
- Dry-run mode for statistics preview

## 🎯 Performance

- Process 35,460 URLs in under 3 seconds
- Memory usage under 500MB for 100k+ URLs
- Efficient regex-based pattern matching

## 📚 Documentation

- Complete quickstart guide with examples
- CLI interface contract specification
- Data model documentation
- Implementation plan and research documents
- Updated README with feature capabilities

## 🧪 Testing

- 80%+ test coverage achieved
- 18 contract tests pass
- Unit tests for all filter functions
- Integration tests for CLI interface
- Performance tests validate requirements

## 🔧 Technical Details

**Dependencies**:
- typer: Modern CLI framework with type hints
- loguru: Structured logging
- pytest: Testing framework (dev dependency)

**Architecture**:
- Modular design with clear separation of concerns
- Independent filter modules (language, product, output)
- Test-driven development throughout

## 📦 Installation

```bash
# Clone repository
git clone https://github.com/Sivivatu/ayx-rag.git
cd ayx-rag

# Switch to release branch
git checkout v0.2.0

# Install dependencies
uv add typer loguru
uv add --dev pytest pytest-cov
```

## 🚀 Usage Examples

```bash
# Filter English documentation only
uv run python src/sitemap_filter.py alteryx-help-current-sitemap.xml --language en

# Filter Designer product docs
uv run python src/sitemap_filter.py alteryx-help-current-sitemap.xml --product designer

# Combine filters and output to file
uv run python src/sitemap_filter.py alteryx-help-current-sitemap.xml \
  --language en --product designer --output designer-en.json

# Get statistics without full output
uv run python src/sitemap_filter.py alteryx-help-current-sitemap.xml \
  --language en --dry-run
```

## 🙏 Contributors

- @Sivivatu - Feature development and documentation

---

## What's Next?

Version 0.3.0 will focus on web scraping capabilities to extract content from filtered URLs.

See [CHANGELOG.md](CHANGELOG.md) for detailed change history.
