"""Performance tests for HTML to Markdown conversion."""

import time
from pathlib import Path

import pytest
from html_to_markdown.converter import HtmlConverter
from html_to_markdown.models import ConversionConfig


@pytest.fixture
def standard_page_html():
    """Create a standard-sized HTML page (similar to Alteryx help pages)."""
    # Approximate size: 3-5KB with typical content structure
    return """<!DOCTYPE html>
<html>
<head>
    <title>Standard Help Page</title>
    <meta property="og:url" content="https://help.example.com/page" />
</head>
<body>
    <h1>Getting Started with the Application</h1>

    <p>This guide will help you understand the basics of using the application effectively.</p>

    <h2>Installation</h2>
    <p>To install the application, follow these steps:</p>
    <ol>
        <li>Download the installer from the official website</li>
        <li>Run the installer with administrator privileges</li>
        <li>Follow the on-screen instructions</li>
        <li>Restart your computer when prompted</li>
    </ol>

    <h2>Configuration</h2>
    <p>After installation, you'll need to configure the application:</p>

    <h3>Basic Settings</h3>
    <ul>
        <li><strong>Username:</strong> Enter your username</li>
        <li><strong>Password:</strong> Create a secure password</li>
        <li><strong>Email:</strong> Provide your email address</li>
    </ul>

    <h3>Advanced Settings</h3>
    <table>
        <tr>
            <th>Setting</th>
            <th>Default</th>
            <th>Description</th>
        </tr>
        <tr>
            <td>Max Memory</td>
            <td>2048MB</td>
            <td>Maximum memory allocation</td>
        </tr>
        <tr>
            <td>Timeout</td>
            <td>30s</td>
            <td>Operation timeout period</td>
        </tr>
        <tr>
            <td>Cache Size</td>
            <td>500MB</td>
            <td>Size of the local cache</td>
        </tr>
    </table>

    <h2>Usage Examples</h2>
    <p>Here are some common usage patterns:</p>

    <h3>Example 1: Basic Workflow</h3>
    <pre><code class="language-python">
import application

# Initialize the application
app = application.Application()

# Configure settings
app.configure({
    'username': 'user',
    'password': 'pass'
})

# Run the workflow
result = app.run()
print(result)
    </code></pre>

    <h3>Example 2: Advanced Features</h3>
    <pre><code class="language-javascript">
const app = require('application');

// Use advanced features
app.enableCaching({
    size: 1024,
    ttl: 3600
});

// Execute complex operations
const result = await app.execute({
    operation: 'transform',
    data: inputData
});
    </code></pre>

    <h2>Troubleshooting</h2>
    <p>If you encounter issues, try these solutions:</p>

    <h3>Common Problems</h3>
    <dl>
        <dt>Application won't start</dt>
        <dd>Check that all prerequisites are installed and your system meets the minimum requirements.</dd>

        <dt>Performance is slow</dt>
        <dd>Increase the memory allocation in advanced settings or clear the cache.</dd>

        <dt>Connection errors</dt>
        <dd>Verify your network settings and firewall configuration.</dd>
    </dl>

    <h2>Next Steps</h2>
    <p>Now that you've completed the basic setup:</p>
    <ul>
        <li>Explore the <a href="/tutorials">tutorials</a> section</li>
        <li>Read the <a href="/api-reference">API reference</a></li>
        <li>Join the <a href="/community">community forum</a></li>
        <li>Check out <a href="/examples">example projects</a></li>
    </ul>

    <h2>Additional Resources</h2>
    <p>For more information, see:</p>
    <ul>
        <li><a href="/docs/installation-guide">Complete Installation Guide</a></li>
        <li><a href="/docs/configuration">Configuration Reference</a></li>
        <li><a href="/docs/best-practices">Best Practices</a></li>
        <li><a href="/support">Support Portal</a></li>
    </ul>
</body>
</html>"""


def test_standard_page_conversion_under_2_seconds(tmp_path: Path, standard_page_html: str):
    """Should convert a standard help page in under 2 seconds."""
    # Create test file
    html_file = tmp_path / "standard_page.html"
    html_file.write_text(standard_page_html, encoding="utf-8")

    # Create converter with default config
    config = ConversionConfig()
    converter = HtmlConverter(config=config)

    # Time the conversion
    start = time.perf_counter()
    result = converter.convert_file(html_file, tmp_path / "output.md")
    duration = time.perf_counter() - start

    # Assert conversion completed
    assert result is not None
    assert result.markdown_content is not None

    # Assert performance requirement
    assert duration < 2.0, f"Conversion took {duration:.3f}s, expected < 2.0s"

    # Verify output quality
    assert "# Getting Started" in result.markdown_content
    assert "Installation" in result.markdown_content
    assert "|" in result.markdown_content  # Table present


