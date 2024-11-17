from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, session
from flask_mysqldb import MySQL
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.exceptions import PubNubException
from dotenv import load_dotenv
import os, re ,bcrypt, requests, json
from oauthlib.oauth2 import WebApplicationClient
import my_db
db= my_db.db



app = flask = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv('SECRET_KEY')

#app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('MYSQL_HOST')
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}"
    f"@{os.getenv('MYSQL_HOST')}/{os.getenv('MYSQL_DATABASE')}"
)


# Disables OAuth 2 https requirement. (FOR TESTING ONLY)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


# Google OAuth 2
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# pubnub keys and ID
pnconfig = PNConfiguration()
pnconfig.subscribe_key = 'sub-c-f8bff00d-78e1-4bb1-86d5-e81d5043ed37'
pnconfig.publish_key = 'pub-c-a5e694de-d708-4674-9f6a-9df8bdae40a7'
pnconfig.secret_key = 'sec-c-MzVlZDVmMzUtZjU3OC00YjgzLTg2ZWEtN2NlZWIyNWEwNGQ3'  
pnconfig.uuid ='Baby-device'

pubnub =PubNub(pnconfig)

db.init_app(app)

# granting access to post to channel

def grant_access():
    pubnub.grant()\
        .channels("New-channel")\
        .read(True)\
        .write(True)\
        .manage(True)\
        .sync()

grant_access()

VIDEO_URL = "http://192.168.183.28:8000/video1.mp4"
SOUND_URL = "http://192.168.183.28:8000/sound1.wav"


SPORTS = ["Basketball", "Badminton","Volleyball"]
REGISTRANTS = {}

@app.route("/", methods=["GET","POST"])
def index():
    return render_template("index.html", sports=SPORTS)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user_name = request.form['username']
        password = request.form['password']
        name = request.form['name']
        email = request.form['email']
        
        # Check if email is valid
        email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_pattern, email):
            flash('Invalid email address. Please enter a valid email.', 'danger')
            return render_template('signup.html')

        # Password requirements check
        if not re.fullmatch(r'^(?=.*[A-Z])(?=.*\d).{8,}$', password):
            flash('Password must be at least 8 characters long, contain at least one digit, and one uppercase letter.', 'danger')
            return render_template('signup.html')
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Check if email already exists
        existing_user = my_db.get_babysitter_by_email(email)
        if existing_user:
            flash('Email already registered. Please choose a different email.', 'danger')
            return render_template('signup.html')

        # Save user to database
        my_db.add_babysitter(user_name=user_name, password=hashed_password, name=name, email=email)
        flash('You have successfully signed up!', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = my_db.get_babysitter_by_email(email)
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            session['email'] = user.email
            flash('Login successful!', 'success')
            return redirect(url_for('loggedin'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
    return render_template('login.html')

@app.route('/login/google')
def google_login():
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@app.route('/login/google/callback')
def google_callback():
    code = request.args.get("code")

    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    token_endpoint = google_provider_cfg["token_endpoint"]

    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Get user info
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # Store the user information in session
    user_info = userinfo_response.json()
    if user_info.get("email_verified"):
        unique_id = user_info["sub"]
        users_email = user_info["email"]
        session['username'] = users_email
        flash('Login successful!', 'success')
        return redirect(url_for('loggedin'))
    else:
        return redirect(url_for('login'))



@app.route('/loggedin')
def loggedin():
    if 'email' in session:
        return f'Welcome {session["email"]}!'
    else:
        return redirect(url_for('login'))
    
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route("/registrants")
def registrants():
    return render_template("registrants.html", registrants=REGISTRANTS)

@app.route("/register", methods=["GET","POST"])
def register():
    name = request.form.get("name")
    sport = request.form.get("sport")
    if not name:
            return render_template("error.html", message="You must provide a name.")
    if not sport:
        message = "You need to select a sport"
        return render_template("error.html", message=message)
    if sport not in SPORTS:
        message = "Invalid sport."
        return render_template("error.html", message=message)
    REGISTRANTS[name] = sport
    return redirect("/registrants")


@app.route("/video")
def video():
    return render_template("video.html", video_url=VIDEO_URL)
@app.route("/sound")
def sound():
    print(SOUND_URL) 
    return render_template("sound.html", sound_url=SOUND_URL)
   


# publish message to pubnub

@app.route('/publish', methods=['POST'])
def publish_message():
    message = request.json.get('message')
    if message:
        try:
            
            response = pubnub.publish().channel('New-channel').message({'text': message}).sync()

            # sucess
            response_data = {
                'status': 'success' if not response.status.is_error() else 'error',
                'status_code': response.status.status_code  
            }
            
            return jsonify(response_data)
        except PubNubException as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    else:
        return jsonify({'status': 'error', 'message': 'No message provided'}), 400


    # return render_template("success.html")
if __name__ == "__main__":
    app.run(debug=True)