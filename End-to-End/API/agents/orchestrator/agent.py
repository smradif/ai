from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from agents.database.general import get_database_checkpointer
from agents.models.api import Item
from .graph import get_orchestrator_graph

async def get_orchestrator_agent(item: Item):
    config = {"configurable": {"thread_id": f"orchestrator_agent:{item.session_id}"}}

    async def event_stream():
        if not item.query or not item.query.strip():
            yield {
                "data": {
                    "chunk": AIMessage(
                        content="I am a support agent. How can I help you?"
                    )
                }
            }
            return

        async with get_database_checkpointer() as checkpointer:
            graph = get_orchestrator_graph(checkpointer=checkpointer)
            emitted_messages: set[str] = set()
            async for event in graph.astream(
                {
                    "query": item.query,
                    # "messages": [
                    #     HumanMessage(content=item.query),
                    # ],
                },
                config=config,
                stream_mode="updates",
            ):
                for node_update in event.values():
                    for message in node_update.get("messages", []):
                        if (
                            isinstance(message, AIMessage)
                            and isinstance(message.content, str)
                            and message.content not in emitted_messages
                        ):
                            emitted_messages.add(message.content)
                        yield {"data": {"chunk": message}}

    return event_stream()
