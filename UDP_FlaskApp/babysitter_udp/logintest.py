from my_db import db, add_babysitter, get_babysitter_by_email, delete_all_users, validate_user
from flask import Flask
import bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://root:14053yr@127.0.0.1/babysitter"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)
# Test methods
def test_db_methods():
    with app.app_context():
        delete_all_users()
        print("Deleted all existing users.")

if __name__ == "__main__":
    test_db_methods()