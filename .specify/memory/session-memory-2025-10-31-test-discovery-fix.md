# Session Memory: Test Discovery Fix (2025-10-31)

## Problem
VS Code was failing to discover tests correctly in the uv workspace project. The test discovery was returning errors due to module import conflicts.

## Root Causes Identified

1. **Duplicate Test Directories**
   - Old tests existed in `/workspaces/uv-ayx-rag/tests/`
   - New tests existed in `/workspaces/uv-ayx-rag/packages/sitemap-filter/tests/`
   - Both directories contained identical test files with same names
   - pytest was trying to import from both locations, causing `import file mismatch` errors

2. **Duplicate Source Directories**
   - Old source code in `/workspaces/uv-ayx-rag/src/`
   - New source code in `/workspaces/uv-ayx-rag/packages/sitemap-filter/src/sitemap_filter/`
   - Caused namespace confusion

3. **Incorrect Import Statements**
   - Multiple files used `from src.filters import ...` (old pattern)
   - Should have been `from sitemap_filter.filters import ...` (workspace pattern)
   - Affected both source files and test files

4. **Misconfigured Test Paths**
   - `pytest.ini` pointed to old `tests/` directory
   - VS Code settings had incorrect test paths including `src` and `packages` root

## Actions Taken

### 1. Cleaned Up Old Directories
```bash
rm -rf tests src .pytest_cache
find . -type d -name __pycache__ -exec rm -rf {} +
```
Removed duplicate directories and cached Python bytecode.

### 2. Fixed Import Statements
Changed imports in the following files from `src.filters` to `sitemap_filter.filters`:

**Source Files:**
- `packages/sitemap-filter/src/sitemap_filter/filters/__init__.py`
- `packages/sitemap-filter/src/sitemap_filter/filters/language.py`
- `packages/sitemap-filter/src/sitemap_filter/filters/product.py`
- `packages/sitemap-filter/src/sitemap_filter/filters/output.py`

**Test Files:**
- `packages/sitemap-filter/tests/unit/test_combined_filters.py`

### 3. Updated pytest.ini
```ini
[pytest]
# Workspace test paths - add new package test directories here
testpaths = 
    packages/sitemap-filter/tests
    # packages/*/tests  # Future: auto-discover all package tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
pythonpath = .
addopts = 
    -v
    --strict-markers
    --tb=short
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
```

### 4. Updated .vscode/settings.json
```json
{
    "python.testing.pytestArgs": [
        "packages/sitemap-filter/tests"
    ],
    "python.testing.unittestEnabled": false,
    "python.testing.pytestEnabled": true
}
```

## Results

✅ **All 57 tests discovered correctly**
```
collected 57 items
- 1 integration test (CLI)
- 56 unit tests (filters, parser, output)
```

✅ **All tests passing**
```
57 passed in 0.40s
```

✅ **VS Code test discovery working**
- Test Explorer can now discover all tests
- No import conflicts
- Clean test execution

✅ **Configuration ready for future workspace packages**
- Comments added to guide adding new package test paths
- Pattern established: `packages/<package-name>/tests`

## Key Learnings

1. **uv Workspace Structure**
   - Each package under `packages/` should be self-contained
   - Source code goes in `packages/<package>/src/<package>/`
   - Tests go in `packages/<package>/tests/`
   - No root-level `src/` or `tests/` directories

2. **Import Pattern for Workspace Packages**
   - Always use package name: `from sitemap_filter.filters import ...`
   - Never use relative `src`: `from src.filters import ...` ❌

3. **Test Discovery Configuration**
   - pytest.ini `testpaths` must list all package test directories explicitly
   - VS Code `python.testing.pytestArgs` must match
   - Both need updating when adding new workspace packages

4. **Cache Clearing is Critical**
   - `__pycache__` directories can cause import conflicts
   - `.pytest_cache` can preserve old test discovery
   - Always clear caches when restructuring imports

## Future Package Addition Checklist

When adding a new package (e.g., `packages/web-scraper/`):

1. Create package structure:
   ```
   packages/web-scraper/
   ├── pyproject.toml
   ├── src/
   │   └── web_scraper/
   │       ├── __init__.py
   │       └── ...
   └── tests/
       └── ...
   ```

2. Update `pytest.ini`:
   ```ini
   testpaths = 
       packages/sitemap-filter/tests
       packages/web-scraper/tests  # ADD NEW LINE
   ```

3. Update `.vscode/settings.json`:
   ```json
   "python.testing.pytestArgs": [
       "packages/sitemap-filter/tests",
       "packages/web-scraper/tests"  // ADD NEW LINE
   ]
   ```

4. Use correct imports in all files:
   ```python
   from web_scraper.module import something
   ```

## Testing Commands

Verify test discovery:
```bash
uv run pytest --collect-only
```

Run all tests:
```bash
uv run pytest
```

Run tests with coverage:
```bash
uv run pytest --cov=packages/sitemap-filter/src --cov-report=term-missing
```

## Files Modified in This Session

1. `/workspaces/uv-ayx-rag/pytest.ini`
2. `/workspaces/uv-ayx-rag/.vscode/settings.json`
3. `/workspaces/uv-ayx-rag/packages/sitemap-filter/src/sitemap_filter/filters/__init__.py`
4. `/workspaces/uv-ayx-rag/packages/sitemap-filter/src/sitemap_filter/filters/language.py`
5. `/workspaces/uv-ayx-rag/packages/sitemap-filter/src/sitemap_filter/filters/product.py`
6. `/workspaces/uv-ayx-rag/packages/sitemap-filter/src/sitemap_filter/filters/output.py`
7. `/workspaces/uv-ayx-rag/packages/sitemap-filter/tests/unit/test_combined_filters.py`

## Directories Removed

1. `/workspaces/uv-ayx-rag/tests/` (duplicate)
2. `/workspaces/uv-ayx-rag/src/` (duplicate)
3. `/workspaces/uv-ayx-rag/.pytest_cache/` (stale cache)
4. All `__pycache__/` directories (stale bytecode)
