import uuid
from fastapi import APIRouter
from langchain_core.messages import HumanMessage, AIMessage
from models.schemas import ChatRequest, ChatResponse, Source
from agents.supervisor import build_supervisor
from db.crud import get_or_create_conversation, get_messages, save_message

router = APIRouter()

_supervisor = None


async def _get_supervisor():
    global _supervisor
    if _supervisor is None:
        _supervisor = await build_supervisor()
    return _supervisor


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chatbot endpoint. Routes message to LangGraph supervisor."""
    supervisor = await _get_supervisor()

    conversation_id = request.conversation_id or str(uuid.uuid4())

    # Ensure conversation exists in DB
    await get_or_create_conversation(conversation_id)

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

    return ChatResponse(
        response=response_text,
        sources=[],
        conversation_id=conversation_id,
    )
