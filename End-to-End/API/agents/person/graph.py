from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import MemorySaver
from .constants import PERSON_NODE, NAME_NODE, AGE_NODE, RESULT_NODE
from validators.person import validate_age, validate_name

checkpointer = MemorySaver()

class UserState(TypedDict, total=False):
    name: Optional[str]
    age: Optional[int]
    final_output: Optional[dict]
    reset: Optional[bool]
    error: Optional[str]

def person_node(state: UserState):
    # Handle reset request
    if state.get("reset"):
        state = {"name": None, "age": None, "final_output": None, "reset": False}

    return state

def person_router(state: UserState):
    if state.get("name") is None:
        return NAME_NODE
    if state.get("age") is None:
        return AGE_NODE
    return RESULT_NODE

def name_node(state: UserState):
     # Handle name
    if state.get("error") == "name_error":
        name = interrupt("Hi! Please provide a name using text only.")
    else:
        name = interrupt("What is your name?")
    
    if validate_name(name):
        return Command(goto=PERSON_NODE, update={**state, "name": name.strip()})
    return Command(goto=PERSON_NODE, update={**state, "name": None, "age": None, "error": "name_error"})

def age_node(state: UserState):
    if( state.get("error") == "age_error"):
        age = interrupt(f"Hi {state['name']}! Please provide an age from 18 to 90.")
    else:
        age= interrupt(f"Hi {state['name']}! How old are you?")
    try:
        if not validate_age(age):
            return Command(goto=PERSON_NODE, update={**state, "age": None, "error": "age_error"})
        return Command(goto=PERSON_NODE, update={**state, "age": int(age)})
    except (ValueError, TypeError):
        return Command(goto=PERSON_NODE, update={**state, "age": None, "error": "age_error"})

def result_node(state: UserState):
    final_output = {**state, "name": state["name"], "age": state["age"], "message": f"Thank you, {state['name']} is {state['age']} years old."}
    return Command(goto=PERSON_NODE, update={**state, "final_output": final_output})


def get_person_graph():
    builder = StateGraph(UserState)
    # Nodes
    builder.add_node(PERSON_NODE, person_node)
    builder.set_entry_point(PERSON_NODE)
    builder.add_node(NAME_NODE, name_node)
    builder.add_node(AGE_NODE, age_node)
    builder.add_node(RESULT_NODE, result_node)

    # Edges
    builder.add_conditional_edges(PERSON_NODE, person_router)
    builder.add_edge(RESULT_NODE, END)

    graph = builder.compile(checkpointer=checkpointer)

    return graph

person_graph = get_person_graph()  # Placeholder for llm_with_tools, tools, structured_llm
