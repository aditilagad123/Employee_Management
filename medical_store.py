
import mysql.connector
from mysql.connector import Error
from datetime import date

# DATABASE CONNECTION
try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Aditi@123",
        database="medicine_store"
    )

    cur = db.cursor()
    print("Database Connected Successfully!")

except Error as e:
    print("Database Connection Error:", e)
    exit()


# CREATE DEFAULT ADMIN
cur.execute("SELECT * FROM users WHERE username=%s", ("admin",))
admin = cur.fetchone()

if admin is None:
    cur.execute(
        "INSERT INTO users(username,password,role) VALUES(%s,%s,%s)",
        ("admin", "admin123", "admin")
    )
    db.commit()


# CUSTOMER REGISTRATION
def registration():
    print("\n===== CUSTOMER REGISTRATION =====")

    username = input("Enter Username: ")
    password = input("Enter Password: ")

    try:
        cur.execute(
            "INSERT INTO users(username,password,role) VALUES(%s,%s,%s)",
            (username, password, "customer")
        )
        db.commit()
        print("Registration Successful!")

    except Error as e:
        db.rollback()
        print("Registration Error:", e)


# ADMIN LOGIN
def admin_login():
    print("\n===== ADMIN LOGIN =====")

    username = input("Enter Username: ")
    password = input("Enter Password: ")

    cur.execute(
        "SELECT * FROM users WHERE username=%s AND password=%s AND role=%s",
        (username, password, "admin")
    )

    user = cur.fetchone()

    if user:
        print("Admin Login Successful!")
        admin_menu()
    else:
        print("Invalid Admin Username or Password!")


# CUSTOMER LOGIN
def customer_login():
    print("\n===== CUSTOMER LOGIN =====")

    username = input("Enter Username: ")
    password = input("Enter Password: ")

    cur.execute(
        "SELECT * FROM users WHERE username=%s AND password=%s AND role=%s",
        (username, password, "customer")
    )

    user = cur.fetchone()

    if user:
        print("Customer Login Successful!")
        customer_menu(user[0])
    else:
        print("Invalid Username or Password!")


# ADD MEDICINE
def add_medicine():
    print("\n===== ADD MEDICINE =====")

    name = input("Enter Medicine Name: ")
    category = input("Enter Category: ")
    price = float(input("Enter Price: "))
    quantity = int(input("Enter Quantity: "))
    expiry = input("Enter Expiry Date (YYYY-MM-DD): ")

    if price <= 0 or quantity < 0:
        print("Invalid price or quantity!")
        return

    try:
        expiry_date = date.fromisoformat(expiry)

        if expiry_date <= date.today():
            print("Expired or invalid medicine expiry date!")
            return

        cur.execute(
            """INSERT INTO medicines
            (medicine_name,category,price,quantity,expiry_date)
            VALUES(%s,%s,%s,%s,%s)""",
            (name, category, price, quantity, expiry_date)
        )

        db.commit()
        print("Medicine Added Successfully!")

    except ValueError:
        print("Invalid Date or Number!")
    except Error as e:
        db.rollback()
        print("Error:", e)


# VIEW MEDICINES
def view_medicines():
    print("\n===== AVAILABLE MEDICINES =====")

    cur.execute(
        """SELECT * FROM medicines
        WHERE quantity > 0 AND expiry_date > CURDATE()"""
    )

    records = cur.fetchall()

    if not records:
        print("No medicines available!")
        return

    for medicine in records:
        print("\nMedicine ID:", medicine[0])
        print("Name:", medicine[1])
        print("Category:", medicine[2])
        print("Price:", medicine[3])
        print("Quantity:", medicine[4])
        print("Expiry Date:", medicine[5])


