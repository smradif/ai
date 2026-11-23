from langgraph.graph import add_messages
from pydantic import BaseModel, Field
from typing import List, TypedDict, Annotated
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, AnyMessage

class Output(BaseModel):
    """ A float value that represent the amount the user want to transfer"""
    amount: float = Field(
        description="The amount the user wants to transfer")
    # amount: Optional[float]
    # country: Optional[str]
    # currency: Optional[str]
    # name: str
    # city: str

class TravelState(TypedDict):
    messages: Annotated[List, add_messages]
    user_query: str
    flight_results: str
    hotel_results: str
    itinerary: str
    llm_call: int