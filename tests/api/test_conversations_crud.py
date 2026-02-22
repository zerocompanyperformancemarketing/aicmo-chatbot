from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from db.models import Conversation


@pytest.fixture
def mock_session():
    """Create a mock async session with context manager support."""
    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=False)
    return session


@pytest.fixture
def patch_session(mock_session):
    """Patch async_session to return our mock."""
    with patch("db.crud.async_session", return_value=mock_session):
        yield mock_session


class TestGetUserIdByUsername:
    @pytest.mark.asyncio
    async def test_returns_user_id(self, patch_session):
        from db.crud import get_user_id_by_username

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = 1
        patch_session.execute.return_value = mock_result

        result = await get_user_id_by_username("admin")
        assert result == 1

    @pytest.mark.asyncio
    async def test_returns_none_for_unknown_user(self, patch_session):
        from db.crud import get_user_id_by_username

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        patch_session.execute.return_value = mock_result

        result = await get_user_id_by_username("unknown")
        assert result is None


class TestGetConversationsForUser:
    @pytest.mark.asyncio
    async def test_returns_conversations(self, patch_session):
        from db.crud import get_conversations_for_user

        conv1 = Conversation(id="conv-1")
        conv2 = Conversation(id="conv-2")
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [conv1, conv2]
        patch_session.execute.return_value = mock_result

        result = await get_conversations_for_user(1)
        assert len(result) == 2
        assert result[0].id == "conv-1"

    @pytest.mark.asyncio
    async def test_returns_empty_list(self, patch_session):
        from db.crud import get_conversations_for_user

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        patch_session.execute.return_value = mock_result

        result = await get_conversations_for_user(1)
        assert result == []


class TestGetConversationById:
    @pytest.mark.asyncio
    async def test_returns_conversation(self, patch_session):
        from db.crud import get_conversation_by_id

        conv = Conversation(id="conv-123")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = conv
        patch_session.execute.return_value = mock_result

        result = await get_conversation_by_id("conv-123", 1)
        assert result.id == "conv-123"

    @pytest.mark.asyncio
    async def test_returns_none_if_not_found(self, patch_session):
        from db.crud import get_conversation_by_id

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        patch_session.execute.return_value = mock_result

        result = await get_conversation_by_id("unknown", 1)
        assert result is None


class TestGetFirstUserMessage:
    @pytest.mark.asyncio
    async def test_returns_first_message(self, patch_session):
        from db.crud import get_first_user_message

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = "Hello world"
        patch_session.execute.return_value = mock_result

        result = await get_first_user_message("conv-123")
        assert result == "Hello world"

    @pytest.mark.asyncio
    async def test_returns_none_if_no_messages(self, patch_session):
        from db.crud import get_first_user_message

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        patch_session.execute.return_value = mock_result

        result = await get_first_user_message("conv-123")
        assert result is None


class TestDeleteConversation:
    @pytest.mark.asyncio
    async def test_deletes_conversation(self, patch_session):
        from db.crud import delete_conversation

        conv = Conversation(id="conv-123")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = conv
        patch_session.execute.return_value = mock_result

        result = await delete_conversation("conv-123", 1)
        assert result is True
        patch_session.delete.assert_called_once_with(conv)
        patch_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_returns_false_if_not_found(self, patch_session):
        from db.crud import delete_conversation

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        patch_session.execute.return_value = mock_result

        result = await delete_conversation("unknown", 1)
        assert result is False
        patch_session.delete.assert_not_called()
