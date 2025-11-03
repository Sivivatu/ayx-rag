# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-11-03

### Added
- **Sitemap Filter CLI** - Filter Alteryx help documentation sitemap URLs by language and product
  - Language filtering for 8 languages (en, de, es, fr, it, ja, pt, zh-CHS)
  - Product filtering for 12+ Alteryx products (designer, server, connect, etc.)
  - Combined filters with AND/OR logic (language AND product, multiple values OR within type)
  - Multiple output formats: JSON (with metadata), plain text, XML sitemap
  - File output support with `--output` flag
  - Dry-run mode for previewing statistics without generating output
  - Performance logging for parsing, filtering, and output phases
  - File size validation with warnings for large sitemaps (>10MB)
  - Comprehensive error handling with clear messages
- Test infrastructure with 96% coverage
  - 77 tests (56 unit, 16 integration, 5 performance)
  - Test fixtures for various scenarios
  - Performance validation (<3s for large sitemaps)
- CLI accessible via workspace main entry point
- Comprehensive documentation in feature README

### Performance
- Processes 8,864 URLs in ~0.1 seconds
- Filters 1,200 URLs in 0.014 seconds
- Memory efficient (<50MB for typical workloads)

### Documentation
- Feature README with complete usage guide
- Architecture documentation
- API examples for all use cases
- Updated root README with feature summary

## Version History

- **0.1.0** (2025-11-03): Initial release with sitemap-filter feature
- **Unreleased**: Active development

---

## Previous Template Entries

### [Initial Setup] - 2025-10-31

#### Added
- Project initialization
- Dev container with Debian-based environment
- Oh My Zsh with spaceship prompt
- VS Code configuration and extensions
- Git repository setup
- Project README with comprehensive documentation
- Constitution defining development principles
- Speckit templates for feature workflow

### Documentation
- README.md with project overview and quick start
- Constitution.md with 7 core principles
- Copilot instructions for AI agent guidance
- Release notes template for future releases

---

## Template for Future Entries

## [X.Y.Z] - YYYY-MM-DD

### Added
- New features and capabilities

### Changed
- Changes to existing functionality

### Deprecated
- Features scheduled for removal

### Removed
- Features removed in this version

### Fixed
- Bug fixes

### Security
- Security improvements and vulnerability fixes

---

## Version History

- **0.1.0** (2025-10-31): Initial project setup
- **Unreleased**: Active development

---

## How to Update This File

1. **During Development**: Add entries to `[Unreleased]` section as features are completed
2. **Before Release**: Move `[Unreleased]` items to new version section
3. **Version Numbering**:
   - **MAJOR** (X.0.0): Breaking changes
   - **MINOR** (0.X.0): New features, backward compatible
   - **PATCH** (0.0.X): Bug fixes, backward compatible
4. **Always Include**: Date in YYYY-MM-DD format
5. **Categories**: Use standard categories (Added, Changed, Fixed, etc.)
6. **Commits Reference**: Link to conventional commits where applicable

## Links

- [Keep a Changelog](https://keepachangelog.com/)
- [Semantic Versioning](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
