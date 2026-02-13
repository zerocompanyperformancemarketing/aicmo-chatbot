from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from db.models import User


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


class TestGetUserByUsername:
    @pytest.mark.asyncio
    async def test_returns_existing_user(self, patch_session):
        from db.crud import get_user_by_username

        mock_user = User(id=1, username="admin", password_hash="hashed", full_name="Admin", email="admin@test.com")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        patch_session.execute.return_value = mock_result

        result = await get_user_by_username("admin")
        assert result.username == "admin"

    @pytest.mark.asyncio
    async def test_returns_none_for_nonexistent(self, patch_session):
        from db.crud import get_user_by_username

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        patch_session.execute.return_value = mock_result

        result = await get_user_by_username("nonexistent")
        assert result is None


class TestCreateUser:
    @pytest.mark.asyncio
    async def test_creates_user(self, patch_session):
        from db.crud import create_user

        result = await create_user("testuser", "hashed_pw", "Test User", "test@test.com")
        patch_session.add.assert_called_once()
        patch_session.commit.assert_called_once()
        patch_session.refresh.assert_called_once()
        saved = patch_session.add.call_args[0][0]
        assert saved.username == "testuser"
        assert saved.password_hash == "hashed_pw"
        assert saved.full_name == "Test User"
        assert saved.email == "test@test.com"
