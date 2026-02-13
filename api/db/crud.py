from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Conversation, Message, User
from db.session import async_session


async def get_or_create_conversation(conversation_id: str) -> Conversation:
    """Fetch an existing conversation or create a new one."""
    async with async_session() as session:
        result = await session.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()
        if conversation is None:
            conversation = Conversation(id=conversation_id)
            session.add(conversation)
            await session.commit()
            await session.refresh(conversation)
        return conversation


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
