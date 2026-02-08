from langgraph.prebuilt import create_react_agent
from agents.utils.llm import get_llm
from agents.utils.prompts import QUOTE_AGENT_PROMPT


def create_quote_agent(tools: list):
    """Create the quote extraction agent."""
    quote_tools = [
        t for t in tools
        if t.name in ("search_transcripts_tool", "get_episode_metadata_tool")
    ]

    return create_react_agent(
        model=get_llm(),
        tools=quote_tools,
        name="quote_agent",
        prompt=QUOTE_AGENT_PROMPT,
    )
