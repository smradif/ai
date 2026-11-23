from langgraph.graph import StateGraph, START, END
import random
from langgraph.graph import add_messages
from langgraph.prebuilt.tool_node import ToolNode

# from typing import List, Annotated
from typing_extensions import List, TypedDict, Annotated, Sequence
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    SystemMessage,
    AIMessage,
    ToolMessage,
)
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver


class ChatState(TypedDict):
    messages: Annotated[List, add_messages]


@tool
def add(a: int, b: int):
    """This is an addition function that add 2 numbers together"""
    print(f"****** Add Tool. Adding: {a} {b}")
    return a + b


@tool
def subtract(a: int, b: int):
    """A tool to subtract two numbers"""
    print(f"File updated")


tools = [add, subtract]


def get_chat_graph(llm, checkpointer):
    def main_node(state: ChatState):
        response = llm.bind_tools(tools).invoke(
            [
                SystemMessage(
                    content="You are my AI assistant, please answer my query to the best of your ability"
                ),
            ]
            + state["messages"]
        )
        return {"messages": [response]}

    def should_continue(state: ChatState):
        last_message = state["messages"][-1]
        if not last_message.tool_calls or len(last_message.tool_calls) == 0:
            return "end"
        return "continue"

    tool_node = ToolNode(tools=tools)

    graph_builder = StateGraph(ChatState)

    graph_builder.add_node("main_node", main_node)
    graph_builder.add_node("tool_node", tool_node)
    graph_builder.add_conditional_edges(
        "main_node", should_continue, {"end": END, "continue": "tool_node"}
    )

    #     graph_builder.add_edge("main_node", "tool_node")
    graph_builder.add_edge("tool_node", "main_node")
    graph_builder.set_entry_point("main_node")

    graph = graph_builder.compile()

    return graph
