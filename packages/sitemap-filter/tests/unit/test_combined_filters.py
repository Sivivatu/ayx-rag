"""Unit tests for combined filter functionality."""

import pytest
from sitemap_filter.filters.parser import URLEntry


class TestFilterCriteria:
    """Tests for FilterCriteria dataclass."""
    
    def test_filter_criteria_creation(self):
        """Test creating FilterCriteria with languages and products."""
        from sitemap_filter.filters import FilterCriteria
        
        criteria = FilterCriteria(languages=["en", "de"], products=["designer"])
        
        assert criteria.languages == ["en", "de"]
        assert criteria.products == ["designer"]
    
    def test_filter_criteria_empty_lists(self):
        """Test FilterCriteria with empty lists."""
        from sitemap_filter.filters import FilterCriteria
        
        criteria = FilterCriteria(languages=[], products=[])
        
        assert criteria.languages == []
        assert criteria.products == []
    
    def test_filter_criteria_only_languages(self):
        """Test FilterCriteria with only languages specified."""
        from sitemap_filter.filters import FilterCriteria
        
        criteria = FilterCriteria(languages=["en"], products=[])
        
        assert criteria.languages == ["en"]
        assert criteria.products == []
    
    def test_filter_criteria_only_products(self):
        """Test FilterCriteria with only products specified."""
        from sitemap_filter.filters import FilterCriteria
        
        criteria = FilterCriteria(languages=[], products=["designer", "server"])
        
        assert criteria.languages == []
        assert criteria.products == ["designer", "server"]


class TestApplyFilters:
    """Tests for apply_filters function with combined criteria."""
    
    @pytest.fixture
    def mixed_entries(self):
        """Create diverse URL entries for testing combinations."""
        return [
            URLEntry(
                "https://help.alteryx.com/current/en/designer.html",
                "2025-10-23",
                "en",
                ["designer"]
            ),
            URLEntry(
                "https://help.alteryx.com/current/en/server.html",
                "2025-10-24",
                "en",
                ["server"]
            ),
            URLEntry(
                "https://help.alteryx.com/current/de/designer.html",
                "2025-10-25",
                "de",
                ["designer"]
            ),
            URLEntry(
                "https://help.alteryx.com/current/de/server.html",
                "2025-10-26",
                "de",
                ["server"]
            ),
            URLEntry(
                "https://help.alteryx.com/current/en/connect.html",
                "2025-10-27",
                "en",
                ["connect"]
            ),
            URLEntry(
                "https://help.alteryx.com/current/fr/designer.html",
                "2025-10-28",
                "fr",
                ["designer"]
            ),
        ]
    
    def test_apply_filters_language_only(self, mixed_entries):
        """Test filtering with only language criteria (no products)."""
        from sitemap_filter.filters import FilterCriteria, apply_filters
        
        criteria = FilterCriteria(languages=["en"], products=[])
        result = apply_filters(mixed_entries, criteria)
        
        assert len(result) == 3
        assert all(entry.language == "en" for entry in result)
    
    def test_apply_filters_product_only(self, mixed_entries):
        """Test filtering with only product criteria (no languages)."""
        from sitemap_filter.filters import FilterCriteria, apply_filters
        
        criteria = FilterCriteria(languages=[], products=["designer"])
        result = apply_filters(mixed_entries, criteria)
        
        assert len(result) == 3
        assert all("designer" in entry.products for entry in result)
    
    def test_apply_filters_language_and_product(self, mixed_entries):
        """Test AND logic: language AND product must both match."""
        from sitemap_filter.filters import FilterCriteria, apply_filters
        
        criteria = FilterCriteria(languages=["en"], products=["designer"])
        result = apply_filters(mixed_entries, criteria)
        
        # Should only get English Designer
        assert len(result) == 1
        assert result[0].language == "en"
        assert "designer" in result[0].products
    
    def test_apply_filters_multiple_languages_and_products(self, mixed_entries):
        """Test OR within type, AND across types."""
        from sitemap_filter.filters import FilterCriteria, apply_filters
        
        # (en OR de) AND (designer OR server)
        criteria = FilterCriteria(languages=["en", "de"], products=["designer", "server"])
        result = apply_filters(mixed_entries, criteria)
        
        # Should get: en+designer, en+server, de+designer, de+server (4 entries)
        # Should NOT get: en+connect, fr+designer
        assert len(result) == 4
        assert all(entry.language in ["en", "de"] for entry in result)
        assert all(any(p in entry.products for p in ["designer", "server"]) for entry in result)
    
    def test_apply_filters_no_matches(self, mixed_entries):
        """Test that conflicting filters return empty list."""
        from sitemap_filter.filters import FilterCriteria, apply_filters
        
        # Spanish designer - no such entries exist
        criteria = FilterCriteria(languages=["es"], products=["designer"])
        result = apply_filters(mixed_entries, criteria)
        
        assert len(result) == 0
    
    def test_apply_filters_empty_criteria_returns_all(self, mixed_entries):
        """Test that empty criteria returns all entries."""
        from sitemap_filter.filters import FilterCriteria, apply_filters
        
        criteria = FilterCriteria(languages=[], products=[])
        result = apply_filters(mixed_entries, criteria)
        
        assert len(result) == 6
        assert result == mixed_entries
    
    def test_apply_filters_preserves_entry_data(self, mixed_entries):
        """Test that filtering preserves all entry attributes."""
        from sitemap_filter.filters import FilterCriteria, apply_filters
        
        criteria = FilterCriteria(languages=["de"], products=["server"])
        result = apply_filters(mixed_entries, criteria)
        
        assert len(result) == 1
        entry = result[0]
        assert entry.loc == "https://help.alteryx.com/current/de/server.html"
        assert entry.lastmod == "2025-10-26"
        assert entry.language == "de"
        assert entry.products == ["server"]
    
    def test_apply_filters_three_languages_one_product(self, mixed_entries):
        """Test OR logic with multiple languages, single product."""
        from sitemap_filter.filters import FilterCriteria, apply_filters
        
        # (en OR de OR fr) AND designer
        criteria = FilterCriteria(languages=["en", "de", "fr"], products=["designer"])
        result = apply_filters(mixed_entries, criteria)
        
        # Should get designer in all three languages
        assert len(result) == 3
        assert {entry.language for entry in result} == {"en", "de", "fr"}
        assert all("designer" in entry.products for entry in result)
