# Quickstart Guide: Page Downloader

**Feature**: 003-page-downloader  
**Date**: 2025-11-05  
**Purpose**: Help developers get started with page-downloader development

## Prerequisites

- Python >=3.10
- uv package manager installed
- Dev container running (optional but recommended)
- Git repository cloned

## Setup

### 1. Create the Package Structure

From repository root:

```bash
mkdir -p packages/page-downloader/src/page_downloader
mkdir -p packages/page-downloader/tests/{unit,integration,fixtures}
```

### 2. Create `pyproject.toml`

```bash
cat > packages/page-downloader/pyproject.toml << 'EOF'
[project]
name = "page-downloader"
version = "0.1.0"
description = "Download HTML pages from Alteryx documentation URLs"
requires-python = ">=3.10"
dependencies = [
    "httpx>=0.25.0",
    "rich>=13.0.0",
]

[build-system]
requires = ["uv_build>=0.9.6,<0.10.0"]
build-backend = "uv_build"
EOF
```

### 3. Install Dependencies

```bash
cd packages/page-downloader
uv sync
```

### 4. Register with Workspace

Add to root `pyproject.toml` under `[tool.uv.sources]`:

```toml
page-downloader = { workspace = true, editable = true }
```

Add to root `[project.dependencies]`:

```toml
dependencies = [
    "sitemap-filter",
    "sitemap-download",
    "page-downloader",  # Add this line
]
```

Sync workspace:

```bash
cd /workspaces/uv-ayx-rag
uv sync
```

## Development Workflow

### TDD Cycle

Following Constitution Principle III, write tests first:

#### 1. Write a Failing Test

```python
# packages/page-downloader/tests/unit/test_path_utils.py
import pytest
from pathlib import Path
from page_downloader.path_utils import sanitize_url_path

def test_sanitize_url_path_basic():
    """Test basic URL path sanitization."""
    url = "https://help.alteryx.com/current/en/designer/tools.html"
    output_dir = Path("/tmp/html")
    
    result = sanitize_url_path(url, output_dir)
    
    assert result == output_dir / "en/designer/tools.html"
```

#### 2. Run Test (Should Fail)

```bash
cd packages/page-downloader
uv run pytest tests/unit/test_path_utils.py::test_sanitize_url_path_basic -v
```

Expected: `ModuleNotFoundError` or `ImportError`

#### 3. Implement Minimal Code

```python
# packages/page-downloader/src/page_downloader/path_utils.py
from pathlib import Path
from urllib.parse import urlparse, unquote
import re

def sanitize_url_path(url: str, output_dir: Path) -> Path:
    """Convert URL to filesystem path, sanitizing invalid characters."""
    parsed = urlparse(url)
    path = unquote(parsed.path).lstrip('/')
    
    # Replace invalid filesystem characters
    invalid_chars = r'[<>:"|?*]'
    path = re.sub(invalid_chars, '_', path)
    
    if not path or path == '/':
        path = 'index.html'
    
    if not path.endswith('.html'):
        path += '.html'
    
    return output_dir / path
```

#### 4. Run Test (Should Pass)

```bash
uv run pytest tests/unit/test_path_utils.py::test_sanitize_url_path_basic -v
```

Expected: `PASSED`

#### 5. Refactor

Add more test cases, improve implementation, maintain passing tests.

### Running Tests

**All tests**:
```bash
uv run pytest tests/
```

**With coverage**:
```bash
uv run pytest tests/ --cov=src/page_downloader --cov-report=term-missing
```

**Single test file**:
```bash
uv run pytest tests/unit/test_path_utils.py -v
```

**Single test function**:
```bash
uv run pytest tests/unit/test_path_utils.py::test_sanitize_url_path_basic -v
```

**Watch mode** (requires pytest-watch):
```bash
uv run ptw tests/unit/test_path_utils.py
```

## Project Structure

```
packages/page-downloader/
├── pyproject.toml           # Package configuration
├── README.md                # Package documentation
├── src/
│   └── page_downloader/
│       ├── __init__.py      # Exports app for main.py
│       ├── cli.py           # Typer CLI commands
│       ├── downloader.py    # HTTP download engine
│       ├── models.py        # Data models
│       ├── validator.py     # HTML & robots.txt validation
│       ├── path_utils.py    # Path sanitization
│       ├── progress.py      # Progress tracking
│       └── exceptions.py    # Custom exceptions
└── tests/
    ├── fixtures/
    │   ├── sample_pages/    # Test HTML files
    │   ├── robots.txt       # Test robots.txt
    │   └── url_lists/       # Sample URL inputs
    ├── unit/
    │   ├── test_downloader.py
    │   ├── test_models.py
    │   ├── test_validator.py
    │   ├── test_path_utils.py
    │   └── test_progress.py
    └── integration/
        ├── test_cli.py
        └── test_incremental.py
```

