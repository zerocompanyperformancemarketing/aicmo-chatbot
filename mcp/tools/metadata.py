from utils.typesense_client import get_typesense_client


def get_episode_metadata(episode_id: str) -> dict:
    """
    Retrieve full episode metadata from the episodes collection.

    Returns title, guest, industry, tags, summary, link.
    """
    client = get_typesense_client()

    try:
        doc = client.collections["episodes"].documents[episode_id].retrieve()
        return {
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
    except Exception:
        return {"error": f"Episode '{episode_id}' not found"}


def list_speakers() -> list[dict]:
    """
    Aggregate unique speakers across all episodes.

    Returns speaker names with episode counts.
    """
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

    return speakers


def list_industries() -> list[dict]:
    """
    Aggregate unique industries from the episodes collection.

    Returns industry names with episode counts.
    """
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

    return industries
