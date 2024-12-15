from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, session
from flask_mysqldb import MySQL
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.exceptions import PubNubException
from dotenv import load_dotenv
import os, re ,bcrypt, requests, json
from oauthlib.oauth2 import WebApplicationClient
from Cryptodome.Cipher import AES 
from pubnub.crypto import PubNubCryptoModule, AesCbcCryptoModule, LegacyCryptoModule
from pubnub.models.consumer.v3.channel import Channel
from pubnub.models.consumer.v3.group import Group
from pubnub.models.consumer.v3.uuid import UUID
import my_db
db= my_db.db





# Function to emit a sound detection notification
def notify_sound_detected():
   print('sound_alert', {'message': 'Sound detected!'})


app = flask = Flask(__name__, static_folder='static')



load_dotenv()
app.secret_key = os.getenv('SECRET_KEY')

app.config['UPLOAD_FOLDER'] = os.path.abspath('uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
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
cipher_key = os.getenv("PUBNUB_CIPHER_KEY")
# pubnub keys and ID
pnconfig = PNConfiguration()

pnconfig.subscribe_key =os.getenv("PUBNUB_SUBSCRIBE_KEY")
pnconfig.publish_key =os.getenv("PUBNUB_PUBLISH_KEY")
pnconfig.secret_key =os.getenv("PUBNUB_SECRET")   
pnconfig.uuid =os.getenv("PUBNUB_NAME") 
pnconfig.cipher_key = cipher_key
pnconfig.cipher_mode = AES.MODE_GCM
pnconfig.fallback_cipher_mode = AES.MODE_CBC
pnconfig.crypto_module = AesCbcCryptoModule(pnconfig)
pubnub =PubNub(pnconfig)

db.init_app(app)

print(f"Flask Secret Key: {os.getenv('SECRET_KEY')}")
print(f"PubNub Secret Key: {os.getenv('PUBNUB_SECRET')}")

channels = {
    "babysitter": {"read": True, "write": True}  
}

channel_groups = {
    "channel-group-babysitter": {"read": True}  
}

uuids = {
    "babysitter": {"get": True, "update": True}  
}

print("Channels:", channels)
print("Channel Groups:", channel_groups)
print("UUIDs:", uuids)


try:
    # Generate the token using correctly structured resources
    envelope = pubnub.grant_token() \
        .channels(channels) \
        .groups(channel_groups) \
        .uuids(uuids) \
        .ttl(1440) \
        .authorized_uuid("babysitter") \
        #.sync()  # Execute the token grant
    
except PubNubException as e:
    print(f"Error generating token: {e}")

#VIDEO_URL = "http://192.168.183.28:8000/video1.mp4"
#SOUND_URL = "http://192.168.183.28:8000/sound1.wav"

VIDEO_URL = "default_video.mp4"
SOUND_URL = "default_sound.wav"
from pubnub.callbacks import SubscribeCallback


def subscribe_to_pubnub():
    class MySubscribeCallback(SubscribeCallback):
        def message(self, pubnub, message):
            global VIDEO_URL, SOUND_URL
            try:
                print(f"Received PubNub message: {message.message}")
                # Update the URLs using the correct keys from the message payload
                if 'video_ready' in message.message:
                    VIDEO_URL = message.message['video_ready']
                    print(f"Updated VIDEO_URL to: {VIDEO_URL}")
                if 'audio_ready' in message.message:
                    SOUND_URL = message.message['audio_ready']
                    print(f"Updated SOUND_URL to: {SOUND_URL}")

                if 'sound_detected' in message.message:
                     print("Sound detected!")
                     pubnub.publish().channel('babysitter').message({
                    'sound_alert': 'Baby is crying!'
                        }).sync()

            except Exception as e:
                print(f"Error in PubNub callback: {e}")
        def status(self, pubnub, status):
            if status.is_error():
                print(f"PubNub status error: {status}")

        def presence(self, pubnub, presence):
            # Handle presence events if needed
            print(f"Presence event: {presence}")

    # Add the listener
    pubnub.add_listener(MySubscribeCallback())

    # Subscribe to the "babysitter" channel
    pubnub.subscribe().channels("babysitter").execute()



SPORTS = ["Basketball", "Badminton","Volleyball"]
REGISTRANTS = {}


guardian_name1 = "John"
guardian_name2 = "Jane"
child_name = "Meghan"

@app.route("/", methods=["GET","POST"])
def index():
    child_name
    guardian_name1
    video_url = VIDEO_URL 
    sound_url = SOUND_URL

    
    subscribe_key = os.getenv("PUBNUB_SUBSCRIBE_KEY")
    publish_key = os.getenv("PUBNUB_PUBLISH_KEY")
    secret_key = os.getenv("PUBNUB_SECRET_KEY") 
   
     
    return render_template("index.html",
                            video_url=video_url, 
                            sound_url=sound_url, 
                            child_name=child_name, 
                            guardian_name1=guardian_name1,
                            guardian_name2=guardian_name2, 
                            pubnub_subscribe_key=subscribe_key, 
                            pubnub_publish_key=publish_key
                            )

@app.route('/static/<path:filename>')
def serve_static_file(filename):
    return send_from_directory(os.path.join(app.root_path, 'static'), filename)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user_name = request.form['username']
        password = request.form['password']
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
        
        # Check if email already exists
        existing_user = my_db.get_babysitter_by_email(email)
        if existing_user:
            flash('Email already registered. Please choose a different email.', 'danger')
            return render_template('signup.html')

        # Save user to database
        my_db.add_babysitter(user_name=user_name, name='', password=password, email=email)
        flash('You have successfully signed up!', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')
@app.route('/manifest.json')
def serve_manifest():
    return send_file('manifest.json', mimetype='application/manifest+json')

@app.route('/sw.js')
def serve_sw():
    return send_file('sw.js', mimetype='application/javascript')
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = my_db.get_babysitter_by_email(email)
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            session['email'] = user.email
            session['name'] = user.name
            session['user_name'] = user.user_name
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
        users_name = user_info.get("name", "Google User")
        
        # Check if user already exists in the database
        existing_user = my_db.get_babysitter_by_email(users_email)
        if not existing_user:
            # Create a new user entry if it is their first time logging in
            my_db.add_babysitter(user_name=unique_id, password="", name=users_name, email=users_email)
            flash('Account created successfully with Google login!', 'success')
        
        session['email'] = users_email
        session['user_name'] = unique_id
        session['name'] = users_name
        flash('Login successful!', 'success')
        return redirect(url_for('loggedin'))
    else:
        flash('User email not available or not verified by Google.', 'danger')
        return redirect(url_for('login'))



@app.route('/loggedin')
def loggedin():
    if 'email' in session:
        return f'Email:{session["email"]}, Username:{session["user_name"]}, Name:{session["name"]}!'
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
    child_name
    return render_template("video.html", video_url=VIDEO_URL, child_name=child_name)


@app.route("/sound")
def sound():
    print(SOUND_URL) 
    return render_template("sound.html", sound_url=SOUND_URL)


@app.route("/history")
def history():
    child_name
    return render_template("history.html", child_name=child_name)


@app.route("/user")
def user():
    child_name
    return render_template("user.html", child_name=child_name)


@app.route("/settings")
def settings():
    child_name
    return render_template("settings.html", child_name=child_name)


@app.route("/onboarding")
def onboarding():
    child_name
    return render_template("onboarding.html", child_name=child_name)



def download_and_save_file(file_url, file_type):
    try:
        # Get the file content
        response = requests.get(file_url, stream=True)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        
        # Determine the file name and path
        file_name = file_url.split("/")[-1]  # Get the file name from the URL
        if file_type == 'video':
            sub_dir = 'videos'
        elif file_type == 'sound':
            sub_dir = 'sounds'
        else:
            raise ValueError("Invalid file type. Must be 'video' or 'sound'.")

        # Ensure the subdirectory exists
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], sub_dir)
        os.makedirs(save_path, exist_ok=True)
        
        # Save the file locally
        file_path = os.path.join(save_path, file_name)
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return file_path  # Return the local path of the saved file
    except requests.RequestException as e:
        raise RuntimeError(f"Error downloading file: {e}")


@app.route("/add_video", methods=["POST"])
def add_video():
    video_url = request.form.get("video_url")
    if not video_url:
        return jsonify({'status': 'error', 'message': 'No video URL provided'}), 400

    try:
        # Download and save the video file locally
        local_path = download_and_save_file(video_url, 'video')
        
        # Add the local file path to the database
        my_db.add_baby_data(camera_feed_path=local_path)
        return jsonify({'status': 'success', 'message': 'Video saved successfully', 'path': local_path})
    except RuntimeError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route("/add_sound", methods=["POST"])
def add_sound():
    sound_url = request.form.get("sound_url")
    if not sound_url:
        return jsonify({'status': 'error', 'message': 'No sound URL provided'}), 400

    try:
        # Download and save the sound file locally
        local_path = download_and_save_file(sound_url, 'sound')
        
        # Add the local file path to the database
        my_db.add_baby_data(audio=local_path)
        return jsonify({'status': 'success', 'message': 'Sound saved successfully', 'path': local_path})
    except RuntimeError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


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
    subscribe_to_pubnub()
    app.run(debug=True)