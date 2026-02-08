from unittest.mock import patch, MagicMock
import pytest
from utils.slack_utils import send_to_slack_channel


class TestSendToSlackChannel:
    @patch("utils.slack_utils.requests.post")
    def test_sends_message(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Note: function has a `self` param (likely a bug in source), pass None
        result = send_to_slack_channel(None, "Test Header", "Test message", "https://hooks.slack.com/test")
        assert result.status_code == 200

        payload = mock_post.call_args[1]["json"]
        assert payload["blocks"][0]["text"]["text"] == "Test Header"
        assert payload["blocks"][1]["text"]["text"] == "Test message"

    def test_raises_without_url(self):
        with pytest.raises(ValueError, match="Slack webhook URL must be provided"):
            send_to_slack_channel(None, "Header", "Message", None)

    @patch("utils.slack_utils.requests.post")
    def test_payload_structure(self, mock_post):
        mock_post.return_value = MagicMock(status_code=200)

        send_to_slack_channel(None, "Header", "Body text", "https://hooks.slack.com/test")

        payload = mock_post.call_args[1]["json"]
        assert len(payload["blocks"]) == 2
        assert payload["blocks"][0]["type"] == "header"
        assert payload["blocks"][1]["type"] == "section"
        assert payload["blocks"][1]["text"]["type"] == "mrkdwn"
