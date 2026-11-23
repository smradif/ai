from fastapi.params import Depends
from fastapi.responses import StreamingResponse
import json
from agents.money.agent import get_money_transfer_agent
from agents.models.api import Item

from auth.jwt import decode_access_token


def money_transfer_api_builder(app):
    @app.post("/money-agent")
    async def money_agent_query(item: Item, token: str = Depends(decode_access_token)):
        """POST endpoint that queries the Money Agent and streams SSE chunks."""

        async def event_stream(item: Item):
            # start event
            yield f"data: {json.dumps({'status': 'started'})}\n\n"
            events = await get_money_transfer_agent(item)
            async for chunk in events:
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


