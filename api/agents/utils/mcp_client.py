import os
from typing import Type

from fastmcp import Client
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, create_model

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

            # Create Pydantic model from MCP tool schema
            args_schema: Type[BaseModel] | None = None
            if tool.inputSchema:
                schema = tool.inputSchema
                # Extract properties and required fields
                properties = schema.get("properties", {})
                required = schema.get("required", [])

                # Build field definitions for Pydantic model
                fields = {}
                for prop_name, prop_def in properties.items():
                    field_type = str  # Default to str
                    field_default = ... if prop_name in required else None

                    # Map JSON schema types to Python types
                    if prop_def.get("type") == "integer":
                        field_type = int
                    elif prop_def.get("type") == "boolean":
                        field_type = bool
                    elif prop_def.get("type") == "number":
                        field_type = float

                    fields[prop_name] = (field_type, field_default)

                # Create dynamic Pydantic model
                if fields:
                    args_schema = create_model(
                        f"{tool.name}_schema",
                        **fields
                    )

            lc_tool = StructuredTool.from_function(
                coroutine=_make_caller(tool.name),
                name=tool.name,
                description=tool.description or "",
                args_schema=args_schema,
            )
            langchain_tools.append(lc_tool)

        return langchain_tools
