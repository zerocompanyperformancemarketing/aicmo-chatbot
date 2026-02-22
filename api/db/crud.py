from datetime import datetime

from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Conversation, Message, User
from db.session import async_session


async def get_or_create_conversation(conversation_id: str, user_id: int | None = None) -> Conversation:
    """Fetch an existing conversation or create a new one."""
    async with async_session() as session:
        result = await session.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()
        if conversation is None:
            conversation = Conversation(id=conversation_id, user_id=user_id)
            session.add(conversation)
            await session.commit()
            await session.refresh(conversation)
        return conversation


async def get_user_id_by_username(username: str) -> int | None:
    """Get user ID from username."""
    async with async_session() as session:
        result = await session.execute(
            select(User.id).where(User.username == username)
        )
        return result.scalar_one_or_none()


async def get_conversations_for_user(user_id: int, limit: int = 50) -> list[Conversation]:
    """List conversations for a user, ordered by updated_at desc."""
    async with async_session() as session:
        result = await session.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())


async def get_conversation_by_id(conversation_id: str, user_id: int) -> Conversation | None:
    """Get a single conversation with ownership check."""
    async with async_session() as session:
        result = await session.execute(
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .where(Conversation.user_id == user_id)
        )
        return result.scalar_one_or_none()


async def get_first_user_message(conversation_id: str) -> str | None:
    """Get the first user message of a conversation for preview."""
    async with async_session() as session:
        result = await session.execute(
            select(Message.content)
            .where(Message.conversation_id == conversation_id)
            .where(Message.role == "user")
            .order_by(Message.created_at)
            .limit(1)
        )
        return result.scalar_one_or_none()


async def delete_conversation(conversation_id: str, user_id: int) -> bool:
    """Delete a conversation and its messages (with ownership check)."""
    async with async_session() as session:
        # Verify ownership
        result = await session.execute(
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .where(Conversation.user_id == user_id)
        )
        conversation = result.scalar_one_or_none()
        if conversation is None:
            return False

        # Delete conversation (messages deleted via cascade)
        await session.delete(conversation)
        await session.commit()
        return True


async def get_messages(conversation_id: str) -> list[Message]:
    """Get all messages for a conversation, ordered by creation time."""
    async with async_session() as session:
        result = await session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        return list(result.scalars().all())


async def save_message(
    conversation_id: str,
    role: str,
    content: str,
    sources: list[dict] | None = None,
) -> Message:
    """Save a message to the database."""
    async with async_session() as session:
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            sources=sources,
        )
        session.add(message)
        await session.commit()
        await session.refresh(message)
        return message


async def get_user_by_username(username: str) -> User | None:
    """Fetch a user by username."""
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()


async def create_user(
    username: str,
    password_hash: str,
    full_name: str,
    email: str,
    first_name: str = "",
    last_name: str = "",
    is_verified: bool = False,
    is_admin: bool = False,
) -> User:
    """Create a new user."""
    async with async_session() as session:
        user = User(
            username=username,
            password_hash=password_hash,
            full_name=full_name,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_verified=is_verified,
            is_admin=is_admin,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


async def update_user_password(username: str, password_hash: str) -> bool:
    """Update a user's password hash and password_changed_at. Returns True if updated."""
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.username == username)
        )
        user = result.scalar_one_or_none()
        if user is None:
            return False
        user.password_hash = password_hash
        user.password_changed_at = datetime.utcnow()
        await session.commit()
        return True


async def get_user_by_email(email: str) -> User | None:
    """Fetch a user by email (case-insensitive)."""
    async with async_session() as session:
        result = await session.execute(
            select(User).where(func.lower(User.email) == email.lower())
        )
        return result.scalar_one_or_none()


async def get_user_by_id(user_id: int) -> User | None:
    """Fetch a user by ID."""
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()


async def get_all_users(limit: int = 100, offset: int = 0) -> list[User]:
    """Get all users with pagination."""
    async with async_session() as session:
        result = await session.execute(
            select(User)
            .order_by(User.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())


async def get_pending_users() -> list[User]:
    """Get all users pending verification."""
    async with async_session() as session:
        result = await session.execute(
            select(User)
            .where(User.is_verified == False)
            .order_by(User.created_at.desc())
        )
        return list(result.scalars().all())


async def verify_user(user_id: int, verified: bool = True) -> bool:
    """Set user verification status. Returns True if updated."""
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if user is None:
            return False
        user.is_verified = verified
        await session.commit()
        return True


async def set_user_active(user_id: int, active: bool) -> bool:
    """Set user active status. Returns True if updated."""
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if user is None:
            return False
        user.is_active = active
        await session.commit()
        return True


async def delete_user(user_id: int) -> bool:
    """Delete a user and all their conversations. Returns True if deleted."""
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if user is None:
            return False
        await session.delete(user)
        await session.commit()
        return True


async def update_user_password_by_id(user_id: int, password_hash: str) -> bool:
    """Update a user's password by ID and update password_changed_at. Returns True if updated."""
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if user is None:
            return False
        user.password_hash = password_hash
        user.password_changed_at = datetime.utcnow()
        await session.commit()
        return True
