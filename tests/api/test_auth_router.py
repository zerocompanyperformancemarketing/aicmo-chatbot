from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from auth import hash_password
from models.schemas import LoginRequest
import routers.auth as auth_module


def create_verified_user(username: str = "admin", password: str = "correct_password") -> MagicMock:
    """Create a mock user that passes all verification checks."""
    mock_user = MagicMock()
    mock_user.username = username
    mock_user.full_name = "Admin"
    mock_user.password_hash = hash_password(password)
    mock_user.is_verified = True
    mock_user.is_active = True
    mock_user.is_admin = False
    mock_user.password_changed_at = datetime.utcnow()
    return mock_user


class TestLogin:
    @pytest.mark.asyncio
    async def test_success_returns_token(self):
        mock_user = create_verified_user()

        with patch.object(auth_module, "get_user_by_username", new_callable=AsyncMock, return_value=mock_user):
            request = LoginRequest(username="admin", password="correct_password")
            response = await auth_module.login(request)

            assert response.access_token
            assert response.username == "admin"
            assert response.full_name == "Admin"
            assert response.token_type == "bearer"

    @pytest.mark.asyncio
    async def test_wrong_password_raises_401(self):
        mock_user = create_verified_user()

        with patch.object(auth_module, "get_user_by_username", new_callable=AsyncMock, return_value=mock_user):
            request = LoginRequest(username="admin", password="wrong_password")

            with pytest.raises(Exception) as exc_info:
                await auth_module.login(request)
            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_nonexistent_user_raises_401(self):
        with patch.object(auth_module, "get_user_by_username", new_callable=AsyncMock, return_value=None):
            request = LoginRequest(username="nobody", password="any")

            with pytest.raises(Exception) as exc_info:
                await auth_module.login(request)
            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_login_returns_is_admin_flag(self):
        mock_user = create_verified_user()
        mock_user.is_admin = True

        with patch.object(auth_module, "get_user_by_username", new_callable=AsyncMock, return_value=mock_user):
            request = LoginRequest(username="admin", password="correct_password")
            response = await auth_module.login(request)

            assert response.is_admin is True
