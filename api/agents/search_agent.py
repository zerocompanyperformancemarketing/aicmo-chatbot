from langgraph.prebuilt import create_react_agent
from agents.utils.llm import get_llm
from agents.utils.prompts import SEARCH_AGENT_PROMPT


def create_search_agent(tools: list):
    """Create the search agent with transcript search tools."""
    search_tools = [
        t for t in tools
        if t.name in ("search_transcripts_tool", "filter_by_industry_tool", "filter_by_speaker_tool")
    ]

    return create_react_agent(
        model=get_llm(),
        tools=search_tools,
        name="search_agent",
        prompt=SEARCH_AGENT_PROMPT,
    )
