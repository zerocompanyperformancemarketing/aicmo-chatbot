import logging
from langgraph.prebuilt import create_react_agent
from agents.utils.llm import get_llm
from agents.utils.prompts import SUMMARY_AGENT_PROMPT

logger = logging.getLogger(__name__)


def create_summary_agent(tools: list):
    """Create the summary agent for topic-based summaries."""
    summary_tools = [
        t for t in tools
        if t.name in ("search_transcripts_tool", "get_episode_metadata_tool")
    ]
    logger.info(f"create_summary_agent | tools={[t.name for t in summary_tools]}")

    return create_react_agent(
        model=get_llm(),
        tools=summary_tools,
        name="summary_agent",
        prompt=SUMMARY_AGENT_PROMPT,
    )
