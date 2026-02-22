import sys
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

# Mock heavy dependencies before importing the router module
sys.modules.setdefault("agents.supervisor", MagicMock())

from models.schemas import ChatRequest
import routers.chat as chat_module


@pytest.fixture
def mock_supervisor():
    supervisor = AsyncMock()
    ai_msg = MagicMock()
    ai_msg.content = "Test response"
    ai_msg.type = "ai"
    supervisor.ainvoke.return_value = {"messages": [ai_msg]}
    return supervisor


class TestChatEndpoint:
    @pytest.mark.asyncio
    async def test_new_conversation(self, mock_supervisor):
        with (
            patch.object(chat_module, "_get_supervisor", return_value=mock_supervisor),
            patch.object(chat_module, "get_user_id_by_username", new_callable=AsyncMock, return_value=1),
            patch.object(chat_module, "get_or_create_conversation", new_callable=AsyncMock),
            patch.object(chat_module, "get_messages", new_callable=AsyncMock, return_value=[]),
            patch.object(chat_module, "save_message", new_callable=AsyncMock) as mock_save,
        ):
            request = ChatRequest(message="Hello")
            response = await chat_module.chat(request, username="testuser")

            assert response.response == "Test response"
            assert response.conversation_id is not None
            assert mock_save.call_count == 2

    @pytest.mark.asyncio
    async def test_existing_conversation_loads_history(self, mock_supervisor):
        prior_msg = MagicMock()
        prior_msg.role = "user"
        prior_msg.content = "Previous question"

        with (
            patch.object(chat_module, "_get_supervisor", return_value=mock_supervisor),
            patch.object(chat_module, "get_user_id_by_username", new_callable=AsyncMock, return_value=1),
            patch.object(chat_module, "get_or_create_conversation", new_callable=AsyncMock),
            patch.object(chat_module, "get_messages", new_callable=AsyncMock, return_value=[prior_msg]),
            patch.object(chat_module, "save_message", new_callable=AsyncMock),
        ):
            request = ChatRequest(message="Follow up", conversation_id="conv-123")
            response = await chat_module.chat(request, username="testuser")

            # Supervisor should receive 2 messages (1 prior + 1 new)
            invoke_args = mock_supervisor.ainvoke.call_args[0][0]
            assert len(invoke_args["messages"]) == 2
            assert response.conversation_id == "conv-123"

    @pytest.mark.asyncio
    async def test_no_ai_message_fallback(self):
        supervisor = AsyncMock()
        supervisor.ainvoke.return_value = {"messages": []}

        with (
            patch.object(chat_module, "_get_supervisor", return_value=supervisor),
            patch.object(chat_module, "get_user_id_by_username", new_callable=AsyncMock, return_value=1),
            patch.object(chat_module, "get_or_create_conversation", new_callable=AsyncMock),
            patch.object(chat_module, "get_messages", new_callable=AsyncMock, return_value=[]),
            patch.object(chat_module, "save_message", new_callable=AsyncMock),
        ):
            request = ChatRequest(message="Hello")
            response = await chat_module.chat(request, username="testuser")

            assert response.response == "I couldn't find an answer."