# UPDATE MEDICINE
def update_medicine():
    print("\n===== UPDATE MEDICINE =====")

    medicine_id = int(input("Enter Medicine ID: "))

    cur.execute(
        "SELECT * FROM medicines WHERE medicine_id=%s",
        (medicine_id,)
    )

    medicine = cur.fetchone()

    if medicine is None:
        print("Medicine Not Found!")
        return

    name = input("Enter New Medicine Name: ")
    category = input("Enter New Category: ")
    price = float(input("Enter New Price: "))
    quantity = int(input("Enter New Quantity: "))
    expiry = input("Enter New Expiry Date (YYYY-MM-DD): ")

    try:
        expiry_date = date.fromisoformat(expiry)

        if price <= 0 or quantity < 0 or expiry_date <= date.today():
            print("Invalid price, quantity or expiry date!")
            return

        cur.execute(
            """UPDATE medicines
            SET medicine_name=%s, category=%s, price=%s,
            quantity=%s, expiry_date=%s
            WHERE medicine_id=%s""",
            (name, category, price, quantity, expiry_date, medicine_id)
        )

        db.commit()
        print("Medicine Updated Successfully!")

    except ValueError:
        print("Invalid Date or Number!")
    except Error as e:
        db.rollback()
        print("Error:", e)


# DELETE MEDICINE
def delete_medicine():
    print("\n===== DELETE MEDICINE =====")

    medicine_id = int(input("Enter Medicine ID: "))

    cur.execute(
        "SELECT * FROM medicines WHERE medicine_id=%s",
        (medicine_id,)
    )

    if cur.fetchone() is None:
        print("Medicine Not Found!")
        return

    try:
        cur.execute(
            "DELETE FROM medicines WHERE medicine_id=%s",
            (medicine_id,)
        )
        db.commit()
        print("Medicine Deleted Successfully!")

    except Error as e:
        db.rollback()
        print("Cannot Delete Medicine:", e)


# SEARCH MEDICINE
def search_medicine():
    print("\n===== SEARCH MEDICINE =====")

    name = input("Enter Medicine Name: ")

    cur.execute(
        """SELECT * FROM medicines
        WHERE medicine_name LIKE %s
        AND quantity > 0 AND expiry_date > CURDATE()""",
        ("%" + name + "%",)
    )

    records = cur.fetchall()

    if not records:
        print("Medicine Not Found!")
    else:
        for medicine in records:
            print(medicine)


# ADD TO CART
def add_to_cart(user_id, cart):
    print("\n===== ADD TO CART =====")

    view_medicines()

    try:
        medicine_id = int(input("\nEnter Medicine ID: "))
        quantity = int(input("Enter Quantity: "))

        if quantity <= 0:
            print("Quantity must be greater than zero!")
            return

        cur.execute(
            """SELECT medicine_name, price, quantity, expiry_date
            FROM medicines WHERE medicine_id=%s""",
            (medicine_id,)
        )

        medicine = cur.fetchone()

        if medicine is None:
            print("Medicine Not Found!")
            return

        if medicine[2] < quantity or medicine[3] <= date.today():
            print("Insufficient stock or medicine expired!")
            return

        if medicine_id in cart:
            new_quantity = cart[medicine_id][1] + quantity
        else:
            new_quantity = quantity

        if new_quantity > medicine[2]:
            print("Requested quantity exceeds available stock!")
            return

        cart[medicine_id] = (medicine[0], new_quantity, float(medicine[1]))
        print("Medicine Added to Cart!")

    except ValueError:
        print("Please enter valid numbers!")


# VIEW CART
def view_cart(cart):
    print("\n===== YOUR CART =====")

    if not cart:
        print("Your Cart Is Empty!")
        return

    total = 0

    for medicine_id, item in cart.items():
        name, quantity, price = item
        amount = quantity * price
        total += amount

        print("Medicine:", name)
        print("Quantity:", quantity)
        print("Price:", price)
        print("Amount:", amount)
        print("--------------------")

    print("Total Amount:", total)


