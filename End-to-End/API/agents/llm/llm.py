from langchain_ollama import OllamaLLM, ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import BaseTool
from pydantic import BaseModel
from typing import Sequence

memory = MemorySaver()

llm = ChatOllama(model="gpt-oss:20b")

def get_llm(
    tools: Sequence[BaseTool] | None = None,
    state: type[BaseModel] | None = None,
):
    llm_with_tools = llm
    llm_with_state = llm
    if state is not None:
        llm_with_state = llm.with_structured_output(state)
    if tools:
        llm_with_tools = llm.bind_tools(list(tools))
    return llm, llm_with_tools, llm_with_state
