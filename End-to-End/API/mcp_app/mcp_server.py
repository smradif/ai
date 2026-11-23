from fastmcp import FastMCP
from fastmcp.server.dependencies import get_access_token
from auth.custom_token_provider import CustomTokenVerifier
from .db import NoteDatabase

def verify_permissions(scope: str) -> bool:
    """Return (user_id, raw_token) for the caller, or raise if they lack the scopes."""
    token = get_access_token()
    if token is None or not scope in token.scopes:
        raise PermissionError("Authentication required")
    return True

def create_mcp_server() -> FastMCP:

    mcp = FastMCP("101 MCP Server", auth=CustomTokenVerifier())

    @mcp.tool()
    async def list_my_notes() -> list[dict]:
        """List all saved notes"""
        verify_permissions("read")
        db = NoteDatabase()
        return await db.get_notes()

    @mcp.tool()
    async def add_note(text: str) -> list[dict]:
        """Save a new note"""
        verify_permissions("write")
        db = NoteDatabase()
        return await db.save_note(1, text)

    @mcp.tool()
    async def delete_note(id: int) -> str:
        """Delete a note by id"""
        verify_permissions("write")
        db = NoteDatabase()
        result = await db.remove_note(id)
        return "Not deleted" if result else f"Error deleteing note with id {id}"

    @mcp.tool()
    def add_tool(a: int, b: int) -> int:
        """This is an addition function that add 2 numbers together"""
        verify_permissions("write")
        return a + b


    @mcp.tool()
    def subtract_tool(a: int, b: int) -> int:
        """A tool to subtract two numbers"""
        return a - b
    
    return mcp