# PLACE ORDER
def place_order(user_id, cart):
    print("\n===== PLACE ORDER =====")

    if not cart:
        print("Your Cart Is Empty!")
        return

    try:
        total = 0

        # Check current stock before ordering
        for medicine_id, item in cart.items():
            name, quantity, price = item

            cur.execute(
                """SELECT quantity, price, expiry_date
                FROM medicines
                WHERE medicine_id=%s FOR UPDATE""",
                (medicine_id,)
            )

            medicine = cur.fetchone()

            if (medicine is None or medicine[0] < quantity
                    or medicine[2] <= date.today()):
                db.rollback()
                print("Stock changed or medicine expired:", name)
                return

            total += quantity * float(medicine[1])

        # Create order
        cur.execute(
            """INSERT INTO orders
            (user_id, order_date, total_amount, status)
            VALUES(%s, CURDATE(), %s, %s)""",
            (user_id, total, "Pending")
        )

        order_id = cur.lastrowid

        # Save order items and reduce stock
        for medicine_id, item in cart.items():
            name, quantity, price = item

            cur.execute(
                """SELECT price FROM medicines
                WHERE medicine_id=%s""",
                (medicine_id,)
            )
            actual_price = float(cur.fetchone()[0])

            cur.execute(
                """INSERT INTO order_items
                (order_id, medicine_id, quantity, price)
                VALUES(%s, %s, %s, %s)""",
                (order_id, medicine_id, quantity, actual_price)
            )

            cur.execute(
                """UPDATE medicines
                SET quantity = quantity - %s
                WHERE medicine_id=%s""",
                (quantity, medicine_id)
            )

        db.commit()
        cart.clear()

        print("Order Placed Successfully!")
        print("Your Order ID:", order_id)
        print("Total Amount:", total)
        print("Order Status: Pending")

    except Error as e:
        db.rollback()
        print("Order Error:", e)


# CUSTOMER ORDER HISTORY
def my_orders(user_id):
    print("\n===== MY ORDERS =====")

    cur.execute(
        """SELECT order_id, order_date, total_amount, status
        FROM orders WHERE user_id=%s ORDER BY order_id DESC""",
        (user_id,)
    )

    records = cur.fetchall()

    if not records:
        print("No Orders Found!")
        return

    for order in records:
        print("\nOrder ID:", order[0])
        print("Order Date:", order[1])
        print("Total Amount:", order[2])
        print("Status:", order[3])


# ADMIN VIEW ORDERS
def view_orders():
    print("\n===== ALL CUSTOMER ORDERS =====")

    cur.execute(
        """SELECT o.order_id, u.username, o.order_date,
        o.total_amount, o.status
        FROM orders o
        JOIN users u ON o.user_id=u.user_id
        ORDER BY o.order_id DESC"""
    )

    records = cur.fetchall()

    if not records:
        print("No Orders Found!")
        return

    for order in records:
        print("\nOrder ID:", order[0])
        print("Customer:", order[1])
        print("Date:", order[2])
        print("Amount:", order[3])
        print("Status:", order[4])


# UPDATE ORDER STATUS
def update_order_status():
    print("\n===== UPDATE ORDER STATUS =====")

    try:
        order_id = int(input("Enter Order ID: "))

        cur.execute(
            "SELECT * FROM orders WHERE order_id=%s",
            (order_id,)
        )

        if cur.fetchone() is None:
            print("Order Not Found!")
            return

        print("1. Pending")
        print("2. Confirmed")
        print("3. Shipped")
        print("4. Delivered")
        print("5. Cancelled")

        choice = input("Enter Choice: ")

        status_list = {
            "1": "Pending",
            "2": "Confirmed",
            "3": "Shipped",
            "4": "Delivered",
            "5": "Cancelled"
        }

        if choice not in status_list:
            print("Invalid Choice!")
            return

        cur.execute(
            "UPDATE orders SET status=%s WHERE order_id=%s",
            (status_list[choice], order_id)
        )

        db.commit()
        print("Order Status Updated!")

    except ValueError:
        print("Enter a valid Order ID!")
    except Error as e:
        db.rollback()
        print("Error:", e)


