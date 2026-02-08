from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """Shared state schema for all agents in the LangGraph supervisor."""
    messages: Annotated[list, add_messages]
