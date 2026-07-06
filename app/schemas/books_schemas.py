from pydantic import BaseModel
from typing import Optional
import uuid

class BookBase(BaseModel):
    title: str
    author: str

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None

class BookResponse(BaseModel):
    id: int
    owner: str