# Feature Specification: Sitemap Filter CLI

**Feature Branch**: `001-sitemap-filter`  
**Created**: 2025-10-30  
**Status**: Draft  
**Input**: User description: "create a sitemap processing script that will focus the sitemap list to specific products and languages via cli commands"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Filter by Language (Priority: P1)

A developer wants to extract only English documentation URLs from the sitemap containing 35,460 mixed-language URLs to reduce processing scope for the initial RAG system implementation.

**Why this priority**: Filtering by language is the most critical feature as the project's constitution mandates focusing exclusively on English documentation first. This reduces the dataset from 35k to approximately 17k URLs, enabling faster development cycles.

**Independent Test**: Can be fully tested by running the filter script with a language parameter and verifying that all output URLs match the specified language pattern (e.g., no `/de/` paths when filtering for English).

**Acceptance Scenarios**:

1. **Given** the full Alteryx sitemap XML file, **When** user runs filter with `--language en` flag, **Then** output contains only English URLs (those without locale prefixes like `/de/`)
2. **Given** the full sitemap, **When** user runs filter with `--language de` flag, **Then** output contains only German URLs (those with `/de/` locale prefix)
3. **Given** the full sitemap, **When** user specifies an invalid language code, **Then** script displays clear error message with list of available languages
4. **Given** an empty or malformed sitemap file, **When** user attempts to filter, **Then** script displays appropriate error message without crashing

---

### User Story 2 - Filter by Product Path (Priority: P2)

A developer wants to extract documentation URLs for specific Alteryx products (e.g., only "designer" or only "server") to build focused RAG systems for individual product areas.

**Why this priority**: Product-specific filtering enables incremental RAG system development. Teams can build and test the system on a smaller, focused dataset (e.g., 5k Designer URLs) before scaling to all products.

**Independent Test**: Can be fully tested by running the filter with a product path parameter and verifying all output URLs contain that path segment, delivering immediate value for product-specific documentation projects.

**Acceptance Scenarios**:

1. **Given** the full sitemap, **When** user runs filter with `--product designer` flag, **Then** output contains only URLs with `/designer/` path segment
2. **Given** the full sitemap, **When** user runs filter with `--product server` flag, **Then** output contains only URLs with `/server/` path segment
3. **Given** the sitemap, **When** user provides multiple product filters with `--product designer --product server`, **Then** output contains URLs matching any of the specified products
4. **Given** the sitemap, **When** user specifies a product path that doesn't exist, **Then** script returns empty result with informative message

---

### User Story 3 - Combine Multiple Filters (Priority: P3)

A developer wants to apply both language and product filters simultaneously to extract a precise subset of documentation (e.g., English Designer docs only).

**Why this priority**: Combined filtering provides maximum flexibility but depends on individual filters working first. It's valuable for advanced use cases and complex dataset requirements.

**Independent Test**: Can be fully tested by running the script with multiple filter flags and verifying output matches all specified criteria, demonstrating the power of composable filters.

**Acceptance Scenarios**:

1. **Given** the full sitemap, **When** user runs filter with `--language en --product designer` flags, **Then** output contains only English URLs with `/designer/` path
2. **Given** the full sitemap, **When** user combines `--language de --product server --product connect`, **Then** output contains German URLs for both server and connect products
3. **Given** filter criteria that match no URLs, **When** user runs the script, **Then** script outputs empty result with message indicating no matches found

---

### User Story 4 - Output Format Options (Priority: P4)

A developer wants to output filtered results in different formats (default JSON, plain text list, or filtered XML) to integrate with various downstream processing tools.

**Why this priority**: Format flexibility improves script utility across different workflows, but core filtering functionality is more critical.

**Independent Test**: Can be fully tested by running the script with format flags and verifying output structure matches the specified format, enabling seamless tool integration.

**Acceptance Scenarios**:

1. **Given** filtered URLs, **When** user doesnt specify a format flag, **Then** output is valid JSON array with URL and lastmod data
2. **Given** filtered URLs, **When** user specifies `--format json` flag(default), **Then** output is valid JSON array with URL and lastmod data
3. **Given** filtered URLs, **When** user specifies `--format txt` flag, **Then** output is plain text with one URL per line
4. **Given** filtered URLs, **When** user specifies `--format xml` flag, **Then** output is valid sitemap XML containing only filtered URLs
5. **Given** filtered URLs, **When** user outputs to file with `--output result.json`, **Then** results are written to specified file instead of stdout

