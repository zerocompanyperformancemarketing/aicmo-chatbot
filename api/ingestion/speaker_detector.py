import json
import logging
from langchain_openai import ChatOpenAI
from agents.utils.llm import get_llm
from models.schemas import ParsedCue

logger = logging.getLogger(__name__)


SPEAKER_DETECTION_PROMPT = """You are analyzing a podcast transcript to identify who is speaking.

Known information:
- Podcast: "The Bliss Business Podcast"
- Hosts: Steven Sikash, Mike Liske
- Guest: {guest_name}

Below are transcript segments. For each segment, assign the most likely speaker based on:
1. Contextual clues (introductions, name mentions)
2. Conversation flow (question/answer patterns - hosts tend to ask questions)
3. Content attribution (personal stories likely belong to the guest)

Return a JSON array where each element has:
- "index": the segment index (0-based)
- "speaker": the speaker name (use exact names: "Steven Sikash", "Mike Liske", or "{guest_name}")
- "confidence": float 0-1

Transcript segments:
{segments}

Return ONLY the JSON array, no other text."""


async def detect_speakers(
    segments: list[ParsedCue],
    guest_name: str,
    batch_size: int = 20,
) -> list[ParsedCue]:
    """
    Use LLM to assign speaker labels to transcript segments.

    Processes in batches to manage token costs.
    """
    llm = get_llm(temperature=0.0)
    labeled_segments: list[ParsedCue] = []

    for batch_start in range(0, len(segments), batch_size):
        batch = segments[batch_start:batch_start + batch_size]

        segments_text = "\n".join(
            f"[{i}] ({seg.start_time:.1f}s - {seg.end_time:.1f}s): {seg.text}"
            for i, seg in enumerate(batch)
        )

        prompt = SPEAKER_DETECTION_PROMPT.format(
            guest_name=guest_name,
            segments=segments_text,
        )

        response = await llm.ainvoke(prompt)
        content = response.content.strip()

        # Strip markdown code fences if present
        if content.startswith("```"):
            content = content.split("\n", 1)[1]
            content = content.rsplit("```", 1)[0]

        try:
            speaker_data = json.loads(content)
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse speaker detection response for batch starting at {batch_start}")
            speaker_data = []

        for i, seg in enumerate(batch):
            speaker = ""
            for sd in speaker_data:
                if sd.get("index") == i:
                    speaker = sd.get("speaker", "")
                    break

            labeled_segments.append(ParsedCue(
                start_time=seg.start_time,
                end_time=seg.end_time,
                text=seg.text,
                speaker=speaker,
            ))

    return labeled_segments
