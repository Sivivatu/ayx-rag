"""Pytest configuration and shared fixtures."""

from pathlib import Path

import pytest


@pytest.fixture
def fixtures_dir():
    """Return the path to the fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def valid_sitemap_path(fixtures_dir):
    """Return path to valid sitemap fixture."""
    return fixtures_dir / "valid_sitemap.xml"


@pytest.fixture
def large_sitemap_path(fixtures_dir):
    """Return path to large sitemap fixture."""
    return fixtures_dir / "large_sitemap.xml"
