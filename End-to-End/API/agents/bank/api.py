import os
from fastapi.params import Depends
from fastapi.responses import StreamingResponse
import json
from agents.chat.agent import get_chat_agent
from agents.models.api import Item
from .db import ChatDatabase
import asyncpg
from database.postgres import get_postgres
from auth.jwt import decode_access_token
from agents.chat.utils import convert_to_conversation, convert_to_messages


def chat_api_builder(app):

    @app.post("/chat-agent")
    async def chat_agent_query(
        item: Item,
        token: str = Depends(decode_access_token),
        db_pool: asyncpg.Pool = Depends(get_postgres),
    ):
        """POST endpoint that queries the Chat Agent and streams SSE chunks."""

        async def event_stream(item: Item):
            yield f"data: {json.dumps({'status': 'started'})}\n\n"
            previous_messages = []
            if item.previous_state_id is not None:
                    db = ChatDatabase(pool=db_pool)
                    chat = await db.get_chat(item.previous_state_id)
                    if chat is not None:
                        previous_messages = convert_to_messages(chat["conversation"])
            events = await get_chat_agent(item, token, previous_messages=previous_messages)
            async for chunk in events:
                if (
                    isinstance(chunk, dict)
                    and chunk.get("type") == "final_state"
                    and item.query != "reset"
                ):
                    messages = (chunk.get("values"))["messages"]
                    response = convert_to_conversation(messages)
                    db = ChatDatabase(pool=db_pool)
                    await db.save_chat(
                        token["user_id"],
                        response["title"],
                        response["conversation"],
                        item.vendor_id,
                        item.session_id,
                    )

                    continue

                chunk_text = ""
                if isinstance(chunk, dict):
                    if "data" in chunk and "chunk" in chunk["data"]:
                        data = chunk["data"]["chunk"]
                        chunk_text = data.content if hasattr(data, "content") else ""
                else:
                    chunk_text = chunk.content if hasattr(chunk, "content") else ""
                if chunk_text:
                    yield f"data: {json.dumps({'status': 'partial', 'chunk': chunk_text})}\n\n"

            yield f"data: {json.dumps({'status': 'done'})}\n\n"

        return StreamingResponse(event_stream(item), media_type="text/event-stream")

    @app.get("/vendors")
    async def get_vendors(db_pool: asyncpg.Pool = Depends(get_postgres)):
        db = ChatDatabase(pool=db_pool)
        vendors = await db.get_vendors()
        return vendors

    @app.get("/chats/{vendor_id}")
    async def get_chats(
        vendor_id: int,
        token: str = Depends(decode_access_token),
        db_pool: asyncpg.Pool = Depends(get_postgres),
    ):
        db = ChatDatabase(pool=db_pool)
        chats = await db.get_chats(token["user_id"], vendor_id)
        return chats

    @app.get("/chat/{id}")
    async def get_chat(
        id: int,
        token: str = Depends(decode_access_token),
        db_pool: asyncpg.Pool = Depends(get_postgres),
    ):
        db = ChatDatabase(pool=db_pool)
        chat = await db.get_chat(id)
        return chat
