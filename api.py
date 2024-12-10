from flask import Flask, request, jsonify, abort
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "root"
app.config["MYSQL_DB"] = "booksellerdb"

mysql = MySQL(app)

# error handler
def handle_error(error_msg, status_code):
    return jsonify({"error": error_msg}), status_code

# index
@app.route("/")
def hello_world():
    return "WELCOME TO BOOKSELLER DATABASE"

# GET
@app.route("/authors")
def get_authors():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Authors")
    authors = cursor.fetchall()

    if not authors:
        return handle_error("No authors found", 404)

    authors_list = [
        {
            "author_ID": author[0], 
            "author_FirstName": author[1], 
            "author_LastName": author[2]
        }
        for author in authors
    ]
    
    return jsonify(authors_list), 200

@app.route("/books")
def get_books():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Books")
    books = cursor.fetchall()

    if not books:
        return handle_error("No books found", 404)

    books_list = [
        {
            "book_ID": book[0], 
            "book_Title": book[1], 
            "author_ID": book[2],
            "ISBN": book[3], 
            "publication_Date": book[4]
        }
        for book in books
    ]
    
    return jsonify(books_list), 200

@app.route("/customers")
def customers():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Customers")
    customers = cursor.fetchall()

    if not customers:
        return handle_error("No customers found", 404)

    customers_list = [
        {
            "customer_ID": customer[0],
            "customer_Name": customer[1],
            "customer_Phone": customer[2],
            "customer_Email": customer[3]
        }
        for customer in customers
    ]
    
    return jsonify(customers_list), 200

@app.route("/orders")
def get_orders():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Orders")
    orders = cursor.fetchall()

    if not orders:
        return handle_error("No orders found", 404)

    orders_list = [
        {
            "order_ID": order[0], 
            "order_Date": order[1], 
            "order_Value": order[2], 
            "customer_ID": order[3], 
            "book_ID": order[4], 
        }
        for order in orders
    ]
    
    return jsonify(orders_list), 200

# POST
@app.route("/authors", methods=["POST"])
def add_author():
    data = request.get_json()
    
    if not data or not data.get("author_FirstName") or not data.get("author_LastName"):
        return handle_error("Missing required fields: author_FirstName and author_LastName are mandatory", 400)
    
    author_FirstName = data["author_FirstName"]
    author_LastName = data["author_LastName"]

    try:
        cursor = mysql.connection.cursor()
        
        query = """
        INSERT INTO Authors (author_FirstName, author_LastName) 
        VALUES (%s, %s)
        """
        cursor.execute(query, (author_FirstName, author_LastName))
        mysql.connection.commit()
        
        return jsonify({"message": "Author added successfully"}), 201
    except Exception as e:
        return handle_error(f"An error occurred: {str(e)}", 500)

@app.route("/books", methods = ["POST"])
def add_book():
    data = request.get_json()
    
    if not data or not data.get("book_Title") or not data.get("ISBN"):
        return handle_error("Missing required fields: book_Title and ISBN are mandatory", 400)
    
    book_Title = data["book_Title"]
    author_ID = data["author_ID"]
    ISBN = data["ISBN"]
    publication_Date = data.get("publication_Date")

    try:
        cursor = mysql.connection.cursor()
        
        query = """
        INSERT INTO Books (book_Title, author_ID, ISBN, publication_Date) 
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (book_Title, author_ID, ISBN, publication_Date))
        mysql.connection.commit()
        
        return jsonify({"message": "Book added successfully"}), 201
    except Exception as e:
        return handle_error(f"An error occurred: {str(e)}", 500)
    
@app.route("/customers", methods = ["POST"])
def add_customer():
    data = request.get_json()
    
    if not data or not data.get("customer_Name") or not data.get("customer_Phone"):
        return handle_error("Missing required fields: customer_Name and customer_Phone are mandatory", 400)
    
    customer_Name = data["customer_Name"]
    customer_Phone = data["customer_Phone"]
    customer_Email = data["customer_Email"]

    try:
        cursor = mysql.connection.cursor()
        
        query = """
        INSERT INTO Customers (customer_Name, customer_Phone, customer_Email) 
        VALUES (%s, %s, %s)
        """
        cursor.execute(query, (customer_Name, customer_Phone, customer_Email))
        mysql.connection.commit()
        
        return jsonify({"message": "Customer added successfully"}), 201
    except Exception as e:
        return handle_error(f"An error occurred: {str(e)}", 500)
    
@app.route("/orders", methods = ["POST"])
def add_order():
    data = request.get_json()
    
    if not data or not data.get("order_Date") or not data.get("order_Value") or not data.get("customer_ID") or not data.get("book_ID"):
        return handle_error("Missing required fields: order_Date, order_Value, customer_ID, and book_ID are mandatory", 400)
    
    order_Date = data["order_Date"]
    order_Value = data["order_Value"]
    customer_ID = data["customer_ID"]
    book_ID = data["book_ID"]

    try:
        cursor = mysql.connection.cursor()
        
        query = """
        INSERT INTO Orders (order_Date, order_Value, customer_ID, book_ID) 
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (order_Date, order_Value, customer_ID, book_ID))
        mysql.connection.commit()
        
        return jsonify({"message": "Order added successfully"}), 201
    except Exception as e:
        return handle_error(f"An error occurred: {str(e)}", 500)

if __name__ == '__main__':
    app.run(debug=True)
