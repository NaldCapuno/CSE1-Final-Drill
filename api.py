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
            "ISBN": book[2], 
            "publication_Date": book[3]
        }
        for book in books
    ]
    
    return jsonify(books_list), 200

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

if __name__ == '__main__':
    app.run(debug=True)
