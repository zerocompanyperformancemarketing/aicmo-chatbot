from ingestion.metadata_extractor import extract_from_filename


class TestExtractFromFilename:
    def test_title_with_guest(self):
        result = extract_from_filename("Great Episode with John Smith _unedited_.vtt")
        assert result["title"] == "Great Episode"
        assert result["guest_name"] == "John Smith"

    def test_title_without_guest(self):
        result = extract_from_filename("Solo Episode Title _unedited_.vtt")
        assert result["title"] == "Solo Episode Title"
        assert result["guest_name"] == ""

    def test_removes_unedited_suffix(self):
        result = extract_from_filename("My Episode _unedited_.vtt")
        assert "_unedited_" not in result["title"]

    def test_removes_edited_suffix(self):
        result = extract_from_filename("My Episode _edited_.vtt")
        assert "_edited_" not in result["title"]

    def test_plain_filename(self):
        result = extract_from_filename("Simple Title.vtt")
        assert result["title"] == "Simple Title"
        assert result["guest_name"] == ""

    def test_with_in_title_no_guest(self):
        # "with" only splits on first occurrence
        result = extract_from_filename("Dealing with Challenges with Jane Doe.vtt")
        assert result["title"] == "Dealing"
        assert result["guest_name"] == "Challenges with Jane Doe"

    def test_strips_whitespace(self):
        result = extract_from_filename("  Padded Title with Guest Name  .vtt")
        assert result["title"] == "Padded Title"
        assert result["guest_name"] == "Guest Name"
