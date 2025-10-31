"""Unit tests for product filtering functionality."""

import pytest
from src.filters.parser import URLEntry


class TestProductExtraction:
    """Tests for extracting product path segments from URLs."""
    
    def test_extract_products_designer_base_url(self):
        """Test extraction of 'designer' from base product URL."""
        from src.filters.product import extract_products
        
        url = "https://help.alteryx.com/current/en/designer.html"
        products = extract_products(url)
        
        assert products == ["designer"]
    
    def test_extract_products_designer_subpath(self):
        """Test extraction from nested designer path."""
        from src.filters.product import extract_products
        
        url = "https://help.alteryx.com/current/en/designer/tools/input-data.html"
        products = extract_products(url)
        
        assert products == ["designer"]
    
    def test_extract_products_server(self):
        """Test extraction of 'server' product."""
        from src.filters.product import extract_products
        
        url = "https://help.alteryx.com/current/de/server/admin/config.html"
        products = extract_products(url)
        
        assert products == ["server"]
    
    def test_extract_products_connect(self):
        """Test extraction of 'connect' product."""
        from src.filters.product import extract_products
        
        url = "https://help.alteryx.com/current/en/connect.html"
        products = extract_products(url)
        
        assert products == ["connect"]
    
    def test_extract_products_unknown_segment(self):
        """Test that unknown path segments return empty list."""
        from src.filters.product import extract_products
        
        url = "https://help.alteryx.com/current/en/unknown-product.html"
        products = extract_products(url)
        
        assert products == []
    
    def test_extract_products_release_notes(self):
        """Test that release-notes path returns empty list (not a product)."""
        from src.filters.product import extract_products
        
        url = "https://help.alteryx.com/current/en/release-notes.html"
        products = extract_products(url)
        
        assert products == []


class TestProductFiltering:
    """Tests for filtering URL entries by product."""
    
    @pytest.fixture
    def sample_entries(self):
        """Create sample URL entries with mixed products."""
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
                "https://help.alteryx.com/current/en/connect.html",
                "2025-10-25",
                "en",
                ["connect"]
            ),
            URLEntry(
                "https://help.alteryx.com/current/de/designer/tools.html",
                "2025-10-26",
                "de",
                ["designer"]
            ),
            URLEntry(
                "https://help.alteryx.com/current/en/release-notes.html",
                "2025-10-27",
                "en",
                []
            ),
        ]
    
    def test_filter_by_product_designer_only(self, sample_entries):
        """Test filtering for designer product only."""
        from src.filters.product import filter_by_product
        
        result = filter_by_product(sample_entries, ["designer"])
        
        assert len(result) == 2
        assert all("designer" in entry.products for entry in result)
    
    def test_filter_by_product_server_only(self, sample_entries):
        """Test filtering for server product only."""
        from src.filters.product import filter_by_product
        
        result = filter_by_product(sample_entries, ["server"])
        
        assert len(result) == 1
        assert result[0].products == ["server"]
    
    def test_filter_by_product_multiple_products(self, sample_entries):
        """Test filtering with multiple products (OR logic)."""
        from src.filters.product import filter_by_product
        
        result = filter_by_product(sample_entries, ["designer", "server"])
        
        assert len(result) == 3
        assert all(
            any(p in entry.products for p in ["designer", "server"])
            for entry in result
        )
    
    def test_filter_by_product_empty_list_returns_all(self, sample_entries):
        """Test that empty product list returns all entries."""
        from src.filters.product import filter_by_product
        
        result = filter_by_product(sample_entries, [])
        
        assert len(result) == 5
        assert result == sample_entries
    
    def test_filter_by_product_nonexistent_product(self, sample_entries):
        """Test filtering for non-existent product returns empty list."""
        from src.filters.product import filter_by_product
        
        result = filter_by_product(sample_entries, ["nonexistent"])
        
        assert len(result) == 0
    
    def test_filter_by_product_preserves_entry_data(self, sample_entries):
        """Test that filtering preserves all entry attributes."""
        from src.filters.product import filter_by_product
        
        result = filter_by_product(sample_entries, ["connect"])
        
        assert len(result) == 1
        entry = result[0]
        assert entry.loc == "https://help.alteryx.com/current/en/connect.html"
        assert entry.lastmod == "2025-10-25"
        assert entry.language == "en"
        assert entry.products == ["connect"]
    
    def test_filter_by_product_includes_entries_with_no_products(self, sample_entries):
        """Test that entries with empty products list are excluded from product filters."""
        from src.filters.product import filter_by_product
        
        # Release notes has no products
        result = filter_by_product(sample_entries, ["designer", "server", "connect"])
        
        assert len(result) == 4
        assert not any(entry.products == [] for entry in result)
