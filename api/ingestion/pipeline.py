import logging
import os
import typesense
from config import Config
from ingestion.vtt_parser import parse_vtt
from ingestion.chunker import chunk_segments
from ingestion.speaker_detector import detect_speakers
from ingestion.metadata_extractor import extract_metadata, extract_from_filename

logger = logging.getLogger(__name__)


def _get_typesense_client() -> typesense.Client:
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


async def ingest_file(file_path: str) -> dict:
    """
    Run the full ingestion pipeline for a single VTT file.

    Flow: parse VTT → detect speakers → extract metadata → chunk → upsert to Typesense
    """
    logger.info(f"ingest_file called | file_path={file_path!r}")
    filename = os.path.basename(file_path)
    logger.info(f"Starting ingestion for: {filename}")

    # Step 1: Parse VTT
    segments = parse_vtt(file_path)
    logger.info(f"Parsed {len(segments)} merged segments")

    # Step 2: Extract metadata (includes guest name from filename)
    metadata = await extract_metadata(filename, segments)
    logger.info(f"Extracted metadata: {metadata.title}")

    # Step 3: Detect speakers
    guest_name = metadata.guest_names[0] if metadata.guest_names else extract_from_filename(filename).get("guest_name", "")
    labeled_segments = await detect_speakers(segments, guest_name)
    logger.info(f"Labeled {len(labeled_segments)} segments with speakers")

    # Step 4: Chunk
    episode_id = filename.replace(".vtt", "").replace(" ", "_").lower()
    chunks = chunk_segments(
        segments=labeled_segments,
        episode_id=episode_id,
        metadata=metadata.model_dump(),
    )
    logger.info(f"Created {len(chunks)} chunks")

    # Step 5: Upsert to Typesense
    client = _get_typesense_client()

    episode_doc = {
        "id": episode_id,
        **metadata.model_dump(exclude={"source_file"}),
        "source_file": filename,
    }
    client.collections["episodes"].documents.upsert(episode_doc)
    logger.info(f"Upserted episode: {episode_id}")

    for i, chunk in enumerate(chunks):
        chunk_doc = {
            "id": f"{episode_id}_chunk_{i}",
            **chunk.model_dump(),
        }
        client.collections["transcript_chunks"].documents.upsert(chunk_doc)

    logger.info(f"Upserted {len(chunks)} chunks for {episode_id}")

    result = {
        "status": "success",
        "episode_id": episode_id,
        "chunks_created": len(chunks),
    }
    logger.info(f"ingest_file returned | {result}")
    return result


async def ingest_directory(directory_path: str) -> dict:
    """Ingest all VTT files in a directory."""
    logger.info(f"ingest_directory called | directory_path={directory_path!r}")
    vtt_files = [
        os.path.join(directory_path, f)
        for f in os.listdir(directory_path)
        if f.endswith(".vtt")
    ]

    results = []
    for file_path in vtt_files:
        result = await ingest_file(file_path)
        results.append(result)

    result = {
        "status": "success",
        "episodes_processed": len(results),
    }
    logger.info(f"ingest_directory returned | {result}")
    return result
