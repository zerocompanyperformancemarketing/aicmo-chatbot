from unittest.mock import patch, MagicMock
from tools.filter import filter_by_industry, filter_by_speaker


class TestFilterByIndustry:
    @patch("tools.filter.get_typesense_client")
    def test_returns_episodes(self, mock_client_fn):
        mock_client = MagicMock()
        mock_client.collections.__getitem__.return_value.documents.search.return_value = {
            "hits": [{
                "document": {
                    "id": "ep-1",
                    "title": "AI Episode",
                    "guest_names": ["Jane"],
                    "industry": "Tech",
                    "topic_tags": ["AI"],
                    "summary": "About AI",
                    "episode_link": "https://example.com",
                }
            }]
        }
        mock_client_fn.return_value = mock_client

        results = filter_by_industry("Tech")
        assert len(results) == 1
        assert results[0]["title"] == "AI Episode"
        assert results[0]["industry"] == "Tech"

    @patch("tools.filter.get_typesense_client")
    def test_empty_results(self, mock_client_fn):
        mock_client = MagicMock()
        mock_client.collections.__getitem__.return_value.documents.search.return_value = {"hits": []}
        mock_client_fn.return_value = mock_client

        results = filter_by_industry("Nonexistent")
        assert results == []


class TestFilterBySpeaker:
    @patch("tools.filter.get_typesense_client")
    def test_returns_chunks(self, mock_client_fn):
        mock_client = MagicMock()
        mock_client.collections.__getitem__.return_value.documents.search.return_value = {
            "hits": [{
                "document": {
                    "text": "Speaker content",
                    "speaker": "Jane Doe",
                    "episode_id": "ep-1",
                    "start_time": 5.0,
                    "end_time": 15.0,
                    "chunk_index": 0,
                }
            }]
        }
        mock_client_fn.return_value = mock_client

        results = filter_by_speaker("Jane Doe")
        assert len(results) == 1
        assert results[0]["speaker"] == "Jane Doe"

    @patch("tools.filter.get_typesense_client")
    def test_filter_applied(self, mock_client_fn):
        mock_client = MagicMock()
        mock_client.collections.__getitem__.return_value.documents.search.return_value = {"hits": []}
        mock_client_fn.return_value = mock_client

        filter_by_speaker("John Smith", limit=3)
        call_args = mock_client.collections.__getitem__.return_value.documents.search.call_args[0][0]
        assert call_args["filter_by"] == "speaker:=John Smith"
        assert call_args["per_page"] == 3
