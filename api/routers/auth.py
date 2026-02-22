import logging

from fastapi import APIRouter, HTTPException, status

from auth import verify_password, create_access_token, hash_password
from db.crud import get_user_by_username, get_user_by_email, create_user
from models.schemas import LoginRequest, LoginResponse, RegisterRequest, RegisterResponse

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

    # Check if user is verified
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account pending verification. Please wait for admin approval.",
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been deactivated. Please contact an administrator.",
        )

    token = create_access_token(user.username, user.password_changed_at)
    logger.info(f"POST /auth/login | user={user.username}")
    return LoginResponse(
        access_token=token,
        username=user.username,
        full_name=user.full_name,
        is_admin=user.is_admin,
    )


@router.post("/register", response_model=RegisterResponse)
async def register(request: RegisterRequest):
    """Register a new user (pending admin verification)."""
    # Check if email is already registered
    existing_user = await get_user_by_email(request.email)
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Also check username (since email is the username)
    existing_username = await get_user_by_username(request.email)
    if existing_username is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create user
    full_name = f"{request.first_name} {request.last_name}".strip()
    user = await create_user(
        username=request.email,
        password_hash=hash_password(request.password),
        full_name=full_name,
        email=request.email,
        first_name=request.first_name,
        last_name=request.last_name,
        is_verified=False,
        is_admin=False,
    )

    logger.info(f"POST /auth/register | user={user.username} | pending verification")
    return RegisterResponse(
        message="Registration successful. Your account is pending admin verification.",
        username=user.username,
    )
