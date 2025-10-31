"""Unit tests for language filtering functionality."""

import pytest
from sitemap_filter.filters.language import detect_language, filter_by_language
from sitemap_filter.filters.parser import URLEntry


class TestLanguageDetection:
    """Tests for language detection from URLs."""
    
    def test_detect_language_english_with_explicit_locale(self):
        """Test that English URLs have explicit /en/ locale."""
        url = "https://help.alteryx.com/current/en/designer.html"
        assert detect_language(url) == "en"
    
    def test_detect_language_german_with_de_locale(self):
        """Test that URLs with /de/ locale are detected as German."""
        url = "https://help.alteryx.com/current/de/designer.html"
        assert detect_language(url) == "de"
    
    def test_detect_language_no_locale_returns_empty(self):
        """Test that URLs without locale pattern return empty string."""
        url = "https://help.alteryx.com/current/designer.html"
        assert detect_language(url) == ""
    
    def test_with_product_path(self):
        """Test language detection works with product paths."""
        url_en = "https://help.alteryx.com/current/en/designer/tools.html"
        url_de = "https://help.alteryx.com/current/de/server/admin.html"
        
        assert detect_language(url_en) == "en"
        assert detect_language(url_de) == "de"
    
    def test_chinese_multi_char_locale(self):
        """Test detection of multi-character locale codes like zh-CHS."""
        url = "https://help.alteryx.com/current/zh-CHS/designer.html"
        assert detect_language(url) == "zh-CHS"


class TestLanguageFiltering:
    """Tests for filtering URL entries by language."""
    
    @pytest.fixture
    def sample_entries(self):
        """Create sample URL entries with mixed languages."""
        return [
            URLEntry("https://help.alteryx.com/current/en/designer.html", "2025-10-23", "en", []),
            URLEntry("https://help.alteryx.com/current/de/designer.html", "2025-10-22", "de", []),
            URLEntry("https://help.alteryx.com/current/en/server.html", "2025-10-21", "en", []),
            URLEntry("https://help.alteryx.com/current/de/server.html", "2025-10-20", "de", []),
            URLEntry("https://help.alteryx.com/current/en/connect.html", "2025-10-19", "en", []),
        ]
    
    def test_filter_by_language_english_only(self, sample_entries):
        """Test filtering for English URLs only."""
        result = filter_by_language(sample_entries, ["en"])
        
        assert len(result) == 3
        assert all(entry.language == "en" for entry in result)
    
    def test_filter_by_language_german_only(self, sample_entries):
        """Test filtering for German URLs only."""
        result = filter_by_language(sample_entries, ["de"])
        
        assert len(result) == 2
        assert all(entry.language == "de" for entry in result)
    
    def test_filter_by_language_multiple_languages(self, sample_entries):
        """Test filtering for multiple languages (OR logic)."""
        result = filter_by_language(sample_entries, ["en", "de"])
        
        assert len(result) == 5  # All entries
    
    def test_filter_by_language_empty_list_returns_all(self, sample_entries):
        """Test that empty language list returns all entries."""
        result = filter_by_language(sample_entries, [])
        
        assert len(result) == 5
        assert result == sample_entries
    
    def test_filter_by_language_nonexistent_language(self, sample_entries):
        """Test filtering for non-existent language returns empty list."""
        result = filter_by_language(sample_entries, ["fr"])
        
        assert len(result) == 0
    
    def test_filter_by_language_preserves_entry_data(self, sample_entries):
        """Test that filtering preserves all entry attributes."""
        result = filter_by_language(sample_entries, ["en"])
        
        first_entry = result[0]
        assert first_entry.loc == "https://help.alteryx.com/current/en/designer.html"
        assert first_entry.lastmod == "2025-10-23"
        assert first_entry.language == "en"
        assert first_entry.products == []
