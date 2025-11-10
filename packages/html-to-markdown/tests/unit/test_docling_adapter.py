import pytest

from html_to_markdown.strategies.docling_adapter import DoclingStrategy


def test_docling_strategy_metadata_and_availability():
    s = DoclingStrategy()
    assert s.name == "docling"
    assert isinstance(s.available(), bool)
    assert isinstance(s.version(), str)


def test_docling_convert_behaviour_depends_on_availability():
    s = DoclingStrategy()
    html = "<h1>Docling</h1><p>Test</p>"
    if not s.available():
        with pytest.raises(RuntimeError):
            s.convert(html)
    else:
        out = s.convert(html)
        assert isinstance(out, str)
        assert "Docling" in out and "Test" in out
