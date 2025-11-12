from html_to_markdown.metrics import (
    DEFAULT_WEIGHTS,
    HtmlStats,
    compute_weighted_score,
    extract_html_stats,
    score_conversion,
)


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


def test_compute_weighted_score_default_weights():
    """Should compute weighted score with default weights."""
    metrics = {
        "heading_fidelity": 1.0,
        "link_preservation": 1.0,
        "table_preservation": 1.0,
        "code_block_integrity": 1.0,
        "image_alt_coverage": 1.0,
    }
    score = compute_weighted_score(metrics)
    assert score == 1.0


def test_compute_weighted_score_custom_weights():
    """Should compute weighted score with custom weights."""
    metrics = {
        "heading_fidelity": 0.8,
        "link_preservation": 0.9,
        "table_preservation": 0.7,
        "code_block_integrity": 0.6,
        "image_alt_coverage": 0.5,
    }
    weights = {
        "heading_fidelity": 0.5,  # Half the weight on headings
        "link_preservation": 0.3,
        "table_preservation": 0.1,
        "code_block_integrity": 0.05,
        "image_alt_coverage": 0.05,
    }
    score = compute_weighted_score(metrics, weights)
    expected = 0.8 * 0.5 + 0.9 * 0.3 + 0.7 * 0.1 + 0.6 * 0.05 + 0.5 * 0.05
    assert abs(score - expected) < 0.001


def test_compute_weighted_score_normalizes_weights():
    """Should normalize weights if they don't sum to 1.0."""
    metrics = {
        "heading_fidelity": 0.8,
        "link_preservation": 0.9,
        "table_preservation": 0.7,
        "code_block_integrity": 0.6,
        "image_alt_coverage": 0.5,
    }
    # Weights sum to 2.0
    weights = {
        "heading_fidelity": 0.5,
        "link_preservation": 0.5,
        "table_preservation": 0.4,
        "code_block_integrity": 0.3,
        "image_alt_coverage": 0.3,
    }
    score = compute_weighted_score(metrics, weights)
    # Should normalize: 0.25, 0.25, 0.2, 0.15, 0.15
    expected = 0.8 * 0.25 + 0.9 * 0.25 + 0.7 * 0.2 + 0.6 * 0.15 + 0.5 * 0.15
    assert abs(score - expected) < 0.001


def test_compute_weighted_score_zero_metrics():
    """Should handle all zero metrics."""
    metrics = {
        "heading_fidelity": 0.0,
        "link_preservation": 0.0,
        "table_preservation": 0.0,
        "code_block_integrity": 0.0,
        "image_alt_coverage": 0.0,
    }
    score = compute_weighted_score(metrics)
    assert score == 0.0


def test_default_weights_sum_to_one():
    """Default weights should sum to 1.0."""
    total = sum(DEFAULT_WEIGHTS.values())
    assert abs(total - 1.0) < 0.001