## Common Development Tasks

### Add a New Dependency

```bash
cd packages/page-downloader
uv add <package-name>
```

Example:
```bash
uv add beautifulsoup4
```

### Add a Development Dependency

```bash
uv add --dev <package-name>
```

Example:
```bash
uv add --dev respx
```

### Run CLI Locally

```bash
# From workspace root
uv run python main.py page-downloader --help

# Single URL test
uv run python main.py page-downloader \
  https://help.alteryx.com/current/en/designer.html \
  --dry-run

# URL list test
uv run python main.py page-downloader \
  data/test-urls.txt \
  --output-dir /tmp/test-html \
  --dry-run
```

### Debug with VS Code

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug page-downloader CLI",
      "type": "python",
      "request": "launch",
      "module": "page_downloader.cli",
      "args": [
        "https://help.alteryx.com/current/en/designer.html",
        "--output-dir", "/tmp/test-html",
        "--dry-run",
        "--verbose"
      ],
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}"
    },
    {
      "name": "Debug page-downloader tests",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": [
        "packages/page-downloader/tests/unit/test_downloader.py",
        "-v"
      ],
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}"
    }
  ]
}
```

### Mock HTTP Requests in Tests

Use `respx` for httpx mocking:

```python
import respx
import httpx
import pytest
from page_downloader.downloader import download_page

@respx.mock
def test_download_success():
    """Test successful page download."""
    url = "https://example.com/page.html"
    html_content = b"<html><body>Test</body></html>"
    
    # Mock the HTTP GET request
    respx.get(url).mock(
        return_value=httpx.Response(
            200,
            headers={"content-type": "text/html", "content-length": "31"},
            content=html_content
        )
    )
    
    # Call the function
    result = download_page(url, output_dir=Path("/tmp"))
    
    # Assertions
    assert result.status == "success"
    assert result.bytes_transferred == 31

@respx.mock
def test_download_timeout():
    """Test download with timeout."""
    url = "https://example.com/slow.html"
    
    # Mock timeout
    respx.get(url).mock(side_effect=httpx.TimeoutException)
    
    # Call and expect error
    with pytest.raises(httpx.TimeoutException):
        download_page(url, output_dir=Path("/tmp"))
```

### Create Test Fixtures

```python
# packages/page-downloader/tests/conftest.py
import pytest
from pathlib import Path
from page_downloader.models import DownloadConfig

@pytest.fixture
def sample_config(tmp_path):
    """Create a sample DownloadConfig."""
    return DownloadConfig(output_dir=tmp_path)

@pytest.fixture
def url_list_file(tmp_path):
    """Create a sample URL list file."""
    url_file = tmp_path / "urls.txt"
    url_file.write_text(
        "https://example.com/page1.html\n"
        "https://example.com/page2.html\n"
        "https://example.com/page3.html\n"
    )
    return url_file

@pytest.fixture
def sample_html():
    """Return sample HTML content."""
    return b"<html><head><title>Test</title></head><body>Content</body></html>"
```

## Integration with main.py

### 1. Export CLI App

In `packages/page-downloader/src/page_downloader/__init__.py`:

```python
"""Page downloader for Alteryx documentation."""

from .cli import app

__all__ = ["app"]
__version__ = "0.1.0"
```

### 2. Register with main.py

In workspace root `main.py`:

```python
#!/usr/bin/env python3
"""Main CLI entry point for uv-ayx-rag."""

import typer
from sitemap_filter import app as sitemap_filter_app
from sitemap_download import app as sitemap_download_app
from page_downloader import app as page_downloader_app  # Add this

app = typer.Typer(
    name="uv-ayx-rag",
    help="RAG system for Alteryx documentation",
    no_args_is_help=True,
)

# Register subcommands
app.add_typer(sitemap_download_app, name="sitemap-download")
app.add_typer(sitemap_filter_app, name="sitemap-filter")
app.add_typer(page_downloader_app, name="page-downloader")  # Add this

if __name__ == "__main__":
    app()
```

### 3. Test Integration

```bash
python main.py --help
python main.py page-downloader --help
```

## Code Style and Linting

Project uses `ruff` for linting and formatting:

### Check code style:
```bash
uv run ruff check packages/page-downloader/src
```

### Auto-fix issues:
```bash
uv run ruff check --fix packages/page-downloader/src
```

### Format code:
```bash
uv run ruff format packages/page-downloader/src
```

### Run before committing:
```bash
uv run ruff check --fix packages/page-downloader/src
uv run ruff format packages/page-downloader/src
uv run pytest packages/page-downloader/tests/ --cov
```

## Git Workflow

### Conventional Commits

All commits must follow conventional commits format:

**Simple commits** (1-2 files):
```bash
git commit -m "feat(page-downloader): add path sanitization"
git commit -m "test(page-downloader): add downloader unit tests"
git commit -m "fix(page-downloader): handle empty URL paths"
```

**Complex commits** (3+ files):
```bash
git commit -m "feat(page-downloader): implement HTTP download engine

