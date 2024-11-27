from flask_sqlalchemy import SQLAlchemy
import bcrypt  #hashing and verifying passwords

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

def setup_database():
        db.create_all()        

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

def get_user_row_if_exists(id):
    user_row = BabySitterLogin.query.filter_by(user_id=id).first()
    if user_row is not None:
        return user_row
    else:
        print(f"The user with id {id} does not exist")
        return False


def validate_user(email, password):
    user = BabySitterLogin.query.filter_by(email=email).first()
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        return {"status": "success", "message": "Login successful", "user": user}
    return {"status": "fail", "message": "Invalid email or password"}

def user_logout(id):
        row = get_user_row_if_exists(id)
        if row is not False:
         db.session.commit()
        
def view_all():
    row = BabySitterLogin.query.all()
    for n in range(0, len(row)):
        print(f"{row[n].id} | {row[n].name} | {row[n].user_id} | {row[n].token} | {row[n].access_level}")

def get_all_logged_in_users():
    row = BabySitterLogin.query.filter_by(login=1).all()
    baby_sitter_records = {"users" : []}
    for n in range(0, len(row)):
        if row[n].access_level == 1:
            read = "checked"
            write = "unchecked"
        elif row[n].access_level == 2:
            read = "checked"
            write = "checked"
        else:
            read = "unchecked"
            write = "unchecked"
        baby_sitter_records["users"].append([row[n].name, row[n].user_id, read, write])
    return baby_sitter_records


class BabySitterData():
       __tablename__ = 'baby_data'
       id = db.Column(db.Integer, primary_key=True, nullable=False)
       time = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.current_timestamp())
       sound_pitch = db.Column(db.Float,nullable=True)
       temperature = db.Column(db.Float,nullable=True)
       humidity = db.Column(db.Float,nullable=True)
       camera_feed_path= db.Column(db.String,nullable=True)
       audio= db.Column(db.String,nullable=True)

       def __init__(self, sound_pitch, temperature, humidity, camera_feed_path, audio ):
        self.sound_pitch = sound_pitch
        self.temperature = temperature
        self.humidity = humidity
        self.camera_feed_path = camera_feed_path
        self.audio = audio


def add_baby_data(sound_pitch, temperature, humidity, camera_feed_path, audio):
        new_baby_data =  BabySitterData(sound_pitch = sound_pitch, temperature = temperature, humidity = humidity, camera_feed_path =camera_feed_path, audio = audio)
        db.session.add(new_baby_data)
        db.session.commit()

def get_baby_temperature(time):
    result = BabySitterData.query.filter_by(time=time).first()
    if result:
        return result.temperature
    return None 

def get_video_record(time):
    result = BabySitterData.query.filter_by(time=time).first()
    if result:
        return result.camera_feed_path
    return None 