def test_multiple_conversions_average_time(tmp_path: Path, standard_page_html: str):
    """Should maintain performance over multiple conversions."""
    # Create test file
    html_file = tmp_path / "page.html"
    html_file.write_text(standard_page_html, encoding="utf-8")

    # Create converter
    config = ConversionConfig()
    converter = HtmlConverter(config=config)

    # Run multiple conversions
    num_runs = 5
    durations = []

    for i in range(num_runs):
        start = time.perf_counter()
        result = converter.convert_file(html_file, tmp_path / f"output_{i}.md")
        duration = time.perf_counter() - start
        durations.append(duration)
        assert result is not None

    # Calculate average
    avg_duration = sum(durations) / len(durations)
    max_duration = max(durations)

    # Assert average is well under 2s
    assert avg_duration < 1.0, f"Average conversion took {avg_duration:.3f}s, expected < 1.0s"
    assert max_duration < 2.0, f"Max conversion took {max_duration:.3f}s, expected < 2.0s"


def test_small_page_conversion_fast(tmp_path: Path):
    """Should convert small pages very quickly."""
    html = "<h1>Title</h1><p>Simple content.</p>"
    html_file = tmp_path / "small.html"
    html_file.write_text(html, encoding="utf-8")

    config = ConversionConfig()
    converter = HtmlConverter(config=config)

    start = time.perf_counter()
    result = converter.convert_file(html_file, tmp_path / "output.md")
    duration = time.perf_counter() - start

    # Small pages should be extremely fast (< 0.5s)
    assert result is not None
    assert duration < 0.5, f"Small page took {duration:.3f}s, expected < 0.5s"


def test_large_page_still_reasonable(tmp_path: Path):
    """Should handle larger pages within reasonable time."""
    # Create a larger page (10KB+)
    large_html = """<!DOCTYPE html>
<html>
<head><title>Large Page</title></head>
<body>
    <h1>Large Documentation Page</h1>
"""

    # Add many sections
    for i in range(50):
        large_html += f"""
    <h2>Section {i}</h2>
    <p>This is section {i} with detailed content and explanations.</p>
    <ul>
        <li>Point 1 for section {i}</li>
        <li>Point 2 for section {i}</li>
        <li>Point 3 for section {i}</li>
    </ul>
"""

    large_html += "</body></html>"

    html_file = tmp_path / "large.html"
    html_file.write_text(large_html, encoding="utf-8")

    config = ConversionConfig()
    converter = HtmlConverter(config=config)

    start = time.perf_counter()
    result = converter.convert_file(html_file, tmp_path / "output.md")
    duration = time.perf_counter() - start

    # Even large pages should complete in reasonable time (< 5s)
    assert result is not None
    assert duration < 5.0, f"Large page took {duration:.3f}s, expected < 5.0s"

    # Verify content is present
    assert "Section 0" in result.markdown_content
    assert "Section 49" in result.markdown_content


def test_batch_throughput_meets_requirement(tmp_path: Path):
    """Should process at least 25 pages per minute in batch mode."""
    # Create 30 test files (representative sample)
    input_dir = tmp_path / "batch_input"
    input_dir.mkdir()

    # Create realistic pages (3-5KB each, similar to Alteryx help pages)
    for i in range(30):
        html = f"""<!DOCTYPE html>
<html>
<head><title>Page {i}</title></head>
<body>
    <h1>Documentation Page {i}</h1>
    <p>This is a realistic help documentation page with typical content structure.</p>

    <h2>Overview</h2>
    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>

    <h2>Configuration</h2>
    <table>
        <tr><th>Setting</th><th>Value</th><th>Description</th></tr>
        <tr><td>Timeout</td><td>30s</td><td>Operation timeout</td></tr>
        <tr><td>Memory</td><td>2GB</td><td>Max memory allocation</td></tr>
    </table>

    <h2>Example</h2>
    <pre><code class="language-python">
import example
result = example.process()
print(result)
    </code></pre>

    <h2>Additional Information</h2>
    <ul>
        <li><a href="/page{i + 1}">Next page</a></li>
        <li><a href="/related">Related documentation</a></li>
        <li><a href="/api">API reference</a></li>
    </ul>
</body>
</html>"""
        (input_dir / f"page{i:03d}.html").write_text(html, encoding="utf-8")

    # Run batch conversion
    from html_to_markdown.cli import app
    from typer.testing import CliRunner

    runner = CliRunner()
    output_dir = tmp_path / "batch_output"

    result = runner.invoke(app, ["batch", str(input_dir), "--out", str(output_dir)])

    assert result.exit_code == 0

    # Extract timing from output
    # Look for "Rate: X.X files/min" in output
    import re

    rate_match = re.search(r"Rate:.*?\(([\d.]+) files/min\)", result.stdout)
    assert rate_match, "Could not find conversion rate in output"

    files_per_min = float(rate_match.group(1))

    # Verify throughput meets requirement
    assert files_per_min >= 25.0, (
        f"Throughput {files_per_min:.1f} files/min does not meet requirement of ≥25 files/min"
    )

    # Verify all files were converted
    assert len(list(output_dir.glob("*.md"))) == 30
