from fastapi.params import Depends
from fastapi.responses import StreamingResponse
import json
from agents.models.api import Item
from .constants import PERSON_NODE, FINAL_OUTPUT
from auth.jwt import decode_access_token
from agents.person.agent import get_person_agent


def person_api_builder(app):
    @app.post("/person-agent")
    async def person_agent(item: Item, token: str = Depends(decode_access_token)):
        
        async def event_stream(item: Item):
            yield f"data: {json.dumps({'status': 'started'})}\n\n"

            events = await get_person_agent(item)
            # final_data = None
            async for event in events:
                if "__interrupt__" in event:
                    interrupt_value = event["__interrupt__"][0].value
                    yield f"data: {json.dumps({'status': 'partial', 'chunk': interrupt_value})}\n\n"
                elif PERSON_NODE in event and isinstance(
                    event[PERSON_NODE], dict
                ) and FINAL_OUTPUT in event[PERSON_NODE] and event[PERSON_NODE][FINAL_OUTPUT] is not None:
                        final_data = event[PERSON_NODE][FINAL_OUTPUT]
                        chunk = final_data["message"]
                        del final_data["message"]
                        yield f"data: {json.dumps({'status': 'partial', 'chunk': chunk})}\n\n"
                        yield f"data: {json.dumps({'status': 'done', 'data': {'final_data': final_data}})}\n\n"
                        return

                yield f"data: {json.dumps({'status': 'done'})}\n\n"
    
        return StreamingResponse(event_stream(item), media_type="text/event-stream")
    
