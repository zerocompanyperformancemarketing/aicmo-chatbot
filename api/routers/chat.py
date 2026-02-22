import logging
import uuid
from fastapi import APIRouter, Depends
from langchain_core.messages import HumanMessage, AIMessage
from logging_utils import truncate
from models.schemas import ChatRequest, ChatResponse, Source
from agents.supervisor import build_supervisor
from auth import get_current_user
from db.crud import get_or_create_conversation, get_messages, save_message, get_user_id_by_username

logger = logging.getLogger(__name__)

router = APIRouter()

_supervisor = None


async def _get_supervisor():
    global _supervisor
    if _supervisor is None:
        logger.info("Initializing supervisor (first request)")
        _supervisor = await build_supervisor()
        logger.info("Supervisor initialized")
    return _supervisor


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, username: str = Depends(get_current_user)):
    """Main chatbot endpoint. Routes message to LangGraph supervisor."""
    logger.info(f"POST /chat | message={truncate(request.message)}, conversation_id={request.conversation_id}")
    supervisor = await _get_supervisor()

    # Get user_id for conversation ownership
    user_id = await get_user_id_by_username(username)

    conversation_id = request.conversation_id or str(uuid.uuid4())

    # Ensure conversation exists in DB (with user ownership)
    await get_or_create_conversation(conversation_id, user_id)

    # Load prior messages for context
    prior_messages = await get_messages(conversation_id)
    history = []
    for msg in prior_messages:
        if msg.role == "user":
            history.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            history.append(AIMessage(content=msg.content))

    # Append current user message
    history.append(HumanMessage(content=request.message))

    result = await supervisor.ainvoke({
        "messages": history,
    })

    # Extract the last AI message as the response
    ai_messages = [m for m in result["messages"] if hasattr(m, "content") and m.type == "ai"]
    response_text = ai_messages[-1].content if ai_messages else "I couldn't find an answer."

    # Save user message and assistant response to DB
    await save_message(conversation_id, "user", request.message)
    await save_message(conversation_id, "assistant", response_text)

    logger.info(f"POST /chat response | conversation_id={conversation_id} | {truncate(response_text)}")
    return ChatResponse(
        response=response_text,
        sources=[],
        conversation_id=conversation_id,
    )
