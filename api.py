from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import jwt, datetime, json

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "root"
app.config["MYSQL_DB"] = "booksellerdb"
app.config["SECRET_KEY"] = "ronald"

mysql = MySQL(app)

# error handler
def handle_error(error_msg, status_code):
    return jsonify({"error": error_msg}), status_code

# token validation
def validate_token():
    token = request.headers.get("x-access-token")

    if not token:
        return None, handle_error("Token is missing!", 401)

    try:
        data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        current_user = {"user_id": data["user_id"], "role": data["role"]}
        return current_user, None
    except Exception:
        return None, handle_error("Token is invalid!", 401)

# role validation
def validate_role(current_user, required_role):
    if current_user["role"] != required_role:
        return handle_error("Access forbidden: insufficient role", 403)
    return None

# users.json
users_data = {
    "users": []
}

def save_to_json():
    with open("users.json", "w") as f:
        json.dump(users_data, f)

def load_from_json():
    global users_data
    try:
        with open("users.json", "r") as f:
            users_data = json.load(f)
    except FileNotFoundError:
        save_to_json() 

# user registration
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data or not data.get("username") or not data.get("password") or not data.get("role"):
        return handle_error("Missing required fields: username, password, and role are mandatory", 400)

    username = data["username"]
    password = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
    role = data["role"]

    load_from_json()

    for user in users_data["users"]:
        if user["username"] == username:
            return handle_error("Username already exists", 400)

    new_user = {"username": username, "password": password, "role": role}
    users_data["users"].append(new_user)
    save_to_json()

    return jsonify({"message": "User registered successfully"}), 201

# user login
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or not data.get("username") or not data.get("password"):
        return handle_error("Missing required fields: username and password are mandatory", 400)

    username = data["username"]
    password = data["password"]

    load_from_json()

    for user in users_data["users"]:
        if user["username"] == username and bcrypt.check_password_hash(user["password"], password):
            token = jwt.encode(
                {
                    "user_id": username,
                    "role": user["role"],
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
                },
                app.config["SECRET_KEY"],
                algorithm="HS256",
            )
            return jsonify({"token": token}), 200

    return handle_error("Invalid credentials", 401)

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
    current_user, error = validate_token()
    if error:
        return error

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
    current_user, error = validate_token()
    if error:
        return error

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
    current_user, error = validate_token()
    if error:
        return error

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
    current_user, error = validate_token()
    if error:
        return error

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
    
# PUT
@app.route("/authors/<int:author_id>", methods=["PUT"])
def update_author(author_id):
    current_user, error = validate_token()
    if error:
        return error

    data = request.get_json()

    if not data or (not data.get("author_FirstName") and not data.get("author_LastName")):
        return handle_error("At least one of 'author_FirstName' or 'author_LastName' must be provided", 400)

    author_FirstName = data.get("author_FirstName")
    author_LastName = data.get("author_LastName")

    try:
        cursor = mysql.connection.cursor()

        query = """
        UPDATE Authors 
        SET author_FirstName = %s, author_LastName = %s 
        WHERE author_ID = %s
        """
        
        cursor.execute(query, (author_FirstName if author_FirstName else "", 
                               author_LastName if author_LastName else "", 
                               author_id))
        mysql.connection.commit()
        
        if cursor.rowcount == 0:
            return handle_error("Author not found", 404)

        return jsonify({"message": "Author updated successfully"}), 200
    except Exception as e:
        return handle_error(f"An error occurred: {str(e)}", 500)
    
