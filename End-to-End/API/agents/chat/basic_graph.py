from langgraph.graph import StateGraph, START, END
import random
from pathlib import Path
from langgraph.graph import add_messages
from typing import List, TypedDict, Annotated

class GraphState(TypedDict):
    messages: Annotated[List, add_messages]
    name: str
    numbers: List[int]
    counter: int


def user_node(state: GraphState):
    state["name"] = f"Hi {state['name']}"
    state["counter"] = 0
    return state;

def random_node(state: GraphState):
     state["counter"] = state["counter"] + 1
     state["numbers"].append(random.randint(0, 10))
     return state

def router(state: GraphState):
     if state["counter"] < 5:
        return "random_node"
     return END

graph_builder = StateGraph(GraphState)
graph_builder.add_node("user_node", user_node)
graph_builder.set_entry_point("user_node")
graph_builder.add_node("random_node", random_node)
graph_builder.add_edge("user_node", "random_node")
graph_builder.add_conditional_edges(
    "random_node",
    router,
    {"random_node": "random_node", END: END},
)

graph = graph_builder.compile()
graph.invoke({"messages": [], "name": "John", "numbers": [], "counter": -1})

graph_image = graph.get_graph().draw_mermaid_png()
image_path = Path(__file__).with_name("graph.png")
image_path.write_bytes(graph_image)
print(f"Graph image saved to {image_path}")
