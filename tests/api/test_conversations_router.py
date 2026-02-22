from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

import routers.conversations as conv_module


@pytest.fixture
def mock_conversation():
    conv = MagicMock()
    conv.id = "conv-123"
    conv.created_at = datetime(2024, 1, 15, 10, 0, 0)
    conv.updated_at = datetime(2024, 1, 15, 12, 0, 0)
    return conv


@pytest.fixture
def mock_message():
    msg = MagicMock()
    msg.id = 1
    msg.role = "user"
    msg.content = "Hello, world!"
    msg.sources = None
    msg.created_at = datetime(2024, 1, 15, 10, 0, 0)
    return msg


class TestListConversations:
    @pytest.mark.asyncio
    async def test_returns_conversations(self, mock_conversation):
        with (
            patch.object(conv_module, "get_user_id_by_username", new_callable=AsyncMock, return_value=1),
            patch.object(conv_module, "get_conversations_for_user", new_callable=AsyncMock, return_value=[mock_conversation]),
            patch.object(conv_module, "get_first_user_message", new_callable=AsyncMock, return_value="Hello world"),
        ):
            response = await conv_module.list_conversations(username="testuser")

            assert len(response.conversations) == 1
            assert response.conversations[0].id == "conv-123"
            assert response.conversations[0].preview == "Hello world"

    @pytest.mark.asyncio
    async def test_returns_empty_list(self):
        with (
            patch.object(conv_module, "get_user_id_by_username", new_callable=AsyncMock, return_value=1),
            patch.object(conv_module, "get_conversations_for_user", new_callable=AsyncMock, return_value=[]),
        ):
            response = await conv_module.list_conversations(username="testuser")

            assert len(response.conversations) == 0

    @pytest.mark.asyncio
    async def test_user_not_found_raises_404(self):
        with (
            patch.object(conv_module, "get_user_id_by_username", new_callable=AsyncMock, return_value=None),
        ):
            with pytest.raises(Exception) as exc_info:
                await conv_module.list_conversations(username="unknown")

            assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_truncates_long_preview(self, mock_conversation):
        long_message = "A" * 150
        with (
            patch.object(conv_module, "get_user_id_by_username", new_callable=AsyncMock, return_value=1),
            patch.object(conv_module, "get_conversations_for_user", new_callable=AsyncMock, return_value=[mock_conversation]),
            patch.object(conv_module, "get_first_user_message", new_callable=AsyncMock, return_value=long_message),
        ):
            response = await conv_module.list_conversations(username="testuser")

            assert len(response.conversations[0].preview) == 103  # 100 chars + "..."
            assert response.conversations[0].preview.endswith("...")


class TestGetConversation:
    @pytest.mark.asyncio
    async def test_returns_conversation_with_messages(self, mock_conversation, mock_message):
        with (
            patch.object(conv_module, "get_user_id_by_username", new_callable=AsyncMock, return_value=1),
            patch.object(conv_module, "get_conversation_by_id", new_callable=AsyncMock, return_value=mock_conversation),
            patch.object(conv_module, "get_messages", new_callable=AsyncMock, return_value=[mock_message]),
        ):
            response = await conv_module.get_conversation("conv-123", username="testuser")

            assert response.id == "conv-123"
            assert len(response.messages) == 1
            assert response.messages[0].content == "Hello, world!"

    @pytest.mark.asyncio
    async def test_conversation_not_found_raises_404(self):
        with (
            patch.object(conv_module, "get_user_id_by_username", new_callable=AsyncMock, return_value=1),
            patch.object(conv_module, "get_conversation_by_id", new_callable=AsyncMock, return_value=None),
        ):
            with pytest.raises(Exception) as exc_info:
                await conv_module.get_conversation("unknown", username="testuser")

            assert exc_info.value.status_code == 404


class TestDeleteConversation:
    @pytest.mark.asyncio
    async def test_deletes_conversation(self):
        with (
            patch.object(conv_module, "get_user_id_by_username", new_callable=AsyncMock, return_value=1),
            patch.object(conv_module, "delete_conversation", new_callable=AsyncMock, return_value=True),
        ):
            response = await conv_module.remove_conversation("conv-123", username="testuser")

            assert response["status"] == "deleted"
            assert response["conversation_id"] == "conv-123"

    @pytest.mark.asyncio
    async def test_conversation_not_found_raises_404(self):
        with (
            patch.object(conv_module, "get_user_id_by_username", new_callable=AsyncMock, return_value=1),
            patch.object(conv_module, "delete_conversation", new_callable=AsyncMock, return_value=False),
        ):
            with pytest.raises(Exception) as exc_info:
                await conv_module.remove_conversation("unknown", username="testuser")

            assert exc_info.value.status_code == 404
