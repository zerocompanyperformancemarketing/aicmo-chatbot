from sqlalchemy import select, delete
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
    username: str, password_hash: str, full_name: str, email: str
) -> User:
    """Create a new user."""
    async with async_session() as session:
        user = User(
            username=username,
            password_hash=password_hash,
            full_name=full_name,
            email=email,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


async def update_user_password(username: str, password_hash: str) -> bool:
    """Update a user's password hash. Returns True if updated."""
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.username == username)
        )
        user = result.scalar_one_or_none()
        if user is None:
            return False
        user.password_hash = password_hash
        await session.commit()
        return True
