import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from auth import get_current_user
from db.crud import (
    get_user_by_username,
    get_user_by_id,
    get_all_users,
    get_pending_users,
    verify_user,
    set_user_active,
    delete_user,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


# --- Schemas ---


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    full_name: str
    is_verified: bool
    is_admin: bool
    is_active: bool
    created_at: datetime


class UserListResponse(BaseModel):
    users: list[UserResponse]


class MessageResponse(BaseModel):
    message: str


# --- Dependencies ---


async def require_admin(username: str = Depends(get_current_user)):
    """Dependency that ensures the current user is an admin."""
    user = await get_user_by_username(username)
    if user is None or not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


def user_to_response(user) -> UserResponse:
    """Convert User model to UserResponse."""
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        full_name=user.full_name,
        is_verified=user.is_verified,
        is_admin=user.is_admin,
        is_active=user.is_active,
        created_at=user.created_at,
    )


# --- Endpoints ---


@router.get("/users", response_model=UserListResponse)
async def list_users(
    limit: int = 100,
    offset: int = 0,
    admin=Depends(require_admin),
):
    """List all users (admin only)."""
    users = await get_all_users(limit=limit, offset=offset)
    logger.info(f"GET /admin/users | admin={admin.username} | count={len(users)}")
    return UserListResponse(users=[user_to_response(u) for u in users])


@router.get("/users/pending", response_model=UserListResponse)
async def list_pending_users(admin=Depends(require_admin)):
    """List users pending verification (admin only)."""
    users = await get_pending_users()
    logger.info(f"GET /admin/users/pending | admin={admin.username} | count={len(users)}")
    return UserListResponse(users=[user_to_response(u) for u in users])


@router.post("/users/{user_id}/verify", response_model=MessageResponse)
async def approve_user(user_id: int, admin=Depends(require_admin)):
    """Approve/verify a user (admin only)."""
    user = await get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already verified",
        )

    success = await verify_user(user_id, verified=True)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify user",
        )

    logger.info(f"POST /admin/users/{user_id}/verify | admin={admin.username} | user={user.username}")
    return MessageResponse(message=f"User {user.username} has been verified")


@router.post("/users/{user_id}/revoke", response_model=MessageResponse)
async def revoke_user(user_id: int, admin=Depends(require_admin)):
    """Revoke user access (admin only)."""
    user = await get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Prevent admin from revoking themselves
    if user.id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot revoke your own access",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already deactivated",
        )

    success = await set_user_active(user_id, active=False)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke user access",
        )

    logger.info(f"POST /admin/users/{user_id}/revoke | admin={admin.username} | user={user.username}")
    return MessageResponse(message=f"User {user.username} has been deactivated")


@router.post("/users/{user_id}/reactivate", response_model=MessageResponse)
async def reactivate_user(user_id: int, admin=Depends(require_admin)):
    """Reactivate a deactivated user (admin only)."""
    user = await get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already active",
        )

    success = await set_user_active(user_id, active=True)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reactivate user",
        )

    logger.info(f"POST /admin/users/{user_id}/reactivate | admin={admin.username} | user={user.username}")
    return MessageResponse(message=f"User {user.username} has been reactivated")


@router.delete("/users/{user_id}", response_model=MessageResponse)
async def remove_user(user_id: int, admin=Depends(require_admin)):
    """Permanently delete a user (admin only)."""
    user = await get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Prevent admin from deleting themselves
    if user.id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    username = user.username
    success = await delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user",
        )

    logger.info(f"DELETE /admin/users/{user_id} | admin={admin.username} | deleted_user={username}")
    return MessageResponse(message=f"User {username} has been permanently deleted")