# ADMIN MENU
def admin_menu():
    while True:
        print("\n===== ADMIN PANEL =====")
        print("1. Add Medicine")
        print("2. View All Medicines")
        print("3. Update Medicine")
        print("4. Delete Medicine")
        print("5. View Customer Orders")
        print("6. Update Order Status")
        print("7. Logout")

        choice = input("Enter Choice: ")

        if choice == "1":
            add_medicine()
        elif choice == "2":
            view_medicines()
        elif choice == "3":
            update_medicine()
        elif choice == "4":
            delete_medicine()
        elif choice == "5":
            view_orders()
        elif choice == "6":
            update_order_status()
        elif choice == "7":
            print("Admin Logged Out!")
            break
        else:
            print("Invalid Choice!")


# CUSTOMER MENU
def customer_menu(user_id):
    cart = {}

    while True:
        print("\n===== CUSTOMER PANEL =====")
        print("1. View All Medicines")
        print("2. Search Medicine")
        print("3. Add to Cart")
        print("4. View Cart")
        print("5. Place Order")
        print("6. View My Orders")
        print("7. Logout")

        choice = input("Enter Choice: ")

        if choice == "1":
            view_medicines()
        elif choice == "2":
            search_medicine()
        elif choice == "3":
            add_to_cart(user_id, cart)
        elif choice == "4":
            view_cart(cart)
        elif choice == "5":
            place_order(user_id, cart)
        elif choice == "6":
            my_orders(user_id)
        elif choice == "7":
            print("Customer Logged Out!")
            break
        else:
            print("Invalid Choice!")


# MAIN MENU
while True:
    print("\n===== ONLINE MEDICINE STORE =====")
    print("1. Admin Login")
    print("2. Customer Registration")
    print("3. Customer Login")
    print("4. Exit")

    choice = input("Enter Choice: ")

    if choice == "1":
        admin_login()
    elif choice == "2":
        registration()
    elif choice == "3":
        customer_login()
    elif choice == "4":
        print("Thank You!")
        break
    else:
        print("Invalid Choice!")


# CLOSE DATABASE
cur.close()
db.close()
print("Database Connection Closed!")



#   mysql workbench


# CREATE DATABASE medicine_store;

# USE medicine_store;

# -- Customer and Admin Login
# CREATE TABLE users (
#     user_id INT AUTO_INCREMENT PRIMARY KEY,
#     username VARCHAR(50) UNIQUE,
#     password VARCHAR(100),
#     role VARCHAR(20)
# );

# -- Medicine Details
# CREATE TABLE medicines (
#     medicine_id INT AUTO_INCREMENT PRIMARY KEY,
#     medicine_name VARCHAR(100),
#     category VARCHAR(50),
#     price FLOAT,
#     quantity INT,
#     expiry_date DATE
# );

# -- Customer Orders
# CREATE TABLE orders (
#     order_id INT AUTO_INCREMENT PRIMARY KEY,
#     user_id INT,
#     order_date DATE,
#     total_amount FLOAT,
#     status VARCHAR(30),
#     FOREIGN KEY (user_id) REFERENCES users(user_id)
# );

# -- Order Items
# CREATE TABLE order_items (
#     item_id INT AUTO_INCREMENT PRIMARY KEY,
#     order_id INT,
#     medicine_id INT,
#     quantity INT,
#     price FLOAT,
#     FOREIGN KEY (order_id) REFERENCES orders(order_id),
#     FOREIGN KEY (medicine_id) REFERENCES medicines(medicine_id)
# );

# -- Sample Medicines
# INSERT INTO medicines
# (medicine_name, category, price, quantity, expiry_date)
# VALUES
# ('Paracetamol', 'Tablet', 20, 100, '2027-12-31'),
# ('Cetirizine', 'Tablet', 30, 50, '2027-10-31'),
# ('Vitamin C', 'Supplement', 80, 40, '2027-11-30'),
# ('Antacid', 'Syrup', 90, 30, '2027-09-30');

# SELECT * FROM users;
# SELECT * FROM medicines;
# SELECT * FROM orders;
# SELECT * FROM order_items;
