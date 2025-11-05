"""Unit tests for sitemap validator."""

import pytest
from pathlib import Path
from sitemap_download.validator import SitemapValidator
from sitemap_download.models import ValidationResult


class TestSitemapValidator:
    """Tests for SitemapValidator class."""

    @pytest.fixture
    def validator(self):
        """Create validator instance."""
        return SitemapValidator()

    @pytest.fixture
    def fixtures_dir(self):
        """Path to test fixtures."""
        return Path(__file__).parent.parent / "fixtures"

    def test_validate_valid_urlset(self, validator, fixtures_dir):
        """Test validation of valid urlset sitemap."""
        sitemap_path = fixtures_dir / "valid_sitemap.xml"
        result = validator.validate(sitemap_path)

        assert result.valid is True
        assert result.url_count is not None
        assert result.url_count > 0
        assert result.error_message is None
        assert result.validation_duration >= 0

    def test_validate_empty_file(self, validator, fixtures_dir):
        """Test validation of empty sitemap file."""
        sitemap_path = fixtures_dir / "empty_sitemap.xml"
        result = validator.validate(sitemap_path)

        assert result.valid is False
        assert result.url_count == 0
        assert "no url" in result.error_message.lower()

    def test_validate_malformed_xml(self, validator, fixtures_dir):
        """Test validation of malformed XML."""
        sitemap_path = fixtures_dir / "malformed_sitemap.xml"
        result = validator.validate(sitemap_path)

        assert result.valid is False
        assert result.error_message is not None
        assert "xml" in result.error_message.lower() or "parse" in result.error_message.lower()

    def test_validate_missing_namespace(self, validator, tmp_path):
        """Test validation of sitemap with missing namespace."""
        sitemap_path = tmp_path / "no_namespace.xml"
        sitemap_path.write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset>\n'
            '  <url>\n'
            '    <loc>https://example.com</loc>\n'
            '  </url>\n'
            '</urlset>'
        )

        result = validator.validate(sitemap_path)

        # Should still work - namespace is optional for basic validation
        assert result.valid is True
        assert result.url_count == 1

    def test_validate_invalid_root_element(self, validator, tmp_path):
        """Test validation of sitemap with invalid root element."""
        sitemap_path = tmp_path / "invalid_root.xml"
        sitemap_path.write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<html>\n'
            '  <body>Not a sitemap</body>\n'
            '</html>'
        )

        result = validator.validate(sitemap_path)

        assert result.valid is False
        assert "root element" in result.error_message.lower() or "urlset" in result.error_message.lower()

    def test_validate_no_urls(self, validator, fixtures_dir):
        """Test validation of sitemap with no URLs."""
        sitemap_path = fixtures_dir / "empty_sitemap.xml"
        result = validator.validate(sitemap_path)

        assert result.valid is False
        assert result.url_count == 0

    def test_validate_url_missing_loc(self, validator, tmp_path):
        """Test validation of URL entry missing loc element."""
        sitemap_path = tmp_path / "missing_loc.xml"
        sitemap_path.write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            '  <url>\n'
            '    <lastmod>2025-10-23</lastmod>\n'
            '  </url>\n'
            '</urlset>'
        )

        result = validator.validate(sitemap_path)

        # Should reject URLs without loc
        assert result.valid is False
        assert "loc" in result.error_message.lower()

    def test_validate_file_not_found(self, validator, tmp_path):
        """Test validation of non-existent file."""
        sitemap_path = tmp_path / "nonexistent.xml"
        result = validator.validate(sitemap_path)

        assert result.valid is False
        assert "not found" in result.error_message.lower() or "does not exist" in result.error_message.lower()

    def test_validate_sitemapindex(self, validator, tmp_path):
        """Test validation of sitemapindex format."""
        sitemap_path = tmp_path / "sitemapindex.xml"
        sitemap_path.write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            '  <sitemap>\n'
            '    <loc>https://example.com/sitemap1.xml</loc>\n'
            '    <lastmod>2025-10-23</lastmod>\n'
            '  </sitemap>\n'
            '</sitemapindex>'
        )

        result = validator.validate(sitemap_path)

        # Should accept sitemapindex format
        assert result.valid is True
        assert result.url_count == 1  # Count sitemap entries
