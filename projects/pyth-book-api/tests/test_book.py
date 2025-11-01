import pytest
import requests

BASE_URL = "http://localhost:8000"  # Altere para o URL correto da sua API

@pytest.fixture
def create_author():
    def _create_author(name):
        response = requests.post(f"{BASE_URL}/authors", json={"name": name})
        assert response.status_code == 200
        return response.json()["id"]
    return _create_author

@pytest.fixture
def create_book():
    def _create_book(name, author_id):
        response = requests.post(f"{BASE_URL}/books", json={"name": name, "author_id": author_id})
        return response
    return _create_book

@pytest.fixture
def create_and_get_book_id(create_author, create_book):
    def _create_and_get_book_id(name, author_name):
        author_id = create_author(author_name)
        response = create_book(name, author_id)
        assert response.status_code == 200
        return response.json()["id"]
    return _create_and_get_book_id

def test_list_books_without_query():
    response = requests.get(f"{BASE_URL}/books")
    assert response.status_code == 200

@pytest.mark.parametrize("author_id, expected_status", [
    ("1", 200),  # Valid author_id
    ("", 200),   # Empty author_id (no filtering applied)
    ("abc", 422),  # Non-integer author_id
])
def test_list_books_with_query(author_id, expected_status, create_author):
    if author_id == "1":
        create_author("Author for List Books")
    response = requests.get(f"{BASE_URL}/books", params={"author_id": author_id})
    assert response.status_code == expected_status

@pytest.mark.parametrize("name, author_id, expected_status", [
    ("ValidBook", 1, 200),
    ("", 1, 422),
    ("x" * 255, 1, 200),
    ("x", 1, 200),
    ("ValidBook", -1, 422),
    ("ValidBook", 0, 422),
    ("ValidBook", "abc", 422),
])
def test_create_book(name, author_id, expected_status, create_author, create_book):
    if author_id == 1:
        author_id = create_author("Author for Create Book")
    response = create_book(name, author_id)
    assert response.status_code == expected_status

@pytest.mark.parametrize("book_id, expected_status", [
    (1, 200),  # Valid ID
    (-1, 422),  # Negative ID
    (0, 422),  # Zero ID
    ("abc", 422),  # Non-integer ID
])
def test_get_book_by_id(book_id, expected_status, create_and_get_book_id):
    if book_id == 1:
        book_id = create_and_get_book_id("Book for Get", "Author for Get Book")
    response = requests.get(f"{BASE_URL}/books/{book_id}")
    assert response.status_code == expected_status

@pytest.mark.parametrize("book_id, name, author_id, expected_status", [
    (1, "UpdatedBook", 1, 200),
    (1, "", 1, 422),
    (1, "x" * 255, 1, 200),
    (1, "x", 1, 200),
    (1, "ValidBook", -1, 422),
    (1, "ValidBook", 0, 422),
    (1, "ValidBook", "abc", 422),
    (-1, "ValidBook", 1, 422),
    (0, "ValidBook", 1, 422),
    ("abc", "ValidBook", 1, 422),
])
def test_update_book(book_id, name, author_id, expected_status, create_author, create_and_get_book_id):
    if author_id == 1:
        author_id = create_author("Author for Update Book")
    if book_id == 1:
        book_id = create_and_get_book_id("Book for Update", "Author for Update Book")
    response = requests.patch(f"{BASE_URL}/books/{book_id}", json={"name": name, "author_id": author_id})
    assert response.status_code == expected_status

@pytest.mark.parametrize("book_id, expected_status", [
    (1, 204),  # Valid ID
    (-1, 422),  # Negative ID
    (0, 422),  # Zero ID
    ("abc", 422),  # Non-integer ID
])
def test_delete_book(book_id, expected_status, create_and_get_book_id):
    if book_id == 1:
        book_id = create_and_get_book_id("Book for Delete", "Author for Delete Book")
    response = requests.delete(f"{BASE_URL}/books/{book_id}")
    assert response.status_code == expected_status