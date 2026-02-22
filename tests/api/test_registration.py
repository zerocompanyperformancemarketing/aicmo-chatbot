from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from models.schemas import RegisterRequest
import routers.auth as auth_module


class TestRegistration:
    @pytest.mark.asyncio
    async def test_success_creates_unverified_user(self):
        mock_user = MagicMock()
        mock_user.username = "test@example.com"

        with patch.object(auth_module, "get_user_by_email", new_callable=AsyncMock, return_value=None), \
             patch.object(auth_module, "get_user_by_username", new_callable=AsyncMock, return_value=None), \
             patch.object(auth_module, "create_user", new_callable=AsyncMock, return_value=mock_user):
            request = RegisterRequest(
                first_name="Test",
                last_name="User",
                email="test@example.com",
                password="password123",
                confirm_password="password123",
            )
            response = await auth_module.register(request)

            assert response.username == "test@example.com"
            assert "pending" in response.message.lower()

    @pytest.mark.asyncio
    async def test_duplicate_email_raises_400(self):
        mock_user = MagicMock()
        mock_user.email = "test@example.com"

        with patch.object(auth_module, "get_user_by_email", new_callable=AsyncMock, return_value=mock_user):
            request = RegisterRequest(
                first_name="Test",
                last_name="User",
                email="test@example.com",
                password="password123",
                confirm_password="password123",
            )

            with pytest.raises(Exception) as exc_info:
                await auth_module.register(request)
            assert exc_info.value.status_code == 400
            assert "already registered" in exc_info.value.detail.lower()

    def test_password_mismatch_fails_validation(self):
        with pytest.raises(ValueError) as exc_info:
            RegisterRequest(
                first_name="Test",
                last_name="User",
                email="test@example.com",
                password="password123",
                confirm_password="different123",
            )
        assert "do not match" in str(exc_info.value).lower()

    def test_password_too_short_fails_validation(self):
        with pytest.raises(ValueError) as exc_info:
            RegisterRequest(
                first_name="Test",
                last_name="User",
                email="test@example.com",
                password="short",
                confirm_password="short",
            )
        assert "8 characters" in str(exc_info.value).lower()

    def test_invalid_email_fails_validation(self):
        with pytest.raises(ValueError) as exc_info:
            RegisterRequest(
                first_name="Test",
                last_name="User",
                email="not-an-email",
                password="password123",
                confirm_password="password123",
            )
        assert "email" in str(exc_info.value).lower()

    def test_empty_first_name_fails_validation(self):
        with pytest.raises(ValueError) as exc_info:
            RegisterRequest(
                first_name="   ",
                last_name="User",
                email="test@example.com",
                password="password123",
                confirm_password="password123",
            )
        assert "empty" in str(exc_info.value).lower()


class TestLoginVerificationChecks:
    @pytest.mark.asyncio
    async def test_unverified_user_cannot_login(self):
        from auth import hash_password

        mock_user = MagicMock()
        mock_user.username = "test@example.com"
        mock_user.password_hash = hash_password("password123")
        mock_user.is_verified = False
        mock_user.is_active = True

        with patch.object(auth_module, "get_user_by_username", new_callable=AsyncMock, return_value=mock_user):
            from models.schemas import LoginRequest
            request = LoginRequest(username="test@example.com", password="password123")

            with pytest.raises(Exception) as exc_info:
                await auth_module.login(request)
            assert exc_info.value.status_code == 403
            assert "pending verification" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_deactivated_user_cannot_login(self):
        from auth import hash_password

        mock_user = MagicMock()
        mock_user.username = "test@example.com"
        mock_user.password_hash = hash_password("password123")
        mock_user.is_verified = True
        mock_user.is_active = False

        with patch.object(auth_module, "get_user_by_username", new_callable=AsyncMock, return_value=mock_user):
            from models.schemas import LoginRequest
            request = LoginRequest(username="test@example.com", password="password123")

            with pytest.raises(Exception) as exc_info:
                await auth_module.login(request)
            assert exc_info.value.status_code == 403
            assert "deactivated" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_verified_active_user_can_login(self):
        from auth import hash_password

        mock_user = MagicMock()
        mock_user.username = "test@example.com"
        mock_user.full_name = "Test User"
        mock_user.password_hash = hash_password("password123")
        mock_user.is_verified = True
        mock_user.is_active = True
        mock_user.is_admin = False
        mock_user.password_changed_at = datetime.utcnow()

        with patch.object(auth_module, "get_user_by_username", new_callable=AsyncMock, return_value=mock_user):
            from models.schemas import LoginRequest
            request = LoginRequest(username="test@example.com", password="password123")
            response = await auth_module.login(request)

            assert response.access_token
            assert response.username == "test@example.com"
            assert response.is_admin is False
