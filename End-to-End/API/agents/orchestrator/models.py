from typing import Literal, List
from langgraph.graph import add_messages
from typing_extensions import TypedDict, Annotated


class TicketState(TypedDict):
    query: str
    ticket_id: str
    category: Literal["billing", "technical", "general"]
    faq_match: str
    resolution: str
    needs_esculation: bool
    final_response: str
    priority: Literal["low", "medium", "high"]
    conversation_history: list[str]
    messages: Annotated[List, add_messages]
    timestamp: str


class CategoryState(TypedDict):
    category: Literal["billing", "technical", "general"]
