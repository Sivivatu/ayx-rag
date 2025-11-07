"""Unit tests for path_utils module - URL path sanitization."""


from page_downloader.path_utils import sanitize_url_path


class TestSanitizeUrlPath:
    """Test suite for sanitize_url_path function."""

    def test_basic_valid_path(self):
        """Test that valid paths pass through unchanged."""
        url = "https://help.alteryx.com/current/en/designer/tools.html"
        result = sanitize_url_path(url)
        assert result == "current/en/designer/tools.html"

    def test_strips_protocol_and_domain(self):
        """Test that protocol and domain are removed from path."""
        url = "https://help.alteryx.com/docs/index.html"
        result = sanitize_url_path(url)
        assert result == "docs/index.html"

    def test_strips_query_parameters(self):
        """Test that query parameters are removed per FR-027d."""
        url = "https://help.alteryx.com/current/en/designer/tools.html?version=2024&lang=en"
        result = sanitize_url_path(url)
        assert result == "current/en/designer/tools.html"

    def test_strips_fragment(self):
        """Test that URL fragments are removed per FR-027d."""
        url = "https://help.alteryx.com/current/en/designer/tools.html#section-1"
        result = sanitize_url_path(url)
        assert result == "current/en/designer/tools.html"

    def test_strips_both_query_and_fragment(self):
        """Test that both query params and fragments are removed."""
        url = "https://help.alteryx.com/page.html?foo=bar&baz=qux#anchor"
        result = sanitize_url_path(url)
        assert result == "page.html"

    def test_replaces_windows_invalid_chars(self):
        """Test that Windows filesystem-invalid characters are replaced per FR-005."""
        # Windows invalid chars: <>:"|?*
        url = "https://example.com/path/file<name>.html"
        result = sanitize_url_path(url)
        assert "<" not in result
        assert result == "path/file_name_.html"

    def test_replaces_multiple_invalid_chars(self):
        """Test multiple invalid characters in path."""
        url = "https://example.com/path/file:name|test*.html"
        result = sanitize_url_path(url)
        assert ":" not in result
        assert "|" not in result
        assert "*" not in result
        assert result == "path/file_name_test_.html"

    def test_handles_null_byte(self):
        """Test that null bytes are replaced (Unix invalid char)."""
        url = "https://example.com/path/file\x00name.html"
        result = sanitize_url_path(url)
        assert "\x00" not in result
        assert result == "path/file_name.html"

    def test_preserves_forward_slashes_in_path(self):
        """Test that forward slashes in path are preserved for directory structure."""
        url = "https://help.alteryx.com/current/en/designer/tools/input-tool.html"
        result = sanitize_url_path(url)
        assert result == "current/en/designer/tools/input-tool.html"
        assert result.count("/") == 4

    def test_handles_unicode_characters(self):
        """Test that Unicode characters are preserved."""
        url = "https://help.alteryx.com/current/ja/デザイナー/tools.html"
        result = sanitize_url_path(url)
        assert "デザイナー" in result
        assert result == "current/ja/デザイナー/tools.html"

    def test_handles_url_encoded_characters(self):
        """Test that URL-encoded characters are preserved as-is."""
        url = "https://help.alteryx.com/current/en/designer/tools%20guide.html"
        result = sanitize_url_path(url)
        # URL-encoded spaces (%20) should remain as-is
        assert result == "current/en/designer/tools%20guide.html"

    def test_handles_trailing_slash(self):
        """Test URLs with trailing slash."""
        url = "https://help.alteryx.com/current/en/designer/"
        result = sanitize_url_path(url)
        assert result == "current/en/designer/"

    def test_handles_root_path(self):
        """Test URL with only domain (root path)."""
        url = "https://help.alteryx.com/"
        result = sanitize_url_path(url)
        assert result == ""

    def test_handles_path_with_dots(self):
        """Test that dots in filenames are preserved."""
        url = "https://help.alteryx.com/current/en/file.name.with.dots.html"
        result = sanitize_url_path(url)
        assert result == "current/en/file.name.with.dots.html"

    def test_empty_path_component(self):
        """Test URL with empty path component."""
        url = "https://help.alteryx.com//double//slash//path.html"
        result = sanitize_url_path(url)
        # Should preserve structure but sanitize
        assert "path.html" in result

    def test_complex_realistic_url(self):
        """Test complex realistic Alteryx URL with multiple features."""
        url = "https://help.alteryx.com/current/en/designer/tools.html?version=2024.1&utm_source=docs#configuration"
        result = sanitize_url_path(url)
        # Should strip query and fragment, preserve path structure
        assert result == "current/en/designer/tools.html"
        assert "?" not in result
        assert "#" not in result
        assert "utm_source" not in result

    def test_malformed_url_without_protocol(self):
        """Test handling of URL without protocol."""
        url = "help.alteryx.com/current/en/designer/tools.html"
        # Should handle gracefully - implementation detail
        result = sanitize_url_path(url)
        assert isinstance(result, str)

    def test_quotation_marks_in_path(self):
        """Test that quotation marks are replaced per FR-005."""
        url = 'https://example.com/path/"quoted"/file.html'
        result = sanitize_url_path(url)
        assert '"' not in result
        assert result == "path/_quoted_/file.html"

    def test_angle_brackets_in_path(self):
        """Test that angle brackets are replaced per FR-005."""
        url = "https://example.com/path/<template>/file.html"
        result = sanitize_url_path(url)
        assert "<" not in result
        assert ">" not in result
        assert result == "path/_template_/file.html"

    def test_preserves_hyphens_and_underscores(self):
        """Test that valid characters like hyphens and underscores are preserved."""
        url = "https://help.alteryx.com/current/en/my-tool_name/index.html"
        result = sanitize_url_path(url)
        assert result == "current/en/my-tool_name/index.html"
        assert "-" in result
        assert "_" in result
