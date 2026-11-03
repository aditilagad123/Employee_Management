import mysql.connector

# DATABASE CONNECTION

db = mysql.connector.connect(
   host="localhost",
       user="root",
       password="Aditi@123",
       database="employee_db"
)

cur = db.cursor()


# ADMIN ACCOUNT

cur.execute("SELECT * FROM registration WHERE username='admin'")

if cur.fetchone() is None:
    cur.execute(
        "INSERT INTO registration(username,password,role) VALUES(%s,%s,%s)",
        ("admin", "admin123", "admin")
    )
    db.commit()


# USER REGISTRATION

def register():

    username = input("Enter Username: ")
    password = input("Enter Password: ")

    try:
        cur.execute(
            "INSERT INTO registration(username,password,role) VALUES(%s,%s,%s)",
            (username, password, "user")
        )

        user_id = cur.lastrowid

        name = input("Enter Employee Name: ")
        email = input("Enter Email: ")
        salary = float(input("Enter Salary: "))

        cur.execute("SELECT * FROM department")
        departments = cur.fetchall()

        print("\nDepartments:")
        for d in departments:
            print(d[0], d[1])

        dept_id = int(input("Enter Department ID: "))

        cur.execute("""
            INSERT INTO employee(user_id,emp_name,email,salary,dept_id)
            VALUES(%s,%s,%s,%s,%s)
        """, (user_id, name, email, salary, dept_id))

        db.commit()

        print("Registration Successful!")

    except mysql.connector.Error as e:
        db.rollback()
        print("Error:", e)


# ADMIN LOGIN

def admin_login():

    username = input("Enter Admin Username: ")
    password = input("Enter Admin Password: ")

    cur.execute(
        "SELECT * FROM registration WHERE username=%s AND password=%s AND role='admin'",
        (username, password)
    )

    if cur.fetchone():
        print("\nAdmin Login Successful!")
        admin_menu()
    else:
        print("Invalid Admin Login!")


# USER LOGIN

def user_login():

    username = input("Enter Username: ")
    password = input("Enter Password: ")

    cur.execute(
        "SELECT * FROM registration WHERE username=%s AND password=%s AND role='user'",
        (username, password)
    )

    user = cur.fetchone()

    if user:
        print("\nUser Login Successful!")
        user_menu(user[0])
    else:
        print("Invalid Login!")


# ADD EMPLOYEE

def add_employee():

    name = input("Enter Name: ")
    email = input("Enter Email: ")
    salary = float(input("Enter Salary: "))

    cur.execute("SELECT * FROM department")
    departments = cur.fetchall()

    for d in departments:
        print(d[0], d[1])

    dept_id = int(input("Enter Department ID: "))

    username = input("Enter Username: ")
    password = input("Enter Password: ")

    try:
        cur.execute(
            "INSERT INTO registration(username,password,role) VALUES(%s,%s,'user')",
            (username, password)
        )

        user_id = cur.lastrowid

        cur.execute("""
            INSERT INTO employee(user_id,emp_name,email,salary,dept_id)
            VALUES(%s,%s,%s,%s,%s)
        """, (user_id, name, email, salary, dept_id))

        db.commit()
        print("Employee Added Successfully!")

    except mysql.connector.Error as e:
        db.rollback()
        print("Error:", e)


# VIEW EMPLOYEES

def view_employee():

    cur.execute("""
        SELECT e.emp_id,e.emp_name,e.email,e.salary,d.dept_name
        FROM employee e
        JOIN department d ON e.dept_id=d.dept_id
    """)

    for e in cur.fetchall():
        print(e)


# UPDATE EMPLOYEE

def update_employee():

    emp_id = int(input("Enter Employee ID: "))

    name = input("Enter New Name: ")
    email = input("Enter New Email: ")
    salary = float(input("Enter New Salary: "))

    cur.execute("""
        UPDATE employee
        SET emp_name=%s,email=%s,salary=%s
        WHERE emp_id=%s
    """, (name, email, salary, emp_id))

    db.commit()

    if cur.rowcount > 0:
        print("Employee Updated Successfully!")
    else:
        print("Employee Not Found!")


# DELETE EMPLOYEE

