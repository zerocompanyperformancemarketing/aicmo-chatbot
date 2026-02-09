import logging
from logging_utils import truncate
from utils.typesense_client import get_typesense_client

logger = logging.getLogger(__name__)


def get_episode_metadata(episode_id: str) -> dict:
    """
    Retrieve full episode metadata from the episodes collection.

    Returns title, guest, industry, tags, summary, link.
    """
    logger.info(f"get_episode_metadata called | episode_id={episode_id!r}")
    client = get_typesense_client()

    try:
        doc = client.collections["episodes"].documents[episode_id].retrieve()
        result = {
            "id": doc.get("id", ""),
            "title": doc.get("title", ""),
            "guest_names": doc.get("guest_names", []),
            "host_names": doc.get("host_names", []),
            "industry": doc.get("industry", ""),
            "topic_tags": doc.get("topic_tags", []),
            "summary": doc.get("summary", ""),
            "episode_link": doc.get("episode_link", ""),
            "duration_seconds": doc.get("duration_seconds", 0),
        }
        logger.info(f"get_episode_metadata returned | {truncate(result)}")
        return result
    except Exception:
        logger.info(f"get_episode_metadata returned | episode not found")
        return {"error": f"Episode '{episode_id}' not found"}


def list_speakers() -> list[dict]:
    """
    Aggregate unique speakers across all episodes.

    Returns speaker names with episode counts.
    """
    logger.info("list_speakers called")
    client = get_typesense_client()

    results = client.collections["transcript_chunks"].documents.search({
        "q": "*",
        "facet_by": "speaker",
        "per_page": 0,
        "max_facet_values": 100,
    })

    speakers = []
    for facet in results.get("facet_counts", []):
        if facet["field_name"] == "speaker":
            for value in facet["counts"]:
                speakers.append({
                    "speaker": value["value"],
                    "chunk_count": value["count"],
                })

    logger.info(f"list_speakers returned | {len(speakers)} speakers | {truncate(speakers)}")
    return speakers


def list_industries() -> list[dict]:
    """
    Aggregate unique industries from the episodes collection.

    Returns industry names with episode counts.
    """
    logger.info("list_industries called")
    client = get_typesense_client()

    results = client.collections["episodes"].documents.search({
        "q": "*",
        "facet_by": "industry",
        "per_page": 0,
        "max_facet_values": 100,
    })

    industries = []
    for facet in results.get("facet_counts", []):
        if facet["field_name"] == "industry":
            for value in facet["counts"]:
                industries.append({
                    "industry": value["value"],
                    "episode_count": value["count"],
                })

    logger.info(f"list_industries returned | {len(industries)} industries | {truncate(industries)}")
    return industries
