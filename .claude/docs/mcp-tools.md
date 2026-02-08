# MCP Tools Reference

## Overview

The FastMCP server (`mcp/server.py`) exposes 9 tools that agents use to query data and
interact with external services. All tools are accessible via SSE transport at `MCP_URL`.

## Tool Inventory

### Search Tools (`mcp/tools/search.py`)

**search_transcripts_tool**
- Searches transcript chunks in Typesense using hybrid (keyword + semantic) search
- Args: `query` (search text), `per_page` (results count, default 10)
- Returns ranked transcript chunks with episode, speaker, and timestamp info

### Filter Tools (`mcp/tools/filter.py`)

**filter_by_industry**
- Filters transcript chunks by industry/category
- Args: `industry` (industry name), `query` (optional search within industry)

**filter_by_speaker**
- Filters transcript chunks by speaker name
- Args: `speaker` (speaker name), `query` (optional search within speaker's content)

### Metadata Tools (`mcp/tools/metadata.py`)

**get_episode_metadata**
- Retrieves full metadata for a specific episode
- Args: `episode_title` (title to look up)

**list_speakers**
- Lists all unique speakers across all episodes
- Args: none

**list_industries**
- Lists all unique industries/categories
- Args: none

### Utility Tools (`mcp/utils/`)

**web_search** (`mcp/utils/scrape_utils.py`)
- Performs web search via ScrapingBee Google Search API
- Args: `query` (search terms), `num_results` (default 5)

**scrape_website** (`mcp/utils/scrape_utils.py`)
- Scrapes and extracts text content from a URL via ScrapingBee
- Args: `url` (page to scrape)

**send_slack_message** (`mcp/utils/slack_utils.py`)
- Sends a message to the configured Slack channel via webhook
- Args: `message` (text to send)

## Code Style for MCP Tools

All MCP tool functions **must** include an `Args` block in the docstring:

```python
@mcp.tool()
async def my_tool(param1: str, param2: int = 10) -> str:
    """Brief description of what this tool does.

    Args:
        param1 : Description of param1
        param2 : Description of param2 (default: 10)
    """
```

This is required for proper tool schema generation by FastMCP.

## Adding New Tools

1. Create or edit a file in `mcp/tools/`
2. Decorate with `@mcp.tool()`
3. Include Args docstring block for all parameters
4. Import and register in `mcp/server.py`
5. Add tests in `tests/mcp/`
