import asyncio
import os
from fastmcp import Client
from langchain.mcp import MCPAdapter
from dotenv import load_dotenv

load_dotenv()
mcp_server_url = os.getenv("MCP_SERVER_URL")
# access_token = os.getenv("MCP_ACCESS_TOKEN")
# if not access_token:
#     raise RuntimeError(
#         "Set MCP_ACCESS_TOKEN to a valid access token from POST /users/login."
#     )

# client = Client(mcp_server_url, auth=access_token)


# async def call_tool(name: str):
#     async with client:
#         tools = await client.list_tools()
#         for tool in tools:
#             print("tool", tool.name, tool.description)
#         print("**** tools", [
#                 {"name": tool.name, "description": tool.description} for tool in tools
#             ])
#         result = await client.call_tool("greet", {"name": name})
#         print(result)


# asyncio.run(call_tool("Ford"))


class MCPClient:
    def __init__(self, access_token):
        self.client = Client(mcp_server_url, auth=access_token)

    async def get_tools(self):
        adapter = MCPAdapter(self.client)
        return await adapter.list_tools()
