import pytest
from api import app

@pytest.fixture
def mock_db(mocker):
    mock_conn = mocker.patch('flask_mysqldb.MySQL.connection')
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_cursor

# General Tests
def test_index():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    assert b"WELCOME TO BOOKSELLER DATABASE" in response.data

# Authors Table Tests
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

# Books Table Tests
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

def test_add_book_missing_fields(mock_db):
    client = app.test_client()
    response = client.post('/books', json={})
    
    assert response.status_code == 400
    assert b"Missing required fields: book_Title and ISBN are mandatory" in response.data

def test_add_book_success(mock_db):
    client = app.test_client()
    mock_db.rowcount = 1
    response = client.post('/books', json={
        'book_Title': 'New Book', 'author_ID': 1, 'ISBN': '987654321', 'publication_Date': '2024-01-01'
    })
    
    assert response.status_code == 201
    assert b"Book added successfully" in response.data

def test_update_book_missing_fields(mock_db):
    client = app.test_client()
    response = client.put('/books/1', json={})
    
    assert response.status_code == 400
    assert b"At least one of 'book_Title', 'ISBN', 'author_ID', or 'publication_Date' must be provided" in response.data

def test_update_book_not_found(mock_db):
    mock_db.rowcount = 0
    
    client = app.test_client()
    response = client.put('/books/999', json={'book_Title': 'Updated Title'})
    
    assert response.status_code == 404
    assert b"Book not found" in response.data

def test_delete_book_not_found(mock_db):
    mock_db.rowcount = 0
    
    client = app.test_client()
    response = client.delete('/books/999')
    
    assert response.status_code == 404
    assert b"Book not found" in response.data

def test_delete_book_success(mock_db):
    mock_db.rowcount = 1
    
    client = app.test_client()
    response = client.delete('/books/1')
    
    assert response.status_code == 200
    assert b"Book deleted successfully" in response.data

# Customers Table Tests
def test_get_customers_empty(mock_db):
    mock_db.fetchall.return_value = []
    
    client = app.test_client()
    response = client.get('/customers')
    
    assert response.status_code == 404
    assert b"No customers found" in response.data

def test_get_customers(mock_db):
    mock_db.fetchall.return_value = [(1, 'John Doe', '123-456-7890', 'john.doe@example.com')]
    
    client = app.test_client()
    response = client.get('/customers')
    
    assert response.status_code == 200
    assert b"John Doe" in response.data
    assert b"123-456-7890" in response.data
    assert b"john.doe@example.com" in response.data

def test_add_customer_missing_fields(mock_db):
    client = app.test_client()
    response = client.post('/customers', json={})
    
    assert response.status_code == 400
    assert b"Missing required fields: customer_Name and customer_Phone are mandatory" in response.data

def test_add_customer_success(mock_db):
    client = app.test_client()
    mock_db.rowcount = 1
    response = client.post('/customers', json={
        'customer_Name': 'John Doe', 'customer_Phone': '123-456-7890', 'customer_Email': 'john.doe@example.com'
    })
    
    assert response.status_code == 201
    assert b"Customer added successfully" in response.data

def test_update_customer_missing_fields(mock_db):
    client = app.test_client()
    response = client.put('/customers/1', json={})
    
    assert response.status_code == 400
    assert b"At least one of 'customer_Name', 'customer_Phone', or 'customer_Email' must be provided" in response.data

def test_update_customer_not_found(mock_db):
    mock_db.rowcount = 0
    
    client = app.test_client()
    response = client.put('/customers/999', json={'customer_Name': 'Updated'})
    
    assert response.status_code == 404
    assert b"Customer not found" in response.data

def test_delete_customer_not_found(mock_db):
    mock_db.rowcount = 0
    
    client = app.test_client()
    response = client.delete('/customers/999')
    
    assert response.status_code == 404
    assert b"Customer not found" in response.data

def test_delete_customer_success(mock_db):
    mock_db.rowcount = 1
    
    client = app.test_client()
    response = client.delete('/customers/1')
    
    assert response.status_code == 200
    assert b"Customer deleted successfully" in response.data

# Orders Table Tests
def test_get_orders_empty(mock_db):
    mock_db.fetchall.return_value = []
    
    client = app.test_client()
    response = client.get('/orders')
    
    assert response.status_code == 404
    assert b"No orders found" in response.data

def test_get_orders(mock_db):
    mock_db.fetchall.return_value = [(1, '2024-01-01', 100.00, 1, 1)]
    
    client = app.test_client()
    response = client.get('/orders')
    
    assert response.status_code == 200
    assert b"2024-01-01" in response.data
    assert b"100.0" in response.data
    assert b"1" in response.data

def test_add_order_missing_fields(mock_db):
    client = app.test_client()
    response = client.post('/orders', json={})
    
    assert response.status_code == 400
    assert b"Missing required fields: order_Date, order_Value, customer_ID, and book_ID are mandatory" in response.data

def test_add_order_success(mock_db):
    client = app.test_client()
    mock_db.rowcount = 1
    response = client.post('/orders', json={
        'order_Date': '2024-01-01', 'order_Value': 100.00, 'customer_ID': 1, 'book_ID': 1
    })
    
    assert response.status_code == 201
    assert b"Order added successfully" in response.data

def test_update_order_not_found(mock_db):
    mock_db.rowcount = 0
    
    client = app.test_client()
    response = client.put('/orders/999', json={'order_Value': '999.00'})
    
    assert response.status_code == 404
    assert b"Order not found" in response.data

def test_delete_order_not_found(mock_db):
    mock_db.rowcount = 0
    
    client = app.test_client()
    response = client.delete('/orders/999')
    
    assert response.status_code == 404
    assert b"Order not found" in response.data

def test_delete_order_success(mock_db):
    mock_db.rowcount = 1
    
    client = app.test_client()
    response = client.delete('/orders/1')
    
    assert response.status_code == 200
    assert b"Order deleted successfully" in response.data

if __name__ == "__main__":
    pytest.main()
