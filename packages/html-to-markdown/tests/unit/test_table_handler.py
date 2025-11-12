"""Unit tests for table handling."""

from html_to_markdown.table_handler import (
    TableAnalyzer,
    extract_table_cells,
    should_use_html_fallback,
)


class TestTableAnalyzer:
    """Tests for TableAnalyzer."""

    def test_simple_table_not_complex(self):
        """Test simple table is not marked as complex."""
        html = """
        <table>
            <tr><th>Header</th></tr>
            <tr><td>Cell</td></tr>
        </table>
        """

        analyzer = TableAnalyzer()
        analyzer.feed(html)

        assert not analyzer.is_complex()

    def test_table_with_rowspan_is_complex(self):
        """Test table with rowspan is marked as complex."""
        html = """
        <table>
            <tr><td rowspan="2">Merged</td><td>Cell</td></tr>
            <tr><td>Cell</td></tr>
        </table>
        """

        analyzer = TableAnalyzer()
        analyzer.feed(html)

        assert analyzer.has_rowspan
        assert analyzer.is_complex()

    def test_table_with_colspan_is_complex(self):
        """Test table with colspan is marked as complex."""
        html = """
        <table>
            <tr><td colspan="2">Merged</td></tr>
            <tr><td>Cell1</td><td>Cell2</td></tr>
        </table>
        """

        analyzer = TableAnalyzer()
        analyzer.feed(html)

        assert analyzer.has_colspan
        assert analyzer.is_complex()

    def test_table_with_nested_tags_is_complex(self):
        """Test table with complex nested tags is marked as complex."""
        html = """
        <table>
            <tr><td><div>Nested</div></td></tr>
        </table>
        """

        analyzer = TableAnalyzer()
        analyzer.feed(html)

        assert analyzer.has_nested_tags
        assert analyzer.is_complex()

    def test_table_with_simple_nested_tags_not_complex(self):
        """Test table with simple formatting tags is not complex."""
        html = """
        <table>
            <tr><td><strong>Bold</strong> and <em>italic</em></td></tr>
            <tr><td><a href="/link">Link</a></td></tr>
            <tr><td><code>code</code></td></tr>
        </table>
        """

        analyzer = TableAnalyzer()
        analyzer.feed(html)

        # Simple formatting tags should not trigger complexity
        assert not analyzer.is_complex()


class TestShouldUseHtmlFallback:
    """Tests for HTML fallback decision."""

    def test_simple_table_no_fallback(self):
        """Test simple table doesn't need HTML fallback."""
        html = """
        <table>
            <tr><th>Header</th></tr>
            <tr><td>Cell</td></tr>
        </table>
        """

        assert not should_use_html_fallback(html, hybrid_mode=True)

    def test_complex_table_needs_fallback(self):
        """Test complex table needs HTML fallback."""
        html = """
        <table>
            <tr><td rowspan="2">Merged</td><td>Cell</td></tr>
            <tr><td>Cell</td></tr>
        </table>
        """

        assert should_use_html_fallback(html, hybrid_mode=True)

    def test_hybrid_mode_disabled_no_fallback(self):
        """Test hybrid mode disabled never uses fallback."""
        html = """
        <table>
            <tr><td rowspan="2">Merged</td></tr>
        </table>
        """

        assert not should_use_html_fallback(html, hybrid_mode=False)


class TestExtractTableCells:
    """Tests for table cell extraction."""

    def test_extract_simple_table(self):
        """Test extracting cells from simple table."""
        html = """
        <table>
            <tr><th>H1</th><th>H2</th></tr>
            <tr><td>A1</td><td>A2</td></tr>
            <tr><td>B1</td><td>B2</td></tr>
        </table>
        """

        rows = extract_table_cells(html)

        assert len(rows) == 3
        assert rows[0] == ["H1", "H2"]
        assert rows[1] == ["A1", "A2"]
        assert rows[2] == ["B1", "B2"]

    def test_extract_strips_whitespace(self):
        """Test cell extraction strips whitespace."""
        html = """
        <table>
            <tr><td>  Content with spaces  </td></tr>
        </table>
        """

        rows = extract_table_cells(html)

        assert rows[0][0] == "Content with spaces"

    def test_extract_empty_cells(self):
        """Test extracting empty cells."""
        html = """
        <table>
            <tr><td></td><td>Content</td></tr>
        </table>
        """

        rows = extract_table_cells(html)

        assert rows[0][0] == ""
        assert rows[0][1] == "Content"

    def test_extract_mixed_th_td(self):
        """Test extracting from mixed th/td rows."""
        html = """
        <table>
            <tr><th>Header</th></tr>
            <tr><td>Data</td></tr>
        </table>
        """

        rows = extract_table_cells(html)

        assert len(rows) == 2
        assert rows[0] == ["Header"]
        assert rows[1] == ["Data"]
