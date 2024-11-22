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

class BabySitterData():
       __tablename__ = 'baby_data'
       id = db.Column(db.Integer, primary_key=True, nullable=False)
       time = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.current_timestamp())
       sound_pitch = db.Column(db.Float,nullable=True)
       temperature = db.Column(db.Float,nullable=True)
       humidity = db.Column(db.Float,nullable=True)
       camera_feed_path= db.Column(db.Float,nullable=True)
       audio= db.Column(db.Float,nullable=True)

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
