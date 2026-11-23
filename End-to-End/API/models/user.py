from pydantic import BaseModel, Field
from datetime import datetime


class UserRegistration(BaseModel):
    fname: str = Field(min_length=1, max_length=100)
    lname: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=8, max_length=256)


class User(BaseModel):
    id: int
    fname: str
    lname: str
    email: str
    created_at: datetime
    role: str = "user"


class UserLogin(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=256)
    role: str = "user"


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str = None
    token_type: str = "bearer"

class DuplicateEmailError(Exception):
    pass