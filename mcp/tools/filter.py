import logging
from logging_utils import truncate
from utils.typesense_client import get_typesense_client

logger = logging.getLogger(__name__)


def filter_by_industry(industry: str, limit: int = 10) -> list[dict]:
    """
    Faceted search on episodes collection by industry.

    Returns matching episodes with metadata.
    """
    logger.info(f"filter_by_industry called | industry={industry!r}, limit={limit}")

    # Require a non-empty industry to avoid returning too many results
    if not industry or not industry.strip():
        raise ValueError("industry is required and cannot be empty")

    client = get_typesense_client()

    # Wrap in backticks for special chars (parentheses, slashes, etc.)
    escaped = industry.replace("`", "\\`")

    search_params = {
        "q": "*",
        "per_page": limit,
        "filter_by": f"industry:=`{escaped}`",
        "include_fields": "id,title,guest_names,host_names,industry,topic_tags,summary,episode_link",
    }

    results = client.collections["episodes"].documents.search(search_params)

    result = [
        {
            "id": hit["document"]["id"],
            "title": hit["document"].get("title", ""),
            "guest_names": hit["document"].get("guest_names", []),
            "industry": hit["document"].get("industry", ""),
            "topic_tags": hit["document"].get("topic_tags", []),
            "summary": hit["document"].get("summary", ""),
            "episode_link": hit["document"].get("episode_link", ""),
        }
        for hit in results.get("hits", [])
    ]
    logger.info(f"filter_by_industry returned | {len(result)} results | {truncate(result)}")
    return result


def filter_by_speaker(speaker_name: str, limit: int = 10) -> list[dict]:
    """
    Search transcript_chunks where speaker matches.

    Returns chunks spoken by that person with episode context.
    """
    logger.info(f"filter_by_speaker called | speaker_name={speaker_name!r}, limit={limit}")

    # Require a non-empty speaker_name to avoid returning too many results
    if not speaker_name or not speaker_name.strip():
        raise ValueError("speaker_name is required and cannot be empty")

    client = get_typesense_client()

    # Wrap in backticks for special chars
    escaped = speaker_name.replace("`", "\\`")

    search_params = {
        "q": "*",
        "per_page": limit,
        "filter_by": f"speaker:=`{escaped}`",
        "include_fields": "text,speaker,episode_id,start_time,end_time,chunk_index",
    }

    results = client.collections["transcript_chunks"].documents.search(search_params)

    result = [
        {
            "text": hit["document"]["text"],
            "speaker": hit["document"].get("speaker", ""),
            "episode_id": hit["document"].get("episode_id", ""),
            "start_time": hit["document"].get("start_time", 0),
            "end_time": hit["document"].get("end_time", 0),
        }
        for hit in results.get("hits", [])
    ]
    logger.info(f"filter_by_speaker returned | {len(result)} results | {truncate(result)}")
    return result
