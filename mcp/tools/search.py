from utils.typesense_client import get_typesense_client


def search_transcripts(
    query: str,
    limit: int = 10,
    industry: str | None = None,
    speaker: str | None = None,
) -> list[dict]:
    """
    Hybrid search (semantic + keyword) on transcript_chunks collection.

    Returns chunk text, speaker, episode title, timestamps, and relevance score.
    """
    client = get_typesense_client()

    search_params = {
        "q": query,
        "query_by": "text,embedding",
        "per_page": limit,
        "include_fields": "text,speaker,episode_id,start_time,end_time,chunk_index,guest_names,industry,topic_tags",
    }

    filter_parts = []
    if industry:
        filter_parts.append(f"industry:={industry}")
    if speaker:
        filter_parts.append(f"speaker:={speaker}")
    if filter_parts:
        search_params["filter_by"] = " && ".join(filter_parts)

    results = client.collections["transcript_chunks"].documents.search(search_params)

    return [
        {
            "text": hit["document"]["text"],
            "speaker": hit["document"].get("speaker", ""),
            "episode_id": hit["document"].get("episode_id", ""),
            "start_time": hit["document"].get("start_time", 0),
            "end_time": hit["document"].get("end_time", 0),
            "chunk_index": hit["document"].get("chunk_index", 0),
            "industry": hit["document"].get("industry", ""),
            "topic_tags": hit["document"].get("topic_tags", []),
            "score": hit.get("text_match_info", {}).get("score", 0),
        }
        for hit in results.get("hits", [])
    ]
