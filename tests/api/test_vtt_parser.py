import tempfile
import os
import pytest
from ingestion.vtt_parser import _time_to_seconds, parse_vtt


class TestTimeToSeconds:
    def test_zero(self):
        assert _time_to_seconds("00:00:00.000") == 0.0

    def test_seconds_only(self):
        assert _time_to_seconds("00:00:05.000") == 5.0

    def test_minutes_and_seconds(self):
        assert _time_to_seconds("00:02:30.000") == 150.0

    def test_hours_minutes_seconds(self):
        assert _time_to_seconds("01:30:45.500") == 5445.5

    def test_milliseconds(self):
        result = _time_to_seconds("00:00:01.250")
        assert abs(result - 1.25) < 0.001


class TestParseVtt:
    def _write_vtt(self, content: str) -> str:
        """Write VTT content to a temp file and return the path."""
        fd, path = tempfile.mkstemp(suffix=".vtt")
        with os.fdopen(fd, "w") as f:
            f.write(content)
        return path

    def test_empty_file(self):
        path = self._write_vtt("WEBVTT\n\n")
        result = parse_vtt(path)
        assert result == []
        os.unlink(path)

    def test_single_cue(self):
        vtt = (
            "WEBVTT\n\n"
            "00:00:01.000 --> 00:00:03.000\n"
            "Hello world.\n\n"
        )
        path = self._write_vtt(vtt)
        result = parse_vtt(path)
        assert len(result) == 1
        assert result[0].text == "Hello world."
        assert result[0].start_time == 1.0
        assert result[0].end_time == 3.0
        os.unlink(path)

    def test_merges_cues_without_sentence_end(self):
        vtt = (
            "WEBVTT\n\n"
            "00:00:01.000 --> 00:00:02.000\n"
            "Hello\n\n"
            "00:00:02.000 --> 00:00:03.000\n"
            "world.\n\n"
        )
        path = self._write_vtt(vtt)
        result = parse_vtt(path)
        # Should merge into one cue since no sentence-ending punct on first
        assert len(result) == 1
        assert result[0].text == "Hello world."
        os.unlink(path)

    def test_splits_on_sentence_end(self):
        vtt = (
            "WEBVTT\n\n"
            "00:00:01.000 --> 00:00:02.000\n"
            "Hello world.\n\n"
            "00:00:02.000 --> 00:00:03.000\n"
            "Goodbye world.\n\n"
        )
        path = self._write_vtt(vtt)
        result = parse_vtt(path)
        assert len(result) == 2
        assert result[0].text == "Hello world."
        assert result[1].text == "Goodbye world."
        os.unlink(path)

    def test_splits_on_large_gap(self):
        vtt = (
            "WEBVTT\n\n"
            "00:00:01.000 --> 00:00:02.000\n"
            "First part\n\n"
            "00:00:05.000 --> 00:00:06.000\n"
            "Second part.\n\n"
        )
        path = self._write_vtt(vtt)
        result = parse_vtt(path)
        # >2s gap should cause a split
        assert len(result) == 2
        os.unlink(path)

    def test_skips_empty_cues(self):
        vtt = (
            "WEBVTT\n\n"
            "00:00:01.000 --> 00:00:02.000\n"
            "Hello.\n\n"
            "00:00:02.000 --> 00:00:03.000\n"
            "   \n\n"
            "00:00:03.000 --> 00:00:04.000\n"
            "World.\n\n"
        )
        path = self._write_vtt(vtt)
        result = parse_vtt(path)
        assert all(r.text.strip() for r in result)
        os.unlink(path)
