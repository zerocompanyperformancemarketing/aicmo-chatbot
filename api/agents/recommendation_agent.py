from langgraph.prebuilt import create_react_agent
from agents.utils.llm import get_llm
from agents.utils.prompts import RECOMMENDATION_AGENT_PROMPT


def create_recommendation_agent(tools: list):
    """Create the episode recommendation agent."""
    rec_tools = [
        t for t in tools
        if t.name in (
            "filter_by_industry_tool",
            "list_speakers_tool",
            "list_industries_tool",
            "get_episode_metadata_tool",
        )
    ]

    return create_react_agent(
        model=get_llm(),
        tools=rec_tools,
        name="recommendation_agent",
        prompt=RECOMMENDATION_AGENT_PROMPT,
    )
