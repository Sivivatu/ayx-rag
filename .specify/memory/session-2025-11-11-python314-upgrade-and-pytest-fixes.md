# Session: 2025-11-11 — Python 3.14 Upgrade & Pytest Import Fixes

## Context & Goals
- Upgrade project Python version from 3.12 to 3.14 to support Docling v2.59+ (adds Python 3.14 compatibility)
- Update all dependencies to latest compatible versions
- Resolve pytest import errors caused by upgrade to pytest 9.0
- Maintain Python 3.10 compatibility as per project requirement
- Prepare html-to-markdown package for Docling adapter implementation

## Implementation Summary

### Python Version Upgrade
- **Target**: Python 3.14.0 (to enable Docling 2.59+)
- **Rationale**: User research identified Docling v2.59.0 as first version supporting Python 3.14
- **Constraint**: Must maintain Python 3.10 as minimum supported version per user requirement
- **Approach**: 
  - Updated root `pyproject.toml` to `requires-python = ">=3.14,<3.15"` (later reverted to `>=3.10`)
  - Updated all workspace package `pyproject.toml` files to align
  - Updated GitHub workflows (test.yml, lint.yml) to use Python 3.14
  - Updated Ruff target-version to `py314`

### Dependency Resolution
- **Typer Conflict**: Docling requires `typer>=0.12.5,<0.20.0`, conflicting with workspace `typer>=0.20.0`
  - Resolution: Pinned root typer to `>=0.12.5,<0.20.0`
  - Also updated sitemap-filter package typer constraint to match
  - Final resolved version: `typer==0.19.2`
- **System Dependencies**: Required for building native Python packages on 3.14
  - Installed: `libxml2-dev`, `libxslt-dev`, `zlib1g-dev`, `build-essential`, `pkg-config`, `g++`
  - Enabled compilation of `lxml` and `pyclipper` for Docling dependencies
- **Lock File**: Regenerated via `uv lock --upgrade --python 3.14` to resolve 3.14-compatible versions
  - Old `lxml==4.9.4` failed (incompatible with Python 3.14 C API changes)
  - New `lxml==6.0.2` succeeded
- **Major Version Updates**:
  - `docling`: 2.61.2 (from unspecified)
  - `httpx`: 0.28.1
  - `rich`: 14.2.0
  - `pytest`: 9.0.0 (caused import issues)
  - `ruff`: 0.14.4

### Pytest Import Mode Issues
- **Root Cause**: pytest 9.0 changed default `import_mode` from `prepend` to `importlib`
  - Importlib mode incompatible with hyphenated directory names (`html-to-markdown`)
  - Error: `ModuleNotFoundError: No module named 'tests.unit.test_markdownify_adapter'`
- **Attempted Fixes**:
  1. Added `packages/html-to-markdown/tests/__init__.py` → didn't help
  2. Set `importmode = prepend` in `pytest.ini` → config option not recognized in pytest 9.0
  3. Added `pythonpath` entries to pytest.ini → still failed
- **Solution**: Pass `--import-mode=prepend` as CLI flag in Makefile
  - Updated `Makefile` test target: `uv run pytest --import-mode=prepend`
  - Verified single test file passes with flag
- **Test Suite Status**: Import errors resolved; tests discovered but markdownify/pypandoc missing

### Package Dependencies
- **html-to-markdown additions**:
  - `docling>=2.59.0,<3.0.0` (Python 3.14 compatible)
  - `markdownify>=0.13.0` (for MarkdownifyStrategy)
  - `pypandoc>=1.13` (for PandocStrategy)
- **Dependency Placement Clarification**:
  - User confirmed: `loguru` and `typer` are ROOT project dependencies
  - Should NOT be duplicated in package-level `pyproject.toml` files
  - All workspace packages inherit root dependencies via workspace mechanism

## Key Decisions & Corrections

### Reverted Changes (per user feedback)
1. **Python Version Requirement**: Reverted from `>=3.14,<3.15` back to `>=3.10`
   - User wants capability to run on Python 3.10+
   - Current environment uses 3.14 for development, but must support 3.10 minimum
2. **Package-level Dependencies**: Removed `loguru` and `typer` from package pyproject files
   - These are workspace-level concerns, not package-specific
   - Only package-specific deps (markdownify, pypandoc, docling) belong in package files

