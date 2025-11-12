from html_to_markdown.metrics import HtmlStats, extract_html_stats, score_conversion


def test_extract_html_stats_counts_expected_elements():
    html = (
        "<html><body>"
        "<h1>A</h1><h2>B</h2>"
        '<a href="/x">link</a>'
        "<table><tr><td>1</td></tr></table>"
        "<img src='x.png' alt='x'/>"
        "<pre><code>print('hi')</code></pre>"
        "</body></html>"
    )
    stats = extract_html_stats(html)
    assert stats.headings == 2
    assert stats.links == 1
    assert stats.tables == 1
    assert stats.images == 1
    assert stats.code_blocks == 1


def test_score_conversion_ratios_capped_at_one():
    # Original has single of each, converted intentionally duplicates headings/links
    original = HtmlStats(headings=1, links=1, tables=1, images=1, code_blocks=1)
    md = (
        "# A\n# Extra Heading\n"
        "[text](url) [another](url2)\n"
        "| col1 | col2 |\n| --- | --- |\n"
        "![alt](x.png)\n"
        "```python\nprint('hi')\n```\n"
    )
    scores = score_conversion(original, md)
    for _k, v in scores.items():
        assert 0.0 <= v <= 1.0
        assert v == 1.0  # All should cap at 1


def test_score_conversion_zero_expected_gives_one():
    # If original had none, metric should default to 1 (no expectation)
    original = HtmlStats(headings=0, links=0, tables=0, images=0, code_blocks=0)
    md = ""  # empty markdown
    scores = score_conversion(original, md)
    for v in scores.values():
        assert v == 1.0
