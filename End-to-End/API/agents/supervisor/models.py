from typing import List, Optional
from langgraph.graph import add_messages
from typing_extensions import TypedDict, Annotated, NotRequired
from pydantic import BaseModel, Field
from agents.models.state import Output

class MoneyState(TypedDict):
    messages: Annotated[List, add_messages]
    amount: NotRequired[Optional[float]]
    country: NotRequired[Optional[str]]
    currency: NotRequired[Optional[str]]
    confirmation: bool
    awaiting_confirmation: NotRequired[bool]
    final_output: NotRequired[Optional[Output]]

class MoneyAmountState(TypedDict):
    messages:List[str]
    amount: float
    currency: str

