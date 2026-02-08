from unittest.mock import patch, MagicMock
from tools.search import search_transcripts


MOCK_HITS = {
    "hits": [
        {
            "document": {
                "text": "AI is transforming business.",
                "speaker": "Jane Doe",
                "episode_id": "ep-1",
                "start_time": 10.0,
                "end_time": 20.0,
                "chunk_index": 0,
                "industry": "Tech",
                "topic_tags": ["AI"],
            },
            "text_match_info": {"score": 95},
        },
    ]
}


class TestSearchTranscripts:
    @patch("tools.search.get_typesense_client")
    def test_basic_search(self, mock_client_fn):
        mock_client = MagicMock()
        mock_client.collections.__getitem__.return_value.documents.search.return_value = MOCK_HITS
        mock_client_fn.return_value = mock_client

        results = search_transcripts("AI business")
        assert len(results) == 1
        assert results[0]["text"] == "AI is transforming business."
        assert results[0]["speaker"] == "Jane Doe"
        assert results[0]["score"] == 95

    @patch("tools.search.get_typesense_client")
    def test_with_filters(self, mock_client_fn):
        mock_client = MagicMock()
        mock_client.collections.__getitem__.return_value.documents.search.return_value = MOCK_HITS
        mock_client_fn.return_value = mock_client

        search_transcripts("AI", industry="Tech", speaker="Jane Doe")

        call_args = mock_client.collections.__getitem__.return_value.documents.search.call_args[0][0]
        assert "filter_by" in call_args
        assert "industry:=Tech" in call_args["filter_by"]
        assert "speaker:=Jane Doe" in call_args["filter_by"]

    @patch("tools.search.get_typesense_client")
    def test_empty_results(self, mock_client_fn):
        mock_client = MagicMock()
        mock_client.collections.__getitem__.return_value.documents.search.return_value = {"hits": []}
        mock_client_fn.return_value = mock_client

        results = search_transcripts("nonexistent")
        assert results == []

    @patch("tools.search.get_typesense_client")
    def test_respects_limit(self, mock_client_fn):
        mock_client = MagicMock()
        mock_client.collections.__getitem__.return_value.documents.search.return_value = MOCK_HITS
        mock_client_fn.return_value = mock_client

        search_transcripts("AI", limit=5)
        call_args = mock_client.collections.__getitem__.return_value.documents.search.call_args[0][0]
        assert call_args["per_page"] == 5
