from my_db import db, add_babysitter, get_babysitter_by_email, delete_all_users, validate_user, get_user_row_if_exists
import pymysql
pymysql.install_as_MySQLdb()
from flask import Flask
import bcrypt


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:14053yr@localhost/babysitter'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


with app.app_context():
    db.create_all()

def test_add_babysitter():
    user_name = input("Enter username for new babysitter: ")
    password = input("Enter password: ")
    name = input("Enter name: ")
    email = input("Enter email: ")
    add_babysitter(user_name, password, name, email)
    print("New babysitter added!")

def test_get_babysitter_by_email():
    email = input("Enter email to search for babysitter: ")
    babysitter = get_babysitter_by_email(email)
    if babysitter:
        print(f"Found babysitter: {babysitter.name}, {babysitter.email}")
    else:
        print("Babysitter not found.")

def test_validate_user():
    email = input("Enter email: ")
    password = input("Enter password: ")
    result = validate_user(email, password)
    print(result)

def test_delete_all_users():
    delete_all_users()
    print("All users deleted.")

def test_get_user_row_if_exists():
    user_id = int(input("Enter user ID: "))
    user_row = get_user_row_if_exists(user_id)
    if user_row:
        print(f"User found: {user_row.name}")
    else:
        print("User not found.")

def show_menu():
    with app.app_context():  
        while True:
            print("\n-----Menu Test -----")
            print("1. Add a new babysitter")
            print("2. find babysitter by email")
            print("3. Validate user login")
            print("4. Delete all users")
            print("5. Check user by ID")
            print("6. Exit")
            
            choice = input("Enter your choice: ")
            
            if choice == '1':
                test_add_babysitter()
            elif choice == '2':
                test_get_babysitter_by_email()
            elif choice == '3':
                test_validate_user()
            elif choice == '4':
                test_delete_all_users()
            elif choice == '5':
                test_get_user_row_if_exists()
            elif choice == '6':
                print("Exiting test menu...")
                break
            else:
                print("Invalid choice, please try again.")


if __name__ == "__main__":
    show_menu()
