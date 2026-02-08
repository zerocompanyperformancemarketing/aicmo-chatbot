from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from db.models import Conversation, Message


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


class TestGetOrCreateConversation:
    @pytest.mark.asyncio
    async def test_returns_existing(self, patch_session):
        from db.crud import get_or_create_conversation

        mock_conv = Conversation(id="conv-1")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_conv
        patch_session.execute.return_value = mock_result

        result = await get_or_create_conversation("conv-1")
        assert result.id == "conv-1"
        patch_session.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_creates_new(self, patch_session):
        from db.crud import get_or_create_conversation

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        patch_session.execute.return_value = mock_result

        result = await get_or_create_conversation("conv-new")
        patch_session.add.assert_called_once()
        patch_session.commit.assert_called_once()
        patch_session.refresh.assert_called_once()


class TestGetMessages:
    @pytest.mark.asyncio
    async def test_returns_messages(self, patch_session):
        from db.crud import get_messages

        msg1 = Message(id=1, conversation_id="conv-1", role="user", content="Hello")
        msg2 = Message(id=2, conversation_id="conv-1", role="assistant", content="Hi there")
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [msg1, msg2]
        patch_session.execute.return_value = mock_result

        result = await get_messages("conv-1")
        assert len(result) == 2
        assert result[0].role == "user"
        assert result[1].role == "assistant"

    @pytest.mark.asyncio
    async def test_returns_empty_list(self, patch_session):
        from db.crud import get_messages

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        patch_session.execute.return_value = mock_result

        result = await get_messages("conv-nonexistent")
        assert result == []


class TestSaveMessage:
    @pytest.mark.asyncio
    async def test_saves_user_message(self, patch_session):
        from db.crud import save_message

        result = await save_message("conv-1", "user", "Hello")
        patch_session.add.assert_called_once()
        patch_session.commit.assert_called_once()
        patch_session.refresh.assert_called_once()
        saved = patch_session.add.call_args[0][0]
        assert saved.role == "user"
        assert saved.content == "Hello"
        assert saved.conversation_id == "conv-1"

    @pytest.mark.asyncio
    async def test_saves_with_sources(self, patch_session):
        from db.crud import save_message

        sources = [{"episode": "ep-1", "text": "snippet"}]
        await save_message("conv-1", "assistant", "Reply", sources=sources)
        saved = patch_session.add.call_args[0][0]
        assert saved.sources == sources
