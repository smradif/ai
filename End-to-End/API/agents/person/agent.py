# from dotenv import load_dotenv
from langgraph.types import Command
from agents.models.api import Item
from .graph import get_person_graph

async def get_person_agent(item: Item):
    graph = get_person_graph()
    config = {"configurable": {"thread_id": f"person_agent:{item.session_id}"}}
    if item.query.strip().lower() == "reset":
        input_data = {"reset": True}
        return graph.astream(input_data, config)
    state = await graph.aget_state(config)
    
    if len(state.next) > 0:
        # Resume the existing thread with user input
        input_data = Command(resume=item.query)
    else:
        input_data = {"name": None, "age": None}
    events =  graph.astream(
        input_data,
        config,
        stream_mode="updates",
    )

    return events
