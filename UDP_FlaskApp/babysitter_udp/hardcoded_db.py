# hardcoded_db.py
import bcrypt



# Hardcoded user database for testing or simple user management
users = [
    {"id": 1, "username": "admin", "email": "admin@example.com", "password": bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'), "role": "admin"},
    {"id": 2, "username": "user1", "email": "user1@example.com", "password": bcrypt.hashpw("user123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'), "role": "user"},
    {"id": 3, "username": "user2", "email": "user2@example.com", "password": bcrypt.hashpw("user456".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'), "role": "user"}
]

# Function to verify user credentials (email and password)
def verify_user(email, password):
    for user in users:
        if user['email'] == email:
            # Check if the entered password matches the stored hashed password
            if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                return user
    return None  # Return None if no user matches the credentials

# Function to find a user by email (for signup)
def find_user_by_email(email):
    for user in users:
        if user['email'] == email:
            return user
    return None  # Return None if no user with the given email exists

# Function to add a new user with hashed password (for signup)
def add_user(username, email, password):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    new_user = {"id": len(users) + 1, "username": username, "email": email, "password": hashed_password, "role": "user"}
    users.append(new_user)
