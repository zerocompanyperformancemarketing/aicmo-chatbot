import logging

from fastapi import APIRouter, HTTPException, status

from auth import verify_password, create_access_token
from db.crud import get_user_by_username
from models.schemas import LoginRequest, LoginResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Authenticate user and return JWT."""
    user = await get_user_by_username(request.username)
    if user is None or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    token = create_access_token(user.username)
    logger.info(f"POST /auth/login | user={user.username}")
    return LoginResponse(
        access_token=token,
        username=user.username,
        full_name=user.full_name,
    )
