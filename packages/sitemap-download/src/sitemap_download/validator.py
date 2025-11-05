"""XML sitemap validator with memory-efficient SAX parsing."""

import time
import xml.sax
from pathlib import Path
from loguru import logger

from .models import ValidationResult
from .exceptions import ValidationError


class SitemapContentHandler(xml.sax.ContentHandler):
    """SAX handler for streaming sitemap validation."""

    def __init__(self):
        """Initialize handler state."""
        super().__init__()
        self.url_count = 0
        self.in_url = False
        self.in_sitemap = False
        self.has_loc = False
        self.current_element_stack = []
        self.root_element = None
        self.errors = []

    def startElement(self, name, attrs):
        """Handle start of element."""
        self.current_element_stack.append(name)

        # Track root element
        if self.root_element is None:
            self.root_element = name
            # Validate root element is urlset or sitemapindex
            if name not in ("urlset", "sitemapindex"):
                self.errors.append(
                    f"Invalid root element '{name}', expected 'urlset' or 'sitemapindex'"
                )

        # Track URL or sitemap entries
        if name == "url":
            self.in_url = True
            self.has_loc = False
        elif name == "sitemap":
            self.in_sitemap = True
            self.has_loc = False
        elif name == "loc":
            self.has_loc = True

    def endElement(self, name):
        """Handle end of element."""
        # Validate URL/sitemap entry has loc
        if name == "url":
            if not self.has_loc:
                self.errors.append(f"URL entry {self.url_count + 1} missing <loc> element")
            else:
                self.url_count += 1
            self.in_url = False
        elif name == "sitemap":
            if not self.has_loc:
                self.errors.append(f"Sitemap entry {self.url_count + 1} missing <loc> element")
            else:
                self.url_count += 1
            self.in_sitemap = False

        if self.current_element_stack:
            self.current_element_stack.pop()


class SitemapValidator:
    """Validates XML sitemaps using streaming SAX parser for memory efficiency."""

    def validate(self, file_path: Path) -> ValidationResult:
        """Validate a sitemap file.

        Args:
            file_path: Path to sitemap XML file

        Returns:
            ValidationResult with validation status, URL count, and any errors

        Note:
            Uses SAX parsing for memory-efficient validation of large files.
            Validates:
            - File exists and is readable
            - Valid XML structure
            - Root element is urlset or sitemapindex
            - All URL/sitemap entries have loc elements
            - File contains at least one URL/sitemap entry
        """
        start_time = time.time()

        # Check file exists
        if not file_path.exists():
            duration = time.time() - start_time
            return ValidationResult.invalid_result(
                error=f"File not found: {file_path}",
                file_size=0,
                duration=duration,
            )

        file_size = file_path.stat().st_size

        # Check file is not empty
        if file_size == 0:
            duration = time.time() - start_time
            return ValidationResult.invalid_result(
                error="File is empty",
                file_size=0,
                duration=duration,
            )

        # Parse and validate XML
        try:
            handler = SitemapContentHandler()
            parser = xml.sax.make_parser()
            parser.setContentHandler(handler)

            with open(file_path, "r", encoding="utf-8") as f:
                parser.parse(f)

            duration = time.time() - start_time

            # Check for errors collected during parsing
            if handler.errors:
                error_msg = "; ".join(handler.errors)
                logger.warning(f"Sitemap validation failed: {error_msg}")
                return ValidationResult.invalid_result(
                    error=error_msg,
                    file_size=file_size,
                    duration=duration,
                )

            # Check URL count
            if handler.url_count == 0:
                return ValidationResult(
                    valid=False,
                    url_count=0,
                    file_size=file_size,
                    error_message="Sitemap contains no URLs",
                    validation_duration=duration,
                )

            logger.debug(
                f"Sitemap validation successful: {handler.url_count} URLs, {file_size} bytes"
            )
            return ValidationResult.valid_result(
                url_count=handler.url_count,
                file_size=file_size,
                duration=duration,
            )

        except xml.sax.SAXParseException as e:
            duration = time.time() - start_time
            error_msg = f"XML parse error at line {e.getLineNumber()}: {e.getMessage()}"
            logger.warning(f"Sitemap validation failed: {error_msg}")
            return ValidationResult.invalid_result(
                error=error_msg,
                file_size=file_size,
                duration=duration,
            )
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Validation error: {str(e)}"
            logger.error(f"Unexpected validation error: {error_msg}")
            return ValidationResult.invalid_result(
                error=error_msg,
                file_size=file_size,
                duration=duration,
            )
