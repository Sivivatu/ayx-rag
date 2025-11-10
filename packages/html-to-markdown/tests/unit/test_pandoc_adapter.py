import pytest

from html_to_markdown.strategies.pandoc_adapter import PandocStrategy


def test_pandoc_strategy_metadata_and_availability():
    s = PandocStrategy()
    assert s.name == "pandoc"
    assert isinstance(s.available(), bool)
    assert isinstance(s.version(), str)


def test_pandoc_convert_behaviour_depends_on_availability():
    s = PandocStrategy()
    html = "<h1>Title</h1><p>Hello</p>"
    if not s.available():
        with pytest.raises(RuntimeError):
            s.convert(html)
    else:
        out = s.convert(html)
        assert isinstance(out, str)
        # Pandoc to GFM should preserve headings/text
        assert "Title" in out and "Hello" in out
