"""Unit tests for validator module - HTML content validation."""

from httpx import Response
from page_downloader.validator import is_html_content


class TestIsHtmlContent:
    """Test suite for is_html_content function."""

    def test_text_html_content_type(self):
        """Test that text/html content type is recognized as HTML."""
        response = Response(
            status_code=200,
            headers={"content-type": "text/html"},
            content=b"<html><body>test</body></html>",
        )
        assert is_html_content(response) is True

    def test_text_html_with_charset(self):
        """Test that text/html with charset is recognized as HTML."""
        response = Response(
            status_code=200,
            headers={"content-type": "text/html; charset=utf-8"},
            content=b"<html><body>test</body></html>",
        )
        assert is_html_content(response) is True

    def test_text_html_with_charset_uppercase(self):
        """Test case-insensitive content-type matching."""
        response = Response(
            status_code=200,
            headers={"content-type": "TEXT/HTML; CHARSET=UTF-8"},
            content=b"<html><body>test</body></html>",
        )
        assert is_html_content(response) is True

    def test_application_xhtml_xml(self):
        """Test that application/xhtml+xml is recognized as HTML."""
        response = Response(
            status_code=200,
            headers={"content-type": "application/xhtml+xml"},
            content=b"<?xml version='1.0'?><html><body>test</body></html>",
        )
        assert is_html_content(response) is True

    def test_application_xhtml_xml_with_charset(self):
        """Test XHTML with charset parameter."""
        response = Response(
            status_code=200,
            headers={"content-type": "application/xhtml+xml; charset=utf-8"},
            content=b"<?xml version='1.0'?><html><body>test</body></html>",
        )
        assert is_html_content(response) is True

    def test_application_pdf_is_not_html(self):
        """Test that PDF content type is not recognized as HTML per FR-012."""
        response = Response(
            status_code=200,
            headers={"content-type": "application/pdf"},
            content=b"%PDF-1.4 fake pdf content",
        )
        assert is_html_content(response) is False

    def test_application_json_is_not_html(self):
        """Test that JSON content type is not recognized as HTML."""
        response = Response(
            status_code=200,
            headers={"content-type": "application/json"},
            content=b'{"key": "value"}',
        )
        assert is_html_content(response) is False

    def test_text_plain_is_not_html(self):
        """Test that plain text is not recognized as HTML."""
        response = Response(
            status_code=200,
            headers={"content-type": "text/plain"},
            content=b"This is plain text",
        )
        assert is_html_content(response) is False

    def test_image_png_is_not_html(self):
        """Test that image content is not recognized as HTML."""
        response = Response(
            status_code=200,
            headers={"content-type": "image/png"},
            content=b"\x89PNG\r\n\x1a\n fake png",
        )
        assert is_html_content(response) is False

    def test_text_xml_is_not_html(self):
        """Test that generic XML is not recognized as HTML."""
        response = Response(
            status_code=200,
            headers={"content-type": "text/xml"},
            content=b"<?xml version='1.0'?><root>data</root>",
        )
        assert is_html_content(response) is False

    def test_missing_content_type_header(self):
        """Test handling of missing Content-Type header."""
        response = Response(
            status_code=200,
            headers={},
            content=b"<html><body>test</body></html>",
        )
        # Should return False when no content-type header present
        assert is_html_content(response) is False

    def test_empty_content_type_header(self):
        """Test handling of empty Content-Type header."""
        response = Response(
            status_code=200,
            headers={"content-type": ""},
            content=b"<html><body>test</body></html>",
        )
        assert is_html_content(response) is False

    def test_malformed_content_type_header(self):
        """Test handling of malformed Content-Type header."""
        response = Response(
            status_code=200,
            headers={"content-type": "invalid;;;content;;;type"},
            content=b"<html><body>test</body></html>",
        )
        assert is_html_content(response) is False

    def test_content_type_with_multiple_parameters(self):
        """Test Content-Type with multiple parameters."""
        response = Response(
            status_code=200,
            headers={"content-type": "text/html; charset=utf-8; boundary=something"},
            content=b"<html><body>test</body></html>",
        )
        assert is_html_content(response) is True

    def test_content_type_with_whitespace(self):
        """Test Content-Type header with extra whitespace."""
        response = Response(
            status_code=200,
            headers={"content-type": "  text/html  ;  charset=utf-8  "},
            content=b"<html><body>test</body></html>",
        )
        assert is_html_content(response) is True

    def test_text_html_subtype_variations(self):
        """Test that only exact text/html or application/xhtml+xml are accepted."""
        # text/html-like but not exact match
        response = Response(
            status_code=200,
            headers={"content-type": "text/html-partial"},
            content=b"<html><body>test</body></html>",
        )
        assert is_html_content(response) is False

    def test_application_octet_stream_is_not_html(self):
        """Test that binary stream content is not recognized as HTML."""
        response = Response(
            status_code=200,
            headers={"content-type": "application/octet-stream"},
            content=b"\x00\x01\x02\x03\x04",
        )
        assert is_html_content(response) is False

    def test_text_css_is_not_html(self):
        """Test that CSS content is not recognized as HTML."""
        response = Response(
            status_code=200,
            headers={"content-type": "text/css"},
            content=b"body { margin: 0; }",
        )
        assert is_html_content(response) is False

    def test_application_javascript_is_not_html(self):
        """Test that JavaScript content is not recognized as HTML."""
        response = Response(
            status_code=200,
            headers={"content-type": "application/javascript"},
            content=b"console.log('test');",
        )
        assert is_html_content(response) is False

    def test_video_content_is_not_html(self):
        """Test that video content is not recognized as HTML."""
        response = Response(
            status_code=200,
            headers={"content-type": "video/mp4"},
            content=b"\x00\x00\x00 ftyp fake video",
        )
        assert is_html_content(response) is False
