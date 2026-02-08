import os

from fastmcp import Client
from langchain_core.tools import StructuredTool

_MCP_URL = os.getenv("MCP_URL", "http://mcp:8001/mcp")


async def get_mcp_tools() -> list[StructuredTool]:
    """Fetch MCP tools and convert them to LangChain-compatible tools."""
    async with Client(_MCP_URL) as client:
        mcp_tools = await client.list_tools()

        langchain_tools = []
        for tool in mcp_tools:
            def _make_caller(tool_name: str):
                async def call_tool(**kwargs):
                    async with Client(_MCP_URL) as c:
                        return await c.call_tool(tool_name, kwargs)
                return call_tool

            lc_tool = StructuredTool.from_function(
                coroutine=_make_caller(tool.name),
                name=tool.name,
                description=tool.description or "",
            )
            langchain_tools.append(lc_tool)

        return langchain_tools
