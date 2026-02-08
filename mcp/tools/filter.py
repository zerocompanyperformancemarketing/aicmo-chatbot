from utils.typesense_client import get_typesense_client


def filter_by_industry(industry: str, limit: int = 10) -> list[dict]:
    """
    Faceted search on episodes collection by industry.

    Returns matching episodes with metadata.
    """
    client = get_typesense_client()

    results = client.collections["episodes"].documents.search({
        "q": "*",
        "filter_by": f"industry:={industry}",
        "per_page": limit,
        "include_fields": "id,title,guest_names,host_names,industry,topic_tags,summary,episode_link",
    })

    return [
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


def filter_by_speaker(speaker_name: str, limit: int = 10) -> list[dict]:
    """
    Search transcript_chunks where speaker matches.

    Returns chunks spoken by that person with episode context.
    """
    client = get_typesense_client()

    results = client.collections["transcript_chunks"].documents.search({
        "q": "*",
        "filter_by": f"speaker:={speaker_name}",
        "per_page": limit,
        "include_fields": "text,speaker,episode_id,start_time,end_time,chunk_index",
    })

    return [
        {
            "text": hit["document"]["text"],
            "speaker": hit["document"].get("speaker", ""),
            "episode_id": hit["document"].get("episode_id", ""),
            "start_time": hit["document"].get("start_time", 0),
            "end_time": hit["document"].get("end_time", 0),
        }
        for hit in results.get("hits", [])
    ]
