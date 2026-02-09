import typesense
from config import Config


def get_typesense_client() -> typesense.Client:
    """Return a configured Typesense client."""
    return typesense.Client({
        "nodes": [{
            "host": Config.TS_HOST,
            "port": Config.TS_PORT,
            "protocol": "http",
        }],
        "api_key": Config.TS_API_KEY,
        "connection_timeout_seconds": 10,
    })


def ensure_collections(client: typesense.Client) -> None:
    """Create Typesense collections if they don't exist."""
    episodes_schema = {
        "name": "episodes",
        "fields": [
            {"name": "title", "type": "string"},
            {"name": "guest_names", "type": "string[]"},
            {"name": "host_names", "type": "string[]"},
            {"name": "industry", "type": "string", "facet": True},
            {"name": "topic_tags", "type": "string[]", "facet": True},
            {"name": "episode_link", "type": "string", "optional": True},
            {"name": "summary", "type": "string"},
            {"name": "duration_seconds", "type": "int32"},
            {"name": "source_file", "type": "string"},
        ],
    }

    chunks_schema = {
        "name": "transcript_chunks",
        "fields": [
            {"name": "episode_id", "type": "string", "reference": "episodes.id"},
            {"name": "text", "type": "string"},
            {"name": "speaker", "type": "string", "facet": True},
            {"name": "start_time", "type": "float"},
            {"name": "end_time", "type": "float"},
            {"name": "chunk_index", "type": "int32"},
            {"name": "guest_names", "type": "string[]"},
            {"name": "industry", "type": "string", "facet": True},
            {"name": "topic_tags", "type": "string[]", "facet": True},
            {
                "name": "embedding",
                "type": "float[]",
                "num_dim": 3072,
                "embed": {
                    "from": ["text"],
                    "model_config": {
                        "model_name": "openai/text-embedding-3-large",
                        "api_key": Config.OPENAI_API_KEY,
                    },
                },
            },
        ],
    }

    existing = {c["name"] for c in client.collections.retrieve()}

    if "episodes" not in existing:
        client.collections.create(episodes_schema)

    if "transcript_chunks" not in existing:
        client.collections.create(chunks_schema)