### Configuration Files Updated
- `pyproject.toml` (root): Updated typer constraint, ruff target, Python req (reverted)
- `packages/html-to-markdown/pyproject.toml`: Added strategy dependencies
- `packages/sitemap-filter/pyproject.toml`: Aligned typer constraint
- `packages/sitemap-download/pyproject.toml`: Updated Python req (reverted)
- `packages/page-downloader/pyproject.toml`: Updated Python req (reverted)
- `.github/workflows/test.yml`: Changed matrix to `["3.14"]` only
- `.github/workflows/lint.yml`: Updated Python install to 3.14
- `Makefile`: Added `--import-mode=prepend` to test target
- `pytest.ini`: Cleaned up (removed experimental importmode settings)

## System Setup & Build Environment
- **Dev Container**: Debian Trixie with Python 3.14.0
- **Build Toolchain**: gcc-14, g++-14, binutils, cython3
- **Native Deps Installed**: 75 new packages (~313 MB) for building Python C extensions
- **Python Location**: `/home/developer/.local/share/uv/python/cpython-3.14.0-linux-x86_64-gnu`
- **Virtual Env**: `.venv` at project root (managed by uv)

## Tests & Status
- **Collection**: 257 tests collected (249 workspace + 8 html-to-markdown)
- **Import Errors**: Resolved via `--import-mode=prepend` CLI flag
- **Missing Dependencies**: markdownify/pypandoc tests fail (expected; deps added to package)
- **Other Packages**: sitemap-filter, sitemap-download, page-downloader tests unaffected
- **Next**: Run full suite after syncing new html-to-markdown dependencies

## CI/CD
- Workflows updated for Python 3.14 (test matrix simplified to single version)
- Lint workflow uses Python 3.14
- Lock file committed with 143 resolved packages

## Open Next Steps
1. **Sync Environment**: Run `uv sync` to install markdownify and pypandoc
2. **Run Full Test Suite**: Verify all 257 tests pass after dependency sync
3. **Docling Adapter**: Implement functional DoclingStrategy with proper markdown rendering
   - Handle model initialization (lazy loading, graceful fallback)
   - Extract structured content from `ConversionResult` (headings, tables, code, images)
   - Make Docling the default strategy (user preference)
4. **CLI Default**: Update html-to-markdown CLI to default `--strategy=docling`
5. **Python 3.10 Validation**: Test suite on Python 3.10 to confirm compatibility maintained
6. **Documentation**: Update copilot-instructions.md with Python 3.14 environment details

## Notable Discoveries
- **pytest 9.0 Breaking Change**: Default import mode switch broke hyphenated package names
- **Docling Model Artifacts**: Previous attempts revealed missing ONNX layout model; needs lazy init strategy
- **Typer Version Lock**: Docling's strict upper bound on typer prevents latest version usage
- **lxml Python 3.14**: Old versions incompatible with Python 3.14 C API changes (implicit function declarations, type mismatches)
- **uv lock --upgrade**: Essential for resolving Python version-specific wheels after major version bump

## Session Timeline
1. User requested Python 3.14 upgrade and Docling v2.59+ for Python 3.14 support
2. Updated pyproject files and workflows to target 3.14
3. Encountered typer version conflict; resolved by pinning to Docling-compatible range
4. Hit lxml build failures; installed system build dependencies
5. Regenerated lock file with `uv lock --upgrade --python 3.14`
6. Successful sync with 123 packages installed (4 minutes)
7. Attempted test run; hit pytest import errors with hyphenated package name
8. Multiple fix attempts; ultimately resolved via CLI flag `--import-mode=prepend`
9. Discovered missing strategy dependencies (markdownify, pypandoc)
10. User clarified: revert Python req to 3.10+, remove loguru/typer from packages
11. Added strategy deps to html-to-markdown package
12. Session summary requested → created this document

## Version Information
- **Python**: 3.14.0 (cpython)
- **uv**: latest (installed via setup-uv@v7)
- **Docling**: 2.61.2
- **Typer**: 0.19.2
- **Pytest**: 9.0.0
- **Ruff**: 0.14.4
- **Workspace Packages**: 4 (sitemap-filter, sitemap-download, page-downloader, html-to-markdown)
- **Total Dependencies**: 143 resolved packages

## User Preferences Captured
- Python 3.10 minimum compatibility is non-negotiable
- Development uses Python 3.14 for latest features/deps
- Root-level dependencies (typer, loguru) should NOT duplicate into packages
- Docling should be default html-to-markdown strategy
- No platform setting changes (GPT-5-Codex toggle out of scope)
