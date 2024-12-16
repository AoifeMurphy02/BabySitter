# utils.py
from hardcoded_db import users

def find_user_by_email(email):
    return next((user for user in users if user['email'] == email), None)

def verify_user(email, password):
    user = find_user_by_email(email)
    return user if user and user['password'] == password else None

def is_admin(user):
    return user['role'] == 'admin'
