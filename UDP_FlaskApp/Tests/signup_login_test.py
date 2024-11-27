import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../babysitter_udp')))

from app import app, db, my_db
from my_db import BabySitterLogin,setup_database



@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            setup_database() 
        yield client
        with app.app_context():
            db.session.remove()

def test_signup_page_loads(client):
    response = client.get('/signup', content_type='html/text')
    assert response.status_code == 200
    assert b'Sign Up' in response.data

def test_valid_signup(client):
    response = client.post('/signup', data=dict(username="testuser", password="Password1", name="John Doe", email="john.doe@example.com"), follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        user = my_db.get_babysitter_by_email("john.doe@example.com")
        assert user is not None
        assert user.user_name == "testuser"

def test_duplicate_signup(client):
    response = client.post('/signup', data=dict(username="testuser2", password="Testpass123", name="John Doe", email="john.doe@example.com"), follow_redirects=True)
    assert response.status_code == 200
    assert b"Email already registered. Please choose a different email." in response.data

    with app.app_context():
        users = BabySitterLogin.query.filter_by(email="john.doe@example.com").all()
        assert len(users) == 1

def test_invalid_email_signup(client):
    response = client.post('/signup', data=dict(username="testuser", password="Testpass123", name="John Doe", email="invalid-email"), follow_redirects=True)

    assert response.status_code == 200
    assert b"Invalid email address. Please enter a valid email." in response.data

    with app.app_context():
        user = BabySitterLogin.query.filter_by(email="invalid-email").first()
        assert user is None

def test_login_page_loads(client):
    response = client.get('/login', content_type='html/text')
    assert response.status_code == 200
    assert b'<input type="email"' in response.data

def test_valid_login(client):
    with app.app_context():
        my_db.add_babysitter(user_name="testuser", password="Testpass123", name="John Doe", email="john.doe@example.com")
    response = client.post('/login', data=dict(email="john.doe@example.com", password="Testpass123"), follow_redirects=True)
    assert response.status_code == 200
    with client.session_transaction() as session:
        assert session.get("user_name") == "testuser"

def test_invalid_login(client):
    response = client.post('/login', data=dict(email="nonexistent@example.com", password="wrongpassword"), follow_redirects=True)
    assert response.status_code == 200
    with client.session_transaction() as session:
        assert session.get("username") is None
        
def test_logout(client):
    with app.app_context():
        my_db.add_babysitter(user_name="testuser", password="Testpass123", name="John Doe", email="john.doe@example.com")
    client.post('/login', data=dict(email="john.doe@example.com", password="Testpass123"), follow_redirects=True)
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    with client.session_transaction() as session:
        assert session.get("user_name") is None

if __name__ == "__main__":
    pytest.main()
