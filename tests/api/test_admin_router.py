from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import routers.admin as admin_module


def create_mock_user(
    user_id: int = 1,
    username: str = "test@example.com",
    email: str = "test@example.com",
    first_name: str = "Test",
    last_name: str = "User",
    full_name: str = "Test User",
    is_verified: bool = True,
    is_admin: bool = False,
    is_active: bool = True,
) -> MagicMock:
    user = MagicMock()
    user.id = user_id
    user.username = username
    user.email = email
    user.first_name = first_name
    user.last_name = last_name
    user.full_name = full_name
    user.is_verified = is_verified
    user.is_admin = is_admin
    user.is_active = is_active
    user.created_at = datetime.utcnow()
    return user


class TestRequireAdmin:
    @pytest.mark.asyncio
    async def test_non_admin_raises_403(self):
        mock_user = create_mock_user(is_admin=False)

        with patch.object(admin_module, "get_user_by_username", new_callable=AsyncMock, return_value=mock_user):
            with pytest.raises(Exception) as exc_info:
                await admin_module.require_admin("test@example.com")
            assert exc_info.value.status_code == 403
            assert "admin" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_admin_user_succeeds(self):
        mock_admin = create_mock_user(is_admin=True)

        with patch.object(admin_module, "get_user_by_username", new_callable=AsyncMock, return_value=mock_admin):
            result = await admin_module.require_admin("admin@example.com")
            assert result.is_admin is True

    @pytest.mark.asyncio
    async def test_nonexistent_user_raises_403(self):
        with patch.object(admin_module, "get_user_by_username", new_callable=AsyncMock, return_value=None):
            with pytest.raises(Exception) as exc_info:
                await admin_module.require_admin("nobody@example.com")
            assert exc_info.value.status_code == 403


class TestListUsers:
    @pytest.mark.asyncio
    async def test_lists_all_users(self):
        mock_admin = create_mock_user(user_id=1, is_admin=True)
        mock_users = [
            create_mock_user(user_id=1, username="user1@test.com"),
            create_mock_user(user_id=2, username="user2@test.com"),
        ]

        with patch.object(admin_module, "get_all_users", new_callable=AsyncMock, return_value=mock_users):
            response = await admin_module.list_users(admin=mock_admin)
            assert len(response.users) == 2


class TestListPendingUsers:
    @pytest.mark.asyncio
    async def test_lists_pending_users(self):
        mock_admin = create_mock_user(user_id=1, is_admin=True)
        mock_users = [
            create_mock_user(user_id=2, is_verified=False),
            create_mock_user(user_id=3, is_verified=False),
        ]

        with patch.object(admin_module, "get_pending_users", new_callable=AsyncMock, return_value=mock_users):
            response = await admin_module.list_pending_users(admin=mock_admin)
            assert len(response.users) == 2


class TestVerifyUser:
    @pytest.mark.asyncio
    async def test_verifies_user(self):
        mock_admin = create_mock_user(user_id=1, is_admin=True)
        mock_user = create_mock_user(user_id=2, is_verified=False)

        with patch.object(admin_module, "get_user_by_id", new_callable=AsyncMock, return_value=mock_user), \
             patch.object(admin_module, "verify_user", new_callable=AsyncMock, return_value=True):
            response = await admin_module.approve_user(user_id=2, admin=mock_admin)
            assert "verified" in response.message.lower()

    @pytest.mark.asyncio
    async def test_already_verified_raises_400(self):
        mock_admin = create_mock_user(user_id=1, is_admin=True)
        mock_user = create_mock_user(user_id=2, is_verified=True)

        with patch.object(admin_module, "get_user_by_id", new_callable=AsyncMock, return_value=mock_user):
            with pytest.raises(Exception) as exc_info:
                await admin_module.approve_user(user_id=2, admin=mock_admin)
            assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_nonexistent_user_raises_404(self):
        mock_admin = create_mock_user(user_id=1, is_admin=True)

        with patch.object(admin_module, "get_user_by_id", new_callable=AsyncMock, return_value=None):
            with pytest.raises(Exception) as exc_info:
                await admin_module.approve_user(user_id=999, admin=mock_admin)
            assert exc_info.value.status_code == 404


class TestRevokeUser:
    @pytest.mark.asyncio
    async def test_revokes_user(self):
        mock_admin = create_mock_user(user_id=1, is_admin=True)
        mock_user = create_mock_user(user_id=2, is_active=True)

        with patch.object(admin_module, "get_user_by_id", new_callable=AsyncMock, return_value=mock_user), \
             patch.object(admin_module, "set_user_active", new_callable=AsyncMock, return_value=True):
            response = await admin_module.revoke_user(user_id=2, admin=mock_admin)
            assert "deactivated" in response.message.lower()

    @pytest.mark.asyncio
    async def test_cannot_revoke_self(self):
        mock_admin = create_mock_user(user_id=1, is_admin=True)

        with patch.object(admin_module, "get_user_by_id", new_callable=AsyncMock, return_value=mock_admin):
            with pytest.raises(Exception) as exc_info:
                await admin_module.revoke_user(user_id=1, admin=mock_admin)
            assert exc_info.value.status_code == 400
            assert "your own" in exc_info.value.detail.lower()


class TestReactivateUser:
    @pytest.mark.asyncio
    async def test_reactivates_user(self):
        mock_admin = create_mock_user(user_id=1, is_admin=True)
        mock_user = create_mock_user(user_id=2, is_active=False)

        with patch.object(admin_module, "get_user_by_id", new_callable=AsyncMock, return_value=mock_user), \
             patch.object(admin_module, "set_user_active", new_callable=AsyncMock, return_value=True):
            response = await admin_module.reactivate_user(user_id=2, admin=mock_admin)
            assert "reactivated" in response.message.lower()


class TestDeleteUser:
    @pytest.mark.asyncio
    async def test_deletes_user(self):
        mock_admin = create_mock_user(user_id=1, is_admin=True)
        mock_user = create_mock_user(user_id=2)

        with patch.object(admin_module, "get_user_by_id", new_callable=AsyncMock, return_value=mock_user), \
             patch.object(admin_module, "delete_user", new_callable=AsyncMock, return_value=True):
            response = await admin_module.remove_user(user_id=2, admin=mock_admin)
            assert "deleted" in response.message.lower()

    @pytest.mark.asyncio
    async def test_cannot_delete_self(self):
        mock_admin = create_mock_user(user_id=1, is_admin=True)

        with patch.object(admin_module, "get_user_by_id", new_callable=AsyncMock, return_value=mock_admin):
            with pytest.raises(Exception) as exc_info:
                await admin_module.remove_user(user_id=1, admin=mock_admin)
            assert exc_info.value.status_code == 400
            assert "your own" in exc_info.value.detail.lower()
