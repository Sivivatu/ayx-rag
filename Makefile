.PHONY: help lint format test test-cov check install clean

help:  ## Show this help message
@echo "Usage: make [target]"
@echo ""
@echo "Available targets:"
@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

install:  ## Install all dependencies
	uv sync

lint:  ## Run ruff linter
	uv run ruff check .

format:  ## Format code with ruff
	uv run ruff format .

format-check:  ## Check if code is formatted
	uv run ruff format --check .

fix:  ## Auto-fix linting issues
	uv run ruff check --fix .

test:  ## Run all tests
	cd packages/sitemap-filter && uv run pytest tests/
	uv run pytest tests/

test-cov:  ## Run tests with coverage
	cd packages/sitemap-filter && uv run pytest tests/ --cov=src/sitemap_filter --cov-report=term-missing --cov-fail-under=80
	uv run pytest tests/

check: lint format-check test  ## Run all checks (lint, format, test)

clean:  ## Clean temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage" -delete
