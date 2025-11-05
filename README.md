# uv-ayx-rag

> RAG (Retrieval Augmented Generation) system for Alteryx help documentation

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Package Manager](https://img.shields.io/badge/package%20manager-uv-blue)](https://github.com/astral-sh/uv)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Overview

A modular RAG system designed to process and query ~35,000 Alteryx help documentation URLs from the sitemap. The project follows test-driven development practices and emphasizes data pipeline integrity with full source attribution and traceability.

### Current Status

**Phase**: Feature development in progress  
**Active Features**:  
- sitemap-filter v0.2.0 (complete)  
- sitemap-download v0.2.0 (complete)  
**Stage**: Ready for release

## Features

### ✅ Sitemap Filter (v0.1.0)

**Status**: Complete | **Branch**: `001-sitemap-filter`

Filter Alteryx help documentation sitemap URLs by language and product. CLI tool with 8 language support, 12+ products, and multiple output formats.

- 🌍 Filter by language (en, de, es, fr, it, ja, pt, zh-CHS)
- 📦 Filter by product (designer, server, connect, etc.)
- 🔀 Combined filters with AND/OR logic
- 📄 Output formats: JSON, text, XML
- ⚡ High performance: 8,864 URLs in ~0.1s
- ✅ 96% test coverage, 77 tests passing

**[View Full Documentation →](packages/sitemap-filter/README.md)**

**Quick Example:**
```bash
# Get English Designer documentation URLs
uv run main.py sitemap.xml --language en --product designer
```

### ✅ Sitemap Download (v0.2.0)

**Status**: Complete | **Branch**: `002-sitemap-download`

Download and validate XML sitemaps with progress tracking, smart incremental updates, and production-ready retry logic.

- 📥 Download with real-time progress (speed, ETA)
- ✓ XML validation with URL counting (SAX streaming)
- 🔄 Smart incremental updates (skip unchanged files)
- 🔁 Retry logic with exponential backoff
- 📦 Archive existing files with timestamps
- 💾 Memory efficient (8KB chunks, streaming)
- ✅ 95%+ test coverage, 56 tests passing

**[View Full Documentation →](packages/sitemap-download/README.md)**

**Quick Example:**
```bash
# Download Alteryx sitemap with progress
uv run python main.py sitemap-download

# Force update with archive
uv run python main.py sitemap-download --force --archive
```

### Planned

- Web scraper for content extraction
- Document processor (HTML cleaning, text chunking)
- Embedding service (vector generation)
- Vector store (indexing and search)
- Query interface (RAG-powered Q&A)

## Quick Start

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/Sivivatu/ayx-rag.git
cd ayx-rag

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# The project will install dependencies as needed when features are implemented
```

### Development Setup

```bash
# The project uses a dev container for consistent development environment
# Open in VS Code with Dev Containers extension, or use the container directly

# When implementing features, dependencies are added with:
uv add <package>           # Runtime dependency
uv add --dev <package>     # Development dependency
```

## Project Structure

```
.
├── .devcontainer/          # Dev container configuration
├── .github/
│   ├── copilot-instructions.md  # AI agent guidance
│   └── prompts/            # Speckit workflow prompts
├── .specify/
│   ├── memory/
│   │   └── constitution.md # Project governance (7 core principles)
│   ├── scripts/            # Feature workflow automation
│   └── templates/          # Spec, plan, and task templates
├── specs/
│   └── 001-sitemap-filter/ # Feature specifications
│       ├── spec.md         # User stories and requirements
│       ├── plan.md         # Implementation plan
│       ├── tasks.md        # Task breakdown
│       ├── research.md     # Technical decisions
│       ├── data-model.md   # Entity definitions
│       ├── contracts/      # API/CLI contracts
│       └── quickstart.md   # Developer guide
├── alteryx-help-current-sitemap.xml  # Source data (35,460 URLs)
└── README.md               # This file
```

When features are implemented, source code will be organized as:

```
src/                        # Source code (created during implementation)
├── scrapers/              # Web scraping modules
├── processors/            # Document processing
├── embeddings/            # Vector generation
├── storage/               # Database interactions
└── query/                 # RAG query interface

tests/                     # Test suite (created during implementation)
├── unit/                  # Unit tests
├── integration/           # Integration tests
└── fixtures/              # Test data
```

## Data Architecture

### Primary Data Source

- **File**: `alteryx-help-current-sitemap.xml`
- **Size**: 1.5MB
- **URLs**: 35,460 Alteryx help documentation URLs
- **Languages**: English (default) and German (`de`)
- **Pattern**: `https://help.alteryx.com/current/{locale?}/{path}.html`
- **Metadata**: Each URL includes `lastmod` timestamp for change tracking

### Focus

- Primary: English documentation
- Incremental updates based on `lastmod` timestamps
- Source attribution preserved through all pipeline stages

## Development Workflow

This project uses the **Speckit** framework for structured feature development:

### 1. Specify (Create Feature Spec)

```bash
# Create new feature specification
.specify/scripts/bash/create-new-feature.sh "feature-name"

# Follow prompts to define user stories, requirements, success criteria
```

### 2. Plan (Create Implementation Plan)

```bash
# Generate implementation plan with research and design
# Uses: /speckit.plan command or equivalent workflow
```

### 3. Tasks (Break Down Implementation)

```bash
# Generate task breakdown organized by user story
# Uses: /speckit.tasks command or equivalent workflow
```

### 4. Implement (Execute Tasks)

```bash
# Follow TDD workflow (REQUIRED):
# 1. Write test (verify it fails)
# 2. Implement feature
# 3. Verify test passes
# 4. Refactor
# 5. Commit with conventional format
```

### 5. Document (Update README and Release Notes)

```bash
# Final steps for any feature:
# 1. Update README.md with new capabilities
# 2. Generate release notes from conventional commits
# 3. Update version numbers
```

## Core Principles

This project follows 8 core principles defined in `.specify/memory/constitution.md`:

1. **Modular Architecture**: Independent, testable modules with clear interfaces
2. **Data Pipeline Integrity**: Source attribution and traceability maintained throughout
3. **Test-Driven Development** (NON-NEGOTIABLE): Tests written before implementation
4. **Incremental Processing**: Support for checkpointing and resume capability
5. **Observability & Monitoring**: Structured logging and progress metrics
6. **Package Management** (NON-NEGOTIABLE): Exclusive use of `uv` package manager
7. **Git Commit Standards** (NON-NEGOTIABLE): Conventional Commits format
8. **Release Documentation** (NON-NEGOTIABLE): Mandatory README, CHANGELOG, and release notes updates

See [constitution.md](.specify/memory/constitution.md) for detailed requirements.

## Technology Stack

- **Language**: Python 3.10+
- **Package Manager**: uv (exclusively - never use pip)
- **Build Backend**: uv_build (native uv build backend for all packages)
- **Testing**: pytest with TDD approach (>80% coverage required)
- **Development**: Debian-based dev container with Oh My Zsh
- **CLI Framework**: typer (type-hint based)
- **Logging**: loguru (structured logging)

## Git Commit Conventions

All commits MUST follow [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `chore`: Maintenance tasks
- `ci`: CI/CD changes
- `build`: Build system changes

### Examples

**Simple commit** (1-2 files):
```
feat(sitemap-filter): add language filtering support
```

**Complex commit** (3+ files):
```
feat(pipeline): implement document processing pipeline

- Add HTML content extractor
- Implement text chunking with overlap
- Create metadata extraction module
- Add unit tests for each component
```

## Testing

Tests are REQUIRED before any implementation (TDD principle):

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=src --cov-report=term-missing

# Run specific test file
uv run pytest tests/unit/test_parser.py

# Run tests for specific feature
uv run pytest tests/integration/test_cli.py -v
```

**Coverage requirement**: Minimum 80%

## Contributing

### Development Process

1. **Create feature branch**: `git checkout -b <issue-number>-feature-name`
2. **Follow Speckit workflow**: Specify → Plan → Tasks → Implement → Document
3. **Write tests first**: TDD is non-negotiable
4. **Use uv exclusively**: Never use pip for package management
5. **Commit with convention**: Follow Conventional Commits format
6. **Update documentation**: README and release notes before merge
7. **Code review required**: All changes reviewed before merge

### Quality Gates

Before merge, verify:

- [ ] All tests pass (`uv run pytest`)
- [ ] Coverage >80% (`uv run pytest --cov=src`)
- [ ] All commits follow Conventional Commits format
- [ ] Documentation updated (README.md, feature docs)
- [ ] CHANGELOG.md entry created for feature version
- [ ] Release notes generated from commits
- [ ] Constitution principles followed (see checklist in feature plan.md)

## License

MIT License - See [LICENSE](LICENSE) file for details

## Project Links

- **Repository**: https://github.com/Sivivatu/ayx-rag
- **Issues**: https://github.com/Sivivatu/ayx-rag/issues
- **Documentation**: See `specs/` directory for feature specifications

## Acknowledgments

- Alteryx for comprehensive help documentation
- [uv](https://github.com/astral-sh/uv) for fast Python package management
- [Speckit](https://github.com/koksmat-com/speckit) framework for structured development

---

**Current Version**: 0.1.0  
**Last Updated**: 2025-11-03  
**Status**: Initial Release - sitemap-filter feature complete
