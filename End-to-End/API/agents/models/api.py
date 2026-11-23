from typing import Optional
from pydantic import BaseModel

class Item(BaseModel):
    query: Optional[str] = None
    vendor_id: Optional[int] = None
    session_id: Optional[str] = None
    previous_state_id: Optional[int] = None