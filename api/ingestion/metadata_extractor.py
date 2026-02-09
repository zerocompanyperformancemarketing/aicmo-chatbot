import json
import logging
import re
from agents.utils.llm import get_llm
from models.schemas import EpisodeMetadata, ParsedCue

logger = logging.getLogger(__name__)


def extract_from_filename(filename: str) -> dict:
    """
    Extract episode title and guest name from the VTT filename.

    Expected pattern: "Title with Guest Name _unedited_.vtt"
    """
    name = filename.replace(".vtt", "").strip()
    # Remove common suffixes
    name = re.sub(r"\s*_unedited_\s*", "", name, flags=re.IGNORECASE)
    name = re.sub(r"\s*_edited_\s*", "", name, flags=re.IGNORECASE)
    name = name.strip()

    # Try to split on " with " to get title and guest
    parts = name.split(" with ", 1)
    if len(parts) == 2:
        return {"title": parts[0].strip(), "guest_name": parts[1].strip()}

    return {"title": name, "guest_name": ""}


METADATA_EXTRACTION_PROMPT = """Analyze this podcast transcript excerpt and extract metadata.

Filename: {filename}
Parsed title: {title}
Parsed guest: {guest_name}

Transcript (first ~2000 words):
{intro_text}

Transcript (last ~500 words):
{outro_text}

Extract and return a JSON object with:
- "title": episode title (use the parsed title if it's good, or improve it)
- "guest_names": array of guest names mentioned
- "host_names": array of host names mentioned
- "industry": the guest's industry/business category (single string)
- "topic_tags": array of 3-5 topic tags discussed in the episode
- "summary": 2-3 sentence summary of the episode

Return ONLY the JSON object, no other text."""


async def extract_metadata(
    filename: str,
    segments: list[ParsedCue],
) -> EpisodeMetadata:
    """Extract episode metadata from filename and transcript content using LLM."""
    logger.info(f"extract_metadata called | filename={filename!r}, segments={len(segments)}")
    file_meta = extract_from_filename(filename)

    # Build intro and outro text
    all_text = " ".join(seg.text for seg in segments)
    words = all_text.split()
    intro_text = " ".join(words[:2000])
    outro_text = " ".join(words[-500:]) if len(words) > 500 else ""

    llm = get_llm(temperature=0.0)
    prompt = METADATA_EXTRACTION_PROMPT.format(
        filename=filename,
        title=file_meta["title"],
        guest_name=file_meta["guest_name"],
        intro_text=intro_text,
        outro_text=outro_text,
    )

    response = await llm.ainvoke(prompt)
    content = response.content.strip()

    # Strip markdown code fences if present
    if content.startswith("```"):
        content = content.split("\n", 1)[1]
        content = content.rsplit("```", 1)[0]

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        logger.warning(f"Failed to parse metadata extraction response for {filename}")
        data = {}

    result = EpisodeMetadata(
        title=data.get("title", file_meta["title"]),
        guest_names=data.get("guest_names", [file_meta["guest_name"]] if file_meta["guest_name"] else []),
        host_names=data.get("host_names", ["Steven Sikash", "Mike Liske"]),
        industry=data.get("industry", ""),
        topic_tags=data.get("topic_tags", []),
        summary=data.get("summary", ""),
        source_file=filename,
        duration_seconds=int(segments[-1].end_time) if segments else 0,
    )
    logger.info(f"extract_metadata returned | title={result.title!r}")
    return result
