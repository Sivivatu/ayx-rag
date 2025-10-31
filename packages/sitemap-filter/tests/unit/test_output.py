"""Unit tests for output formatting functionality."""

import json
import xml.etree.ElementTree as ET
import pytest
from sitemap_filter.filters.parser import URLEntry


class TestJSONFormatter:
    """Tests for JSON output formatting."""
    
    @pytest.fixture
    def sample_entries(self):
        """Sample URL entries for testing."""
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
        ]
    
    def test_format_json_structure(self, sample_entries):
        """Test JSON output has correct structure."""
        from sitemap_filter.filters.output import format_json
        
        result = format_json(sample_entries, total_count=100)
        
        assert "total_urls" in result
        assert "filtered_urls" in result
        assert "results" in result
        assert isinstance(result["results"], list)
    
    def test_format_json_counts(self, sample_entries):
        """Test JSON output has correct counts."""
        from sitemap_filter.filters.output import format_json
        
        result = format_json(sample_entries, total_count=100)
        
        assert result["total_urls"] == 100
        assert result["filtered_urls"] == 2
    
    def test_format_json_results_content(self, sample_entries):
        """Test JSON results contain URL and lastmod."""
        from sitemap_filter.filters.output import format_json
        
        result = format_json(sample_entries, total_count=100)
        
        assert len(result["results"]) == 2
        assert result["results"][0]["url"] == "https://help.alteryx.com/current/en/designer.html"
        assert result["results"][0]["lastmod"] == "2025-10-23"
        assert result["results"][1]["url"] == "https://help.alteryx.com/current/en/server.html"
        assert result["results"][1]["lastmod"] == "2025-10-24"
    
    def test_format_json_valid_json(self, sample_entries):
        """Test that output can be serialized as valid JSON."""
        from sitemap_filter.filters.output import format_json
        
        result = format_json(sample_entries, total_count=100)
        
        # Should not raise exception
        json_str = json.dumps(result)
        assert json_str is not None
        
        # Should be parsable
        parsed = json.loads(json_str)
        assert parsed["total_urls"] == 100
    
    def test_format_json_empty_entries(self):
        """Test JSON formatting with empty entries list."""
        from sitemap_filter.filters.output import format_json
        
        result = format_json([], total_count=100)
        
        assert result["total_urls"] == 100
        assert result["filtered_urls"] == 0
        assert result["results"] == []


class TestTextFormatter:
    """Tests for plain text output formatting."""
    
    @pytest.fixture
    def sample_entries(self):
        """Sample URL entries for testing."""
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
                "https://help.alteryx.com/current/de/connect.html",
                "2025-10-25",
                "de",
                ["connect"]
            ),
        ]
    
    def test_format_txt_one_url_per_line(self, sample_entries):
        """Test text format outputs one URL per line."""
        from sitemap_filter.filters.output import format_txt
        
        result = format_txt(sample_entries)
        lines = result.strip().split('\n')
        
        assert len(lines) == 3
        assert lines[0] == "https://help.alteryx.com/current/en/designer.html"
        assert lines[1] == "https://help.alteryx.com/current/en/server.html"
        assert lines[2] == "https://help.alteryx.com/current/de/connect.html"
    
    def test_format_txt_no_metadata(self, sample_entries):
        """Test text format contains only URLs, no metadata."""
        from sitemap_filter.filters.output import format_txt
        
        result = format_txt(sample_entries)
        
        # Should not contain dates
        assert "2025-10-23" not in result
        assert "2025-10-24" not in result
        
        # Should only contain URLs
        for line in result.strip().split('\n'):
            assert line.startswith("https://")
    
    def test_format_txt_empty_entries(self):
        """Test text formatting with empty entries list."""
        from sitemap_filter.filters.output import format_txt
        
        result = format_txt([])
        
        assert result == ""
    
    def test_format_txt_single_entry(self):
        """Test text formatting with single entry."""
        from sitemap_filter.filters.output import format_txt
        
        entries = [URLEntry("https://example.com", "2025-10-23", "en", [])]
        result = format_txt(entries)
        
        assert result == "https://example.com\n"


class TestXMLFormatter:
    """Tests for XML sitemap output formatting."""
    
    @pytest.fixture
    def sample_entries(self):
        """Sample URL entries for testing."""
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
        ]
    
    def test_format_xml_valid_structure(self, sample_entries):
        """Test XML output has valid sitemap structure."""
        from sitemap_filter.filters.output import format_xml
        
        result = format_xml(sample_entries)
        
        # Should be parseable XML
        root = ET.fromstring(result)
        
        # Check namespace
        assert root.tag == "{http://www.sitemaps.org/schemas/sitemap/0.9}urlset"
    
    def test_format_xml_url_elements(self, sample_entries):
        """Test XML contains correct URL elements."""
        from sitemap_filter.filters.output import format_xml
        
        result = format_xml(sample_entries)
        root = ET.fromstring(result)
        
        ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = root.findall('ns:url', ns)
        
        assert len(urls) == 2
    
    def test_format_xml_url_content(self, sample_entries):
        """Test XML URL elements contain loc and lastmod."""
        from sitemap_filter.filters.output import format_xml
        
        result = format_xml(sample_entries)
        root = ET.fromstring(result)
        
        ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        first_url = root.find('ns:url', ns)
        
        loc = first_url.find('ns:loc', ns).text
        lastmod = first_url.find('ns:lastmod', ns).text
        
        assert loc == "https://help.alteryx.com/current/en/designer.html"
        assert lastmod == "2025-10-23"
    
    def test_format_xml_declaration(self, sample_entries):
        """Test XML includes proper declaration."""
        from sitemap_filter.filters.output import format_xml
        
        result = format_xml(sample_entries)
        
        assert result.startswith('<?xml version="1.0" encoding="UTF-8"?>')
    
    def test_format_xml_empty_entries(self):
        """Test XML formatting with empty entries list."""
        from sitemap_filter.filters.output import format_xml
        
        result = format_xml([])
        root = ET.fromstring(result)
        
        ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = root.findall('ns:url', ns)
        
        assert len(urls) == 0
    
    def test_format_xml_all_entries_included(self, sample_entries):
        """Test that all entries are included in XML output."""
        from sitemap_filter.filters.output import format_xml
        
        result = format_xml(sample_entries)
        root = ET.fromstring(result)
        
        ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = root.findall('ns:url', ns)
        
        locs = [url.find('ns:loc', ns).text for url in urls]
        
        assert "https://help.alteryx.com/current/en/designer.html" in locs
        assert "https://help.alteryx.com/current/en/server.html" in locs
