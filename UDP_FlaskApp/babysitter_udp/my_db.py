from flask_sqlalchemy import SQLAlchemy

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
        self.password = password
        self.name = name
        self.email = email

def add_babysitter(user_name, password, name, email):
        new_babysitter = BabySitterLogin(user_name=user_name, password=password, name=name, email=email)
        db.session.add(new_babysitter)
        db.session.commit()

def get_babysitter_by_email(email):
        return BabySitterLogin.query.filter_by(email=email).first()