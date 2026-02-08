from langgraph_supervisor import create_supervisor
from agents.utils.llm import get_llm
from agents.utils.mcp_client import get_mcp_tools
from agents.utils.prompts import SUPERVISOR_SYSTEM_PROMPT
from agents.search_agent import create_search_agent
from agents.quote_agent import create_quote_agent
from agents.summary_agent import create_summary_agent
from agents.recommendation_agent import create_recommendation_agent


async def build_supervisor():
    """Build the LangGraph supervisor with all sub-agents."""
    tools = await get_mcp_tools()

    search_agent = create_search_agent(tools)
    quote_agent = create_quote_agent(tools)
    summary_agent = create_summary_agent(tools)
    recommendation_agent = create_recommendation_agent(tools)

    supervisor = create_supervisor(
        agents=[search_agent, quote_agent, summary_agent, recommendation_agent],
        model=get_llm(),
        prompt=SUPERVISOR_SYSTEM_PROMPT,
    )

    return supervisor.compile()
