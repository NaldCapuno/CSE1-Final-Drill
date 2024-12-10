# Bookseller Database API

## Description
A Flask-based REST API for managing authors, books, customers, and orders in a bookseller database.

## Installation
```bash
pip install -r requirements.txt
```

## Configuration
To configure the database:
1. Upload the ```booksellerdb``` MySQL database to your server or local machine.
2. Update the database configuration in the Flask app with your database connection details.

Environment variables needed:
- ```MYSQL_HOST```: The host for the MySQL database (e.g., localhost or IP address of the database server)
- ```MYSQL_USER```: MySQL username (e.g., root)
- ```MYSQL_PASSWORD```: MySQL password
- ```MYSQL_DB```: Name of the database (e.g., booksellerdb)

## API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| /	| GET	| Welcome message |
| /authors	| GET	| List all authors |
| /authors	| POST	| Add a new author |
| /authors/<author_id>	| PUT	| Update an author's details |
| /authors/<author_id>	| DELETE	| Delete an author |
| /books	| GET	| List all books |
| /books	| POST	| Add a new book |
| /books/<book_id>	| PUT	| Update a book's details |
| /books/<book_id>	| DELETE	| Delete a book |
| /customers	| GET	| List all customers |
| /customers	| POST	| Add a new customer |
| /customers/<customer_id>	| PUT	| Update a customer's details |
| /customers/<customer_id>	| DELETE	| Delete a customer |
| /orders	| GET	| List all orders |
| /orders	| POST	| Add a new order |
| /orders/<order_id>	| PUT	| Update an order's details |
| /orders/<order_id>	| DELETE	| Delete an order |

## Git Commit Guidelines
Use conventional commits:
```bash
feat: add user authentication
fix: resolve database connection issue
docs: update API documentation
test: add user registration tests
```
