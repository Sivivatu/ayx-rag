from html_to_markdown.strategies.markdownify_adapter import MarkdownifyStrategy


def test_markdownify_strategy_metadata_and_availability():
    s = MarkdownifyStrategy()
    assert s.name == "markdownify"
    # Should report availability even if version probe fails gracefully
    assert isinstance(s.available(), bool)


def test_markdownify_converts_minimal_html():
    s = MarkdownifyStrategy()
    md = s.convert("<h1>Title</h1><p>Hello</p>")
    assert "Title" in md
    assert "Hello" in md