- Add downloader.py with streaming download support
- Implement retry logic with exponential backoff
- Add timeout handling for connect and read
- Create unit tests for all download scenarios"
```

### Commit Types

- `feat`: New feature
- `fix`: Bug fix
- `test`: Adding/updating tests
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `style`: Code style changes (formatting, etc.)
- `chore`: Build/tooling changes
- `perf`: Performance improvements

## Debugging Tips

### Enable verbose logging:
```bash
python main.py page-downloader urls.txt --verbose
```

### Check log output:
```bash
# Logs go to stderr, redirect to file
python main.py page-downloader urls.txt 2> debug.log
```

### Use pdb debugger:
```python
import pdb; pdb.set_trace()  # Add breakpoint
```

### Use rich inspect for debugging:
```python
from rich import inspect
inspect(my_object, methods=True)
```

## Performance Testing

### Test rate limiting accuracy:
```python
import time
from page_downloader.downloader import RateLimiter

limiter = RateLimiter(delay=0.5)
times = []

for i in range(10):
    start = time.time()
    limiter.wait()
    elapsed = time.time() - start
    times.append(elapsed)

# Check variance < 10% (SC-008)
import statistics
mean = statistics.mean(times)
variance = statistics.variance(times)
print(f"Mean: {mean:.3f}s, Variance: {variance:.6f}")
assert variance / mean < 0.10  # Less than 10% variance
```

### Test download speed:
```python
@respx.mock
def test_download_performance():
    """Verify single page download < 5 seconds (SC-001)."""
    url = "https://example.com/page.html"
    content = b"x" * 1024 * 100  # 100KB
    
    respx.get(url).mock(return_value=httpx.Response(200, content=content))
    
    start = time.time()
    result = download_page(url)
    elapsed = time.time() - start
    
    assert elapsed < 5.0  # SC-001 requirement
```

## Troubleshooting

### Issue: Module not found

**Problem**: `ModuleNotFoundError: No module named 'page_downloader'`

**Solution**: Sync workspace
```bash
cd /workspaces/uv-ayx-rag
uv sync
```

### Issue: Tests not discovering

**Problem**: Pytest can't find tests

**Solution**: Ensure `__init__.py` exists in test directories
```bash
touch packages/page-downloader/tests/__init__.py
touch packages/page-downloader/tests/unit/__init__.py
```

### Issue: Import errors in tests

**Problem**: Tests can't import from `page_downloader`

**Solution**: Run tests from package root with uv:
```bash
cd packages/page-downloader
uv run pytest tests/
```

### Issue: httpx mocking not working

**Problem**: `respx.mock` doesn't intercept requests

**Solution**: Ensure `@respx.mock` decorator is used and respx is installed:
```bash
uv add --dev respx
```

## Next Steps

1. **Implement models.py**: Define data classes from data-model.md
2. **Implement path_utils.py**: URL-to-path sanitization
3. **Implement downloader.py**: HTTP download engine with retry logic
4. **Implement validator.py**: robots.txt and HTML validation
5. **Implement progress.py**: Progress tracking with rich
6. **Implement exceptions.py**: Custom exception classes
7. **Implement cli.py**: Typer CLI commands
8. **Write comprehensive tests**: Achieve >95% coverage
9. **Update README.md**: Package documentation
10. **Create release notes**: Document v0.1.0 features

## Resources

- **Spec**: `specs/003-page-downloader/spec.md`
- **Research**: `specs/003-page-downloader/research.md`
- **Data Model**: `specs/003-page-downloader/data-model.md`
- **CLI Contract**: `specs/003-page-downloader/contracts/cli-interface.md`
- **httpx docs**: https://www.python-httpx.org/
- **rich docs**: https://rich.readthedocs.io/
- **typer docs**: https://typer.tiangolo.com/
- **pytest docs**: https://docs.pytest.org/
- **respx docs**: https://lundberg.github.io/respx/

## Getting Help

- Review existing packages: `sitemap-filter`, `sitemap-download`
- Check constitution: `.specify/memory/constitution.md`
- Read copilot instructions: `.github/copilot-instructions.md`
- Search project issues on GitHub
- Ask in team chat/discussions

Happy coding! 🚀
