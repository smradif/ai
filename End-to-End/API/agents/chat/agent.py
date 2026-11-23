# from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from typing import List
from agents.models.api import Item
from agents.database.general import get_database_checkpointer
from .graph import get_chat_graph
from mcp_app.mcp_client import MCPClient

system_message = SystemMessage(content="""
                                    You are a helpful chat agent.
                                    Your task is to ask the user to enter the information needed and you should be able
                                    to help them in an way you can.
                                    If you can't answer the question, please advice the user.
                                    You should be polite and entertaining.
                                    """)


def get_chat_message(item: Item, previous_messages: List[BaseMessage] = None):
    if item.previous_state_id is not None:
        return [
            system_message,
            *(previous_messages or []),
            HumanMessage(content=item.query),
        ]
    return [
        system_message,
        HumanMessage(content=item.query),
    ]


async def get_chat_agent(item: Item, token: str, previous_messages: List[BaseMessage] = None):
    config = {"configurable": {"thread_id": f"chat_agent:{item.session_id}"}}

    async def event_stream():
        async with get_database_checkpointer() as checkpointer:
            print("tooooooools", token)
            tools = await MCPClient(access_token=token).get_tools()
            graph = get_chat_graph(checkpointer=checkpointer, tools=tools)
            messages = get_chat_message(item, previous_messages)
            async for event in graph.astream_events(
                {"messages": messages},
                config=config,
                stream_mode="updates",
            ):
                yield event
            # Rerun the graph to get the final state after all events have been processed
            snapshot = await graph.aget_state(config)
            yield {
                "type": "final_state",
                "values": snapshot.values,
            }

    return event_stream()
