from langgraph.graph import StateGraph, END
from langgraph.graph import add_messages
from langgraph.prebuilt.tool_node import ToolNode
from typing_extensions import List, TypedDict, Annotated
from langchain_core.tools import tool
from agents.llm.llm import get_llm


class ChatState(TypedDict):
     messages: Annotated[List, add_messages]

class ChatOutput(TypedDict):
     answer: str

# @tool
# def add_tool(a: int, b: int):
#     """This is an addition function that add 2 numbers together"""
#     print(f"****** Add Tool. Adding: {a} {b}")
#     return a + b


# @tool
# def subtract_tool(a: int, b: int):
#     """A tool to subtract two numbers"""
#     print(f"****** Subtract Tool. Subtracting: {a} {b}")
#     return a - b

# tools = [add_tool, subtract_tool]


def get_chat_graph(checkpointer, tools):
     _, llm_with_tools, _ = get_llm(tools=tools, state=ChatOutput)

     def main_node(state: ChatState):
          response = llm_with_tools.invoke(state["messages"])
          return {"messages": [response]}

     def should_continue(state: ChatState):
             last_message = state["messages"][-1]
             if not last_message.tool_calls or len(last_message.tool_calls) == 0:
                 return "end"
             return "continue"

     graph_builder = StateGraph(ChatState)
     tool_node = ToolNode(tools=tools)
     graph_builder.add_node("main_node", main_node)
     graph_builder.add_node("tool_node", tool_node)
     graph_builder.add_conditional_edges(
          "main_node", should_continue, {"end": END, "continue": "tool_node"}
     )
     graph_builder.add_edge("tool_node", "main_node")
     graph_builder.set_entry_point("main_node")

     graph = graph_builder.compile(checkpointer=checkpointer)

     return graph
