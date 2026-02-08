import requests
from config import Config

def send_to_slack_channel(
        self,
        header: str,
        message: str,
        slack_webhook_url: str | None = Config.SLACK_WEBHOOK_URL
    ) -> requests.Response:
    """
    Send a message to a Slack via webhook.
    Args:
        header (str): The header text for the Slack message.
        message (str): The main content of the Slack message in Markdown format.
        slack_webhook_url (str | None): The Slack webhook URL to send the message to. Defaults to the value in Config.
    Returns:
        requests.Response: The response object from the Slack API.
    """
    if not slack_webhook_url:
        # raise error if slack_webhook_url is not provided
        raise ValueError("Slack webhook URL must be provided.")

    payload = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": header
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": message
                }
            }
        ]
    }
    # Define headers
    headers = {
        "Content-type": "application/json"
    }
    # Send POST request to Slack webhook URL
    return requests.post(slack_webhook_url, json=payload, headers=headers)