---

### Edge Cases

- What happens when sitemap XML is malformed or missing required elements?
- How does system handle sitemap files with different encodings?
- What if user provides conflicting filters (e.g., filter for both language 'en' and path '/de/')?
- How does script perform with very large sitemap files (100k+ URLs)?
- What happens when lastmod dates are missing or in unexpected formats?
- How does system handle URLs with query parameters or fragments?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Script MUST accept an input sitemap XML file path as a required argument
- **FR-002**: Script MUST support `--language` flag to filter URLs by locale (e.g., `en`, `de`)
- **FR-003**: Script MUST support `--product` flag to filter URLs by product path segment (e.g., `designer`, `server`)
- **FR-004**: Script MUST allow multiple `--product` flags to filter for multiple products (OR logic)
- **FR-005**: Script MUST combine multiple filter types using AND logic (e.g., language AND product)
- **FR-006**: Script MUST validate XML structure and provide clear error messages for malformed input
- **FR-007**: Script MUST support output format options via `--format` flag: `txt` (default), `json`, `xml`
- **FR-008**: Script MUST preserve `lastmod` timestamps from original sitemap in all output formats
- **FR-009**: Script MUST write output to stdout by default or to file specified with `--output` flag
- **FR-010**: Script MUST display help information with `--help` flag showing all available options
- **FR-011**: Script MUST provide version information with `--version` flag
- **FR-012**: Script MUST return non-zero exit code on errors and zero on success
- **FR-013**: Script MUST handle large sitemap files (35k+ URLs) efficiently without excessive memory usage
- **FR-014**: Script MUST detect English URLs by absence of locale prefix (default language assumption)
- **FR-015**: Script MUST display count of filtered URLs and total URLs processed
- **FR-016**: Script MUST support `--dry-run` flag to show filter statistics without outputting URLs

### Key Entities

- **URL Entry**: Represents a single sitemap URL entry with attributes:
  - `loc`: The full URL string
  - `lastmod`: Last modification date in ISO format (YYYY-MM-DD)
  - `language`: Detected language code (en, de, or detected from path)
  - `product`: Detected product path segment(s)

- **Filter Criteria**: Represents user-specified filtering rules with attributes:
  - `languages`: List of language codes to include
  - `products`: List of product path segments to include
  - `combination_logic`: How filters combine (AND across types, OR within type)

- **Sitemap**: Represents the XML document structure with attributes:
  - `url_entries`: Collection of URL Entry objects
  - `total_count`: Total number of URLs in original sitemap
  - `filtered_count`: Number of URLs after applying filters

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can filter 35,460-URL sitemap and receive results in under 3 seconds on standard hardware
- **SC-002**: Script correctly identifies and filters at least 99% of URLs based on language and product criteria
- **SC-003**: 100% of output formats (txt, json, xml) produce valid, parseable results
- **SC-004**: Script processes sitemap files up to 10MB in size without memory errors
- **SC-005**: Users can successfully combine language and product filters in a single command without errors
- **SC-006**: Error messages are clear and actionable - users can identify and fix issues within 1 minute
- **SC-007**: Script execution with invalid parameters fails fast (under 1 second) with helpful error messages
- **SC-008**: 90% of users successfully filter sitemap on first attempt without consulting documentation beyond `--help`
- **SC-009**: All filtered URLs preserve their original `lastmod` timestamps with 100% accuracy
- **SC-010**: Memory usage remains below 500MB even for 100k-URL sitemaps

## Assumptions

- English documentation URLs lack explicit locale prefix (pattern: `help.alteryx.com/current/{path}`)
- Non-English URLs include locale prefix (pattern: `help.alteryx.com/current/{locale}/{path}`)
- Product identification relies on consistent path segment patterns in URLs
- XML sitemap follows standard sitemap protocol schema (http://www.sitemaps.org/schemas/sitemap/0.9)
- Users have Python 3.11+ installed (per project requirements)
- Script will be invoked via `uv run` per project package management standards
- Default output format is plain text (one URL per line) for easy piping to other tools
