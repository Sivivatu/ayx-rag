# Release v0.4.1 - Performance Fix

**Released**: 12 November 2025

## ⚡ Performance

### Critical Startup Performance Fix
Fixed a critical performance regression that caused 3+ minute startup times for all CLI commands, including simple operations like `--help`.

**Problem**:
- Heavy dependencies (Docling, Markdownify, evaluator, metrics) were imported at module level
- Every CLI invocation triggered full library initialization, even for `--help`
- Users experienced 180+ second delays for trivial commands

**Solution**:
- Implemented lazy loading for all heavy dependencies
- Moved strategy imports (`DoclingStrategy`, `MarkdownifyStrategy`) inside functions
- Added deferred imports in CLI commands (convert, batch, evaluate, benchmark)
- Implemented `__getattr__` pattern in `__init__.py` for lazy app export
- Changed evaluate command threshold parameters to optional with lazy loading

**Impact**:
- ✅ Reduced startup time from **3+ minutes to ~6 seconds** (95-97% improvement)
- ✅ Simple commands respond in ~6s (mostly uv run overhead + module structure)
- ✅ Heavy ML/document libraries only load when commands actually execute
- ✅ No functionality changes - all 132 tests still passing

**Performance Breakdown**:
```
Before: 180+ seconds (3+ minutes)
After:  ~6 seconds
- uv run overhead: ~3-4s
- Module imports: ~2-3s
- Python startup: ~1s

Heavy library loading (Docling): Only when needed (0s for --help)
```

## 🔧 Technical Changes

**Commits**:
- `2e9d388` - perf(html-to-markdown): lazy-load heavy dependencies
  - Lazy loading in `_all_strategy_classes()`
  - Deferred imports in command functions
  - `__getattr__` implementation for lazy app import
- `73367b6` - docs(main): update html-to-markdown registration
- `238dc84` - chore(html-to-markdown): bump version to v0.4.1

**Files Modified**:
- `packages/html-to-markdown/src/html_to_markdown/cli.py` - Lazy imports in commands
- `packages/html-to-markdown/src/html_to_markdown/__init__.py` - Lazy app export
- `main.py` - Documentation cleanup
- `CHANGELOG.md` - v0.4.1 entry
- `packages/html-to-markdown/README.md` - Performance documentation
- `packages/html-to-markdown/pyproject.toml` - Version bump to 0.4.1

## 📚 Documentation

- Updated README with startup performance characteristics
- Added lazy loading explanation in performance section
- Documented import optimization strategy in CHANGELOG
- Clarified that heavy libraries load on-demand

## ✅ Testing

All existing tests pass without modification:
- 132 tests (94 unit + 38 integration)
- No functional changes required
- Performance improvement validated via timing

## 📦 Installation

```bash
# Update to latest version
git pull origin 004-html-to-markdown

# Sync workspace
uv sync
```

## 🚀 Verification

Test the performance improvement:

```bash
# Should complete in ~6 seconds (not 3+ minutes)
time uv run python main.py --help

# Should complete in ~6 seconds
time uv run python main.py html-to-markdown --help

# Actual conversion still works (loads libraries when needed)
uv run python main.py html-to-markdown convert test.html
```

## 🐛 Known Issues

None. This is a pure performance optimization with no functional changes.

## 🙏 Impact

This fix restores usability for the html-to-markdown CLI:
- **Before**: 3-minute wait for help text made tool unusable for quick checks
- **After**: 6-second startup is acceptable for a feature-rich CLI
- Users can now use `--help` efficiently during development
- No impact on actual conversion performance (still <2s per file)

## What's Next?

Version 0.5.0 will focus on:
- Release notes generation for v0.4.0 (main feature release)
- Code cleanup and edge case testing (T038-T040)
- Optional enhancements (idempotency, encoding detection, warning logging)

See [CHANGELOG.md](CHANGELOG.md) for detailed change history.

---

**Full Changelog**: v0.4.0...v0.4.1
