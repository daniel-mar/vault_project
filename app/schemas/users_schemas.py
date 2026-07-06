from pydantic import BaseModel, Field
from typing import Optional

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=8, max_length=72)
    role: str = Field(default="user", pattern="^(admin|user)$")


class UserResponse(BaseModel):
    username: str
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserInDB(BaseModel):
    username: str
    role: str
