"""Unit tests for XML parser module."""

import pytest
from pathlib import Path
from sitemap_filter.filters.parser import parse_sitemap, URLEntry


class TestXMLParser:
    """Tests for XML sitemap parsing functionality."""
    
    @pytest.fixture
    def sample_sitemap_path(self):
        """Path to sample sitemap fixture."""
        return Path(__file__).parent.parent / "fixtures" / "sample_sitemap.xml"
    
    @pytest.fixture
    def malformed_sitemap_path(self):
        """Path to malformed sitemap fixture."""
        return Path(__file__).parent.parent / "fixtures" / "malformed_sitemap.xml"
    
    def test_parse_sitemap_returns_list_of_entries(self, sample_sitemap_path):
        """Test that parse_sitemap returns a list of URLEntry objects."""
        entries = parse_sitemap(sample_sitemap_path)
        
        assert isinstance(entries, list)
        assert len(entries) > 0
        assert all(isinstance(entry, URLEntry) for entry in entries)
    
    def test_parse_sitemap_extracts_loc_and_lastmod(self, sample_sitemap_path):
        """Test that parser correctly extracts loc and lastmod from XML."""
        entries = parse_sitemap(sample_sitemap_path)
        
        # Check first entry
        first_entry = entries[0]
        assert first_entry.loc == "https://help.alteryx.com/current/designer.html"
        assert first_entry.lastmod == "2025-10-23"
    
    def test_parse_sitemap_handles_missing_file(self):
        """Test that parser raises appropriate error for missing file."""
        with pytest.raises(FileNotFoundError):
            parse_sitemap(Path("nonexistent.xml"))
    
    def test_urlentry_has_required_attributes(self, sample_sitemap_path):
        """Test that URLEntry has all required attributes."""
        entries = parse_sitemap(sample_sitemap_path)
        entry = entries[0]
        
        assert hasattr(entry, 'loc')
        assert hasattr(entry, 'lastmod')
        assert hasattr(entry, 'language')
        assert hasattr(entry, 'products')
    
    def test_parse_sitemap_counts_all_urls(self, sample_sitemap_path):
        """Test that parser processes all URLs in the sitemap."""
        entries = parse_sitemap(sample_sitemap_path)
        
        # Sample sitemap has 10 URLs based on the fixture
        assert len(entries) == 10
