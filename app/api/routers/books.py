from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.schemas.books_schemas import BookCreate, BookResponse, BookUpdate
from app.schemas.users_schemas import UserInDB
from app.core.security import get_current_user
from app.core.config import BOOKS


router = APIRouter(prefix="/books", tags=["Books (CRUD)"])

# Can be handled by database, until then, using mock data and handling here
def get_next_id():
    return max(BOOKS.keys(), default=0) + 1

@router.post("/create", response_model=BookResponse)
def create_book(book: BookCreate, current_user: UserInDB = Depends(get_current_user)):
    # Case Insensitive edge-case
    for exisiting_book in BOOKS.values():
        if exisiting_book["title"].lower() == book.title.lower():
            raise HTTPException(status_code=400, detail="Book title exists already.")

    # Create Book
    new_id = get_next_id()
    new_book = {
        "id": new_id, # Book Response
        "title": book.title,
        "author": book.author,
        "owner": current_user.username
    }

    # insert book_id
    BOOKS[new_id] = new_book
    return new_book