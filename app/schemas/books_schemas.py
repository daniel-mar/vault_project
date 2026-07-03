from pydantic import BaseModel
import uuid

class BookCreate(BaseModel):
    title: str
    author: str

class BookResponse(BaseModel):
    id: str