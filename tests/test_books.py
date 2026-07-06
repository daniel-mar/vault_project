import pytest
from tests.helpers import establish_kyber_session, auth_client_user, auth_client_admin
from tests.constants import USER_REGULAR_1, USER_REGULAR_2, USER__REGULAR_3, USER_ADMIN_1, USER_ADMIN_2, USER_ADMIN_3, BOOK_A, BOOK_B, BOOK_A_UPDATE, BOOK_B_UPDATE


@pytest.fixture(autouse=True)
def clear_books():
    from app.core.config import BOOKS
    BOOKS.clear()

# # ==========================================
# # --- CREATE READ UPDATE DELETE ---
# # ==========================================

def test_create_book(auth_client_user):
    
    # Create a book
    response_create_book = auth_client_user.post("/api/v1/books/create", json=BOOK_A)
    assert response_create_book.status_code == 200

    response_data = response_create_book.json()

    book_id = response_data["id"]
    book_owner = response_data["owner"]

    print(f"***** Book ID: {book_id} *****")
    print(f"***** Username of book creator: {book_owner} *****")
    print(f"Book Response: {response_data}")

    # Confirm creation of book within database
    assert book_id == 1
    assert book_owner == USER_REGULAR_1["username"]

# def test_sequence_create_and_read(auth_client_user):
#     """
#     Logic: Create page and redirect to dashboard with all books.
#     """
#     # Create a book
#     response_create_book = auth_client_user.post("/api/v1/books/create", json=BOOK_A)    
#     assert response_create_book.status_code == 200

#     response_data = response_create_book.json()

#     # Read created book(s) from database/memory
#     response_read_book = auth_client_user.get("/api/v1/books/view")
#     assert response_read_book.status_code == 200
    
#     # Iterate through books stored compare ID with saved response ID
#     # Compare with saved response TITLE with constants title used to create book.
#     books = response_read_book.json()
#     assert any(b["id"] == response_data and b["title"] == BOOK_A["title"] for b in books)


# def test_sequence_create_read_update_read(auth_client_user):

#     # Create book
#     response_create = auth_client_user.post("/api/v1/books", json = BOOK_B)
#     book_id = response_create.json()["id"]

#     # Read book
#     response_read_book = auth_client_user.get("/api/v1/books")
#     assert any(b["id"] == book_id for b in response_read_book.json())

#     # Update book (author)
#     response_update_book = auth_client_user.put(f"/api/v1/books/{book_id}", json = BOOK_B_UPDATE["author"])
#     assert response_update_book == 200

#     # Read updated book
#     response_read_updated_book = auth_client_user.get("/api/v1/books")
#     updated_book = next(b for b in response_read_updated_book.json() if b["id"] == book_id)
#     assert updated_book["author"] == BOOK_B_UPDATE["author"]