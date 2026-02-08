import webvtt
from models.schemas import ParsedCue


def _time_to_seconds(time_str: str) -> float:
    """Convert VTT timestamp (HH:MM:SS.mmm) to seconds."""
    parts = time_str.split(":")
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = float(parts[2])
    return hours * 3600 + minutes * 60 + seconds


def parse_vtt(file_path: str) -> list[ParsedCue]:
    """
    Parse a VTT file and merge short cues into complete sentences.

    Strategy: concatenate consecutive cues until we hit sentence-ending
    punctuation or a >2s gap between cues.
    """
    captions = list(webvtt.read(file_path))
    if not captions:
        return []

    merged: list[ParsedCue] = []
    current_text = ""
    current_start = _time_to_seconds(captions[0].start)
    current_end = _time_to_seconds(captions[0].end)

    for i, caption in enumerate(captions):
        start = _time_to_seconds(caption.start)
        end = _time_to_seconds(caption.end)
        text = caption.text.strip()

        if not text:
            continue

        if not current_text:
            current_text = text
            current_start = start
            current_end = end
            continue

        gap = start - current_end
        ends_sentence = current_text.rstrip().endswith((".", "!", "?"))

        if ends_sentence or gap > 2.0:
            merged.append(ParsedCue(
                start_time=current_start,
                end_time=current_end,
                text=current_text.strip(),
            ))
            current_text = text
            current_start = start
            current_end = end
        else:
            current_text += " " + text
            current_end = end

    if current_text.strip():
        merged.append(ParsedCue(
            start_time=current_start,
            end_time=current_end,
            text=current_text.strip(),
        ))

    return merged
