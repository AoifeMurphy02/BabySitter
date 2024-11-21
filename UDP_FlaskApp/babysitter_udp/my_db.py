from flask_sqlalchemy import SQLAlchemy
import bcrypt  #for hashing and verifying passwords

db = SQLAlchemy()

class BabySitterLogin(db.Model):
    __tablename__ = 'baby_sitter_login'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    time = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.current_timestamp())
    user_name = db.Column(db.String(255), nullable=True)
    password = db.Column(db.String(255), nullable=True)
    name = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(255), nullable=True)

    def __init__(self, user_name, password, name, email):
        self.user_name = user_name
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        self.name = name
        self.email = email

def add_babysitter(user_name, password, name, email):
        new_babysitter = BabySitterLogin(user_name=user_name, password=password, name=name, email=email)
        db.session.add(new_babysitter)
        db.session.commit()

def get_babysitter_by_email(email):
        return BabySitterLogin.query.filter_by(email=email).first()

def delete_all_users():
        try:
                db.session.query(BabySitterLogin).delete()
                db.session.commit()
        except Exception as e:
                print("Delete failed " +str(e))
                db.session.rollback()

def get_user_row_if_exists(user_id):
    user_row = BabySitterLogin.query.filter_by(user_id=user_id).first()
    if user_row is not None:
        return user_row
    else:
        print(f"The user with id {user_id} does not exist")
        return False


def validate_user(email, password):
    user = BabySitterLogin.query.filter_by(email=email).first()
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        return {"status": "success", "message": "Login successful", "user": user}
    return {"status": "fail", "message": "Invalid email or password"}