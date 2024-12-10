import pytest
from api import app

@pytest.fixture
def mock_db(mocker):
    mock_conn = mocker.patch('flask_mysqldb.MySQL.connection')
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_cursor

def test_index():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    assert b"WELCOME TO BOOKSELLER DATABASE" in response.data

def test_get_authors_empty(mock_db):
    mock_db.fetchall.return_value = []
    
    client = app.test_client()
    response = client.get('/authors')
    
    assert response.status_code == 404
    assert b"No authors found" in response.data

def test_get_authors(mock_db):
    mock_db.fetchall.return_value = [(1, 'John', 'Doe'), (2, 'Jane', 'Smith')]
    
    client = app.test_client()
    response = client.get('/authors')
    
    assert response.status_code == 200
    assert b"John" in response.data
    assert b"Doe" in response.data

def test_get_books_empty(mock_db):
    mock_db.fetchall.return_value = []
    
    client = app.test_client()
    response = client.get('/books')
    
    assert response.status_code == 404
    assert b"No books found" in response.data

def test_get_books(mock_db):
    mock_db.fetchall.return_value = [(1, 'Book Title', 1, '123456789', '2024-01-01')]
    
    client = app.test_client()
    response = client.get('/books')
    
    assert response.status_code == 200
    assert b"Book Title" in response.data

def test_add_author_missing_fields(mock_db):
    client = app.test_client()
    response = client.post('/authors', json={})
    
    assert response.status_code == 400
    assert b"Missing required fields: author_FirstName and author_LastName are mandatory" in response.data

def test_add_author_success(mock_db):
    client = app.test_client()
    mock_db.rowcount = 1
    response = client.post('/authors', json={
        'author_FirstName': 'John', 'author_LastName': 'Doe'
    })
    
    assert response.status_code == 201
    assert b"Author added successfully" in response.data

def test_update_author_missing_fields(mock_db):
    client = app.test_client()
    response = client.put('/authors/1', json={})
    
    assert response.status_code == 400
    assert b"At least one of 'author_FirstName' or 'author_LastName' must be provided" in response.data

def test_update_author_not_found(mock_db):
    mock_db.rowcount = 0
    
    client = app.test_client()
    response = client.put('/authors/999', json={'author_FirstName': 'Updated'})
    
    assert response.status_code == 404
    assert b"Author not found" in response.data

def test_delete_author_not_found(mock_db):
    mock_db.rowcount = 0
    
    client = app.test_client()
    response = client.delete('/authors/999')
    
    assert response.status_code == 404
    assert b"Author not found" in response.data

def test_delete_author_success(mock_db):
    mock_db.rowcount = 1
    
    client = app.test_client()
    response = client.delete('/authors/1')
    
    assert response.status_code == 200
    assert b"Author deleted successfully" in response.data

if __name__ == "__main__":
    pytest.main()