@app.route("/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    current_user, error = validate_token()
    if error:
        return error

    data = request.get_json()

    if not data or (not data.get("book_Title") and not data.get("ISBN") and not data.get("author_ID") and not data.get("publication_Date")):
        return handle_error("At least one of 'book_Title', 'ISBN', 'author_ID', or 'publication_Date' must be provided", 400)

    book_Title = data.get("book_Title")
    author_ID = data.get("author_ID")
    ISBN = data.get("ISBN")
    publication_Date = data.get("publication_Date")

    try:
        cursor = mysql.connection.cursor()

        query = """
        UPDATE Books
        SET book_Title = %s, author_ID = %s, ISBN = %s, publication_Date = %s
        WHERE book_ID = %s
        """
        
        cursor.execute(query, (book_Title if book_Title else "", 
                               author_ID if author_ID else "", 
                               ISBN if ISBN else "", 
                               publication_Date if publication_Date else "", 
                               book_id))
        mysql.connection.commit()
        
        if cursor.rowcount == 0:
            return handle_error("Book not found", 404)

        return jsonify({"message": "Book updated successfully"}), 200
    except Exception as e:
        return handle_error(f"An error occurred: {str(e)}", 500)
    
@app.route("/customers/<int:customer_id>", methods=["PUT"])
def update_customer(customer_id):
    current_user, error = validate_token()
    if error:
        return error

    data = request.get_json()

    if not data or (not data.get("customer_Name") and not data.get("customer_Phone") and not data.get("customer_Email")):
        return handle_error("At least one of 'customer_Name', 'customer_Phone', or 'customer_Email' must be provided", 400)

    customer_Name = data.get("customer_Name")
    customer_Phone = data.get("customer_Phone")
    customer_Email = data.get("customer_Email")

    try:
        cursor = mysql.connection.cursor()

        query = """
        UPDATE Customers
        SET customer_Name = %s, customer_Phone = %s, customer_Email = %s
        WHERE customer_ID = %s
        """
        
        cursor.execute(query, (customer_Name if customer_Name else "", 
                               customer_Phone if customer_Phone else "", 
                               customer_Email if customer_Email else "", 
                               customer_id))
        mysql.connection.commit()
        
        if cursor.rowcount == 0:
            return handle_error("Customer not found", 404)

        return jsonify({"message": "Customer updated successfully"}), 200
    except Exception as e:
        return handle_error(f"An error occurred: {str(e)}", 500)

@app.route("/orders/<int:order_id>", methods=["PUT"])
def update_order(order_id):
    current_user, error = validate_token()
    if error:
        return error

    data = request.get_json()

    if not data or (not data.get("order_Date") and not data.get("order_Value") and not data.get("customer_ID") and not data.get("book_ID")):
        return handle_error("At least one of 'order_Date', 'order_Value', 'customer_ID', or 'book_ID' must be provided", 400)

    order_Date = data.get("order_Date")
    order_Value = data.get("order_Value")
    customer_ID = data.get("customer_ID")
    book_ID = data.get("book_ID")

    try:
        cursor = mysql.connection.cursor()

        query = """
        UPDATE Orders
        SET order_Date = %s, order_Value = %s, customer_ID = %s, book_ID = %s
        WHERE order_ID = %s
        """
        
        cursor.execute(query, (order_Date if order_Date else "", 
                               order_Value if order_Value else "", 
                               customer_ID if customer_ID else "", 
                               book_ID if book_ID else "", 
                               order_id))
        mysql.connection.commit()
        
        if cursor.rowcount == 0:
            return handle_error("Order not found", 404)

        return jsonify({"message": "Order updated successfully"}), 200
    except Exception as e:
        return handle_error(f"An error occurred: {str(e)}", 500)
    
# DELETE
@app.route("/authors/<int:author_id>", methods=["DELETE"])
def delete_author(author_id):
    current_user, error = validate_token()
    if error:
        return error

    try:
        cursor = mysql.connection.cursor()

        update_books_query = "UPDATE Books SET author_ID = NULL WHERE author_ID = %s"
        cursor.execute(update_books_query, (author_id,))
        mysql.connection.commit()

        delete_author_query = "DELETE FROM Authors WHERE author_ID = %s"
        cursor.execute(delete_author_query, (author_id,))
        mysql.connection.commit()

        if cursor.rowcount == 0:
            return handle_error("Author not found", 404)

        return jsonify({"message": "Author deleted successfully"}), 200
    except Exception as e:
        return handle_error(f"An error occurred: {str(e)}", 500)
    
@app.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    current_user, error = validate_token()
    if error:
        return error

    try:
        cursor = mysql.connection.cursor()

        update_orders_query = "UPDATE Orders SET book_ID = NULL WHERE book_ID = %s"
        cursor.execute(update_orders_query, (book_id,))
        mysql.connection.commit()

        delete_book_query = "DELETE FROM Books WHERE book_ID = %s"
        cursor.execute(delete_book_query, (book_id,))
        mysql.connection.commit()

        if cursor.rowcount == 0:
            return handle_error("Book not found", 404)

        return jsonify({"message": "Book deleted successfully"}), 200
    except Exception as e:
        return handle_error(f"An error occurred: {str(e)}", 500)
    
@app.route("/customers/<int:customer_id>", methods=["DELETE"])
def delete_customer(customer_id):
    current_user, error = validate_token()
    if error:
        return error

    try:
        cursor = mysql.connection.cursor()

        update_orders_query = "UPDATE Orders SET customer_ID = NULL WHERE customer_ID = %s"
        cursor.execute(update_orders_query, (customer_id,))
        mysql.connection.commit()

        delete_customer_query = "DELETE FROM Customers WHERE customer_ID = %s"
        cursor.execute(delete_customer_query, (customer_id,))
        mysql.connection.commit()

        if cursor.rowcount == 0:
            return handle_error("Customer not found", 404)

        return jsonify({"message": "Customer deleted successfully"}), 200
    except Exception as e:
        return handle_error(f"An error occurred: {str(e)}", 500)

@app.route("/orders/<int:order_id>", methods=["DELETE"])
def delete_order(order_id):
    current_user, error = validate_token()
    if error:
        return error

    try:
        cursor = mysql.connection.cursor()

        delete_order_query = "DELETE FROM Orders WHERE order_ID = %s"
        cursor.execute(delete_order_query, (order_id,))
        mysql.connection.commit()

        if cursor.rowcount == 0:
            return handle_error("Order not found", 404)

        return jsonify({"message": "Order deleted successfully"}), 200
    except Exception as e:
        return handle_error(f"An error occurred: {str(e)}", 500)

if __name__ == '__main__':
    app.run(debug=True)
