import logging
from fastapi import APIRouter, Depends, HTTPException

from auth import get_current_user
from models.schemas import (
    ConversationResponse,
    ConversationListResponse,
    ConversationSummary,
    MessageResponse,
)
from db.crud import (
    get_user_id_by_username,
    get_conversations_for_user,
    get_conversation_by_id,
    get_first_user_message,
    get_messages,
    delete_conversation,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("", response_model=ConversationListResponse)
async def list_conversations(username: str = Depends(get_current_user)):
    """List all conversations for the current user."""
    logger.info(f"GET /conversations | user={username}")

    user_id = await get_user_id_by_username(username)
    if user_id is None:
        raise HTTPException(status_code=404, detail="User not found")

    conversations = await get_conversations_for_user(user_id)

    summaries = []
    for conv in conversations:
        preview = await get_first_user_message(conv.id)
        summaries.append(
            ConversationSummary(
                id=conv.id,
                preview=preview[:100] + "..." if preview and len(preview) > 100 else (preview or "New conversation"),
                created_at=conv.created_at,
                updated_at=conv.updated_at,
            )
        )

    return ConversationListResponse(conversations=summaries)


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: str, username: str = Depends(get_current_user)):
    """Get a conversation with all its messages."""
    logger.info(f"GET /conversations/{conversation_id} | user={username}")

    user_id = await get_user_id_by_username(username)
    if user_id is None:
        raise HTTPException(status_code=404, detail="User not found")

    conversation = await get_conversation_by_id(conversation_id, user_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = await get_messages(conversation_id)
    message_responses = [
        MessageResponse(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            sources=msg.sources,
            created_at=msg.created_at,
        )
        for msg in messages
    ]

    return ConversationResponse(
        id=conversation.id,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=message_responses,
    )


@router.delete("/{conversation_id}")
async def remove_conversation(conversation_id: str, username: str = Depends(get_current_user)):
    """Delete a conversation."""
    logger.info(f"DELETE /conversations/{conversation_id} | user={username}")

    user_id = await get_user_id_by_username(username)
    if user_id is None:
        raise HTTPException(status_code=404, detail="User not found")

    deleted = await delete_conversation(conversation_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {"status": "deleted", "conversation_id": conversation_id}
