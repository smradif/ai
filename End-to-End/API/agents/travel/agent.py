from agents.models.api import Item
from .graph import get_travel_graph
from agents.database.general import get_database_checkpointer
from langchain_core.messages import HumanMessage


async def get_travel_agent(item: Item):
    config = {"configurable": {"thread_id": item.session_id, "checkpoint_ns": "travel_agent"}}

    async def event_stream():
        async with get_database_checkpointer() as checkpointer:
            graph = get_travel_graph(
                checkpointer=checkpointer,
            )
            async for event in graph.astream_events(
                {
                    "messages": [HumanMessage(content=item.query)],
                    "user_query": item.query,
                    "flight_results": "",
                    "hotel_results": "",
                    "llm_calls": "0",
                },
                config=config,
                stream_mode="updates",
            ):
                yield event

    return event_stream()
