"""Tests for exception classes."""

import pytest
from sitemap_download.exceptions import (
    SitemapDownloadError,
    NetworkError,
    ValidationError,
    ConfigurationError,
)


class TestExceptions:
    """Tests for exception hierarchy."""

    def test_base_exception(self):
        """Test that SitemapDownloadError can be raised."""
        with pytest.raises(SitemapDownloadError):
            raise SitemapDownloadError("Base error")

    def test_network_error_inherits_from_base(self):
        """Test that NetworkError inherits from SitemapDownloadError."""
        assert issubclass(NetworkError, SitemapDownloadError)
        with pytest.raises(SitemapDownloadError):
            raise NetworkError("Network error")

    def test_validation_error_inherits_from_base(self):
        """Test that ValidationError inherits from SitemapDownloadError."""
        assert issubclass(ValidationError, SitemapDownloadError)
        with pytest.raises(SitemapDownloadError):
            raise ValidationError("Validation error")

    def test_configuration_error_inherits_from_base(self):
        """Test that ConfigurationError inherits from SitemapDownloadError."""
        assert issubclass(ConfigurationError, SitemapDownloadError)
        with pytest.raises(SitemapDownloadError):
            raise ConfigurationError("Configuration error")

    def test_network_error_message(self):
        """Test NetworkError with custom message."""
        error = NetworkError("Connection timeout")
        assert str(error) == "Connection timeout"

    def test_validation_error_message(self):
        """Test ValidationError with custom message."""
        error = ValidationError("Invalid XML structure")
        assert str(error) == "Invalid XML structure"

    def test_configuration_error_message(self):
        """Test ConfigurationError with custom message."""
        error = ConfigurationError("Invalid destination path")
        assert str(error) == "Invalid destination path"