def delete_employee():

    emp_id = int(input("Enter Employee ID: "))

    cur.execute(
        "SELECT user_id FROM employee WHERE emp_id=%s",
        (emp_id,)
    )

    result = cur.fetchone()

    if result:

        cur.execute("DELETE FROM attendance WHERE emp_id=%s", (emp_id,))
        cur.execute("DELETE FROM employee WHERE emp_id=%s", (emp_id,))
        cur.execute("DELETE FROM registration WHERE id=%s", (result[0],))

        db.commit()

        print("Employee Deleted Successfully!")

    else:
        print("Employee Not Found!")


# ADMIN MENU

def admin_menu():

    while True:

        print("\n===== ADMIN MENU =====")
        print("1. Add Employee")
        print("2. View Employees")
        print("3. Update Employee")
        print("4. Delete Employee")
        print("5. Logout")

        choice = input("Enter Choice: ")

        if choice == "1":
            add_employee()

        elif choice == "2":
            view_employee()

        elif choice == "3":
            update_employee()

        elif choice == "4":
            delete_employee()

        elif choice == "5":
            break

        else:
            print("Invalid Choice!")


# USER MENU

def user_menu(user_id):

    while True:

        print("\n===== USER MENU =====")
        print("1. View My Profile")
        print("2. Update My Profile")
        print("3. View My Attendance")
        print("4. Logout")

        choice = input("Enter Choice: ")

        if choice == "1":

            cur.execute(
                "SELECT emp_id,emp_name,email,salary FROM employee WHERE user_id=%s",
                (user_id,)
            )

            print(cur.fetchone())

        elif choice == "2":

            name = input("Enter New Name: ")
            email = input("Enter New Email: ")

            cur.execute("""
                UPDATE employee
                SET emp_name=%s,email=%s
                WHERE user_id=%s
            """, (name, email, user_id))

            db.commit()
            print("Profile Updated!")

        elif choice == "3":

            cur.execute("""
                SELECT a.att_date,a.status
                FROM attendance a
                JOIN employee e ON a.emp_id=e.emp_id
                WHERE e.user_id=%s
            """, (user_id,))

            records = cur.fetchall()

            for r in records:
                print(r)

        elif choice == "4":
            break

        else:
            print("Invalid Choice!")


# MAIN MENU

while True:

    print("\n===== EMPLOYEE MANAGEMENT SYSTEM =====")
    print("1. Admin Login")
    print("2. User Registration")
    print("3. User Login")
    print("4. Exit")

    choice = input("Enter Choice: ")

    if choice == "1":
        admin_login()

    elif choice == "2":
        register()

    elif choice == "3":
        user_login()

    elif choice == "4":
        print("Thank You!")
        break

    else:
        print("Invalid Choice!")

cur.close()
db.close()



#mysql 

# CREATE DATABASE employee_db;

# USE employee_db;

# CREATE TABLE registration (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     username VARCHAR(50) UNIQUE,
#     password VARCHAR(100),
#     role VARCHAR(20)
# );

# CREATE TABLE department (
#     dept_id INT AUTO_INCREMENT PRIMARY KEY,
#     dept_name VARCHAR(50)attendance
# );

# CREATE TABLE employee (
#     emp_id INT AUTO_INCREMENT PRIMARY KEY,
#     user_id INT UNIQUE,
#     emp_name VARCHAR(50),
#     email VARCHAR(100),
#     salary FLOAT,
#     dept_id INT,
#     FOREIGN KEY(user_id) REFERENCES registration(id),
#     FOREIGN KEY(dept_id) REFERENCES department(dept_id)
# );

# CREATE TABLE attendance (
#     att_id INT AUTO_INCREMENT PRIMARY KEY,
#     emp_id INT,
#     att_date DATE,
#     status VARCHAR(20),
#     FOREIGN KEY(emp_id) REFERENCES employee(emp_id)
# );

# INSERT INTO department(dept_name)
# VALUES ('IT'), ('HR'), ('Finance'), ('Marketing');

# SHOW FULL PROCESSLIST;
# SELECT * FROM information_schema.innodb_trx;

# SHOW DATABASES;

# USE employee_db;

# SHOW TABLES;

# SELECT * FROM registration;

# SELECT * FROM employee;
