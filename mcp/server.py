import logging
from config import Config
from fastmcp import FastMCP
from logging_utils import truncate
from utils.scrape_utils import scrape_website, web_search
from utils.slack_utils import send_to_slack_channel
from utils.typesense_client import get_typesense_client, ensure_collections
from tools.search import search_transcripts
from tools.filter import filter_by_industry, filter_by_speaker
from tools.metadata import get_episode_metadata, list_speakers, list_industries

logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

mcp = FastMCP("aicmo-tools")


# --- Web Tools ---

@mcp.tool()
def web_search_tool(query: str, num_results: int = 5) -> dict:
    """
    Search the web for information using a query string.
    Returns a list of results with title, url, and description.

    Args:
        query : The search query string to look up on the web.
        num_results : Number of search results to return.
    """
    logger.info(f"web_search_tool called | query={query!r}, num_results={num_results}")
    result = web_search(query=query, num_results=num_results)
    logger.info(f"web_search_tool returned | {truncate(result)}")
    return result


@mcp.tool()
def scrape_website_tool(
    url: str,
    render_js: bool = False,
    extract_rules: dict | None = None,
    wait: int | None = None,
    premium_proxy: bool = False,
) -> dict:
    """
    Scrape a website and return its content.
    Optionally extract structured data using CSS/XPath selectors via extract_rules.

    Args:
        url : The URL of the website to scrape.
        render_js : Whether to render JavaScript on the page. Uses more credits if enabled.
        extract_rules : CSS/XPath extraction rules for pulling structured data from the page.
        wait : Milliseconds to wait before capturing the page content.
        premium_proxy : Use premium residential proxies for hard-to-scrape sites.
    """
    logger.info(f"scrape_website_tool called | url={url!r}, render_js={render_js}, wait={wait}")
    result = scrape_website(
        url=url,
        render_js=render_js,
        extract_rules=extract_rules,
        wait=wait,
        premium_proxy=premium_proxy,
    )
    logger.info(f"scrape_website_tool returned | {truncate(result)}")
    return result


# --- Transcript Search Tools ---

@mcp.tool()
def search_transcripts_tool(
    query: str,
    limit: int = 10,
    industry: str | None = None,
    speaker: str | None = None,
) -> list[dict]:
    """
    Hybrid search (semantic + keyword) across podcast transcript chunks.
    Returns relevant passages with speaker, episode, and timestamp info.

    Args:
        query : The search query to find relevant transcript content.
        limit : Maximum number of results to return.
        industry : Optional industry filter to narrow results.
        speaker : Optional speaker name filter to narrow results.
    """
    logger.info(f"search_transcripts_tool called | query={query!r}, limit={limit}, industry={industry!r}, speaker={speaker!r}")
    result = search_transcripts(query=query, limit=limit, industry=industry, speaker=speaker)
    logger.info(f"search_transcripts_tool returned | {len(result)} results | {truncate(result)}")
    return result


@mcp.tool()
def filter_by_industry_tool(industry: str, limit: int = 10) -> list[dict]:
    """
    Filter episodes by industry category.
    Returns matching episodes with metadata.

    Args:
        industry : The industry name to filter by.
        limit : Maximum number of episodes to return.
    """
    logger.info(f"filter_by_industry_tool called | industry={industry!r}, limit={limit}")
    result = filter_by_industry(industry=industry, limit=limit)
    logger.info(f"filter_by_industry_tool returned | {len(result)} results | {truncate(result)}")
    return result


@mcp.tool()
def filter_by_speaker_tool(speaker_name: str, limit: int = 10) -> list[dict]:
    """
    Find transcript chunks by a specific speaker.
    Returns chunks spoken by that person with episode context.

    Args:
        speaker_name : The name of the speaker to search for.
        limit : Maximum number of chunks to return.
    """
    logger.info(f"filter_by_speaker_tool called | speaker_name={speaker_name!r}, limit={limit}")
    result = filter_by_speaker(speaker_name=speaker_name, limit=limit)
    logger.info(f"filter_by_speaker_tool returned | {len(result)} results | {truncate(result)}")
    return result


# --- Metadata Tools ---

@mcp.tool()
def get_episode_metadata_tool(episode_id: str) -> dict:
    """
    Retrieve full metadata for a specific episode.
    Returns title, guests, industry, tags, summary, and link.

    Args:
        episode_id : The unique identifier of the episode.
    """
    logger.info(f"get_episode_metadata_tool called | episode_id={episode_id!r}")
    result = get_episode_metadata(episode_id=episode_id)
    logger.info(f"get_episode_metadata_tool returned | {truncate(result)}")
    return result


@mcp.tool()
def list_speakers_tool() -> list[dict]:
    """
    List all unique speakers across all podcast episodes.
    Returns speaker names with the number of chunks they appear in.
    """
    logger.info("list_speakers_tool called")
    result = list_speakers()
    logger.info(f"list_speakers_tool returned | {len(result)} speakers | {truncate(result)}")
    return result


@mcp.tool()
def list_industries_tool() -> list[dict]:
    """
    List all unique industries from the podcast episodes.
    Returns industry names with episode counts.
    """
    logger.info("list_industries_tool called")
    result = list_industries()
    logger.info(f"list_industries_tool returned | {len(result)} industries | {truncate(result)}")
    return result


# --- Slack Tools ---

@mcp.tool()
def send_slack_message_tool(header: str, message: str) -> str:
    """
    Send a message to Slack via webhook.
    Returns the HTTP status code of the Slack API response.

    Args:
        header : The header text for the Slack message.
        message : The main content of the Slack message in Markdown format.
    """
    logger.info(f"send_slack_message_tool called | header={header!r}, message={truncate(message)}")
    response = send_to_slack_channel(header=header, message=message)
    result = f"Status: {response.status_code}"
    logger.info(f"send_slack_message_tool returned | {result}")
    return result


# Ensure Typesense collections exist on startup
try:
    client = get_typesense_client()
    ensure_collections(client)
    logger.info("Typesense collections initialized")
except Exception as e:
    logger.warning(f"Could not initialize Typesense collections: {e}")

app = mcp.http_app()
