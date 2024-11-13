from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, session
from flask_mysqldb import MySQL
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.exceptions import PubNubException
from dotenv import load_dotenv
import os, re ,bcrypt


app = flask = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv('SECRET_KEY')

# MySQL configurations 
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.config["MYSQL_CUSTOM_OPTIONS"] = {"ssl": {"ca":  os.path.join(os.path.dirname(__file__), 'eu-west-1-bundle.pem')}} 

mysql = MySQL(app)


# pubnub keys and ID
pnconfig = PNConfiguration()
pnconfig.subscribe_key = 'sub-c-f8bff00d-78e1-4bb1-86d5-e81d5043ed37'
pnconfig.publish_key = 'pub-c-a5e694de-d708-4674-9f6a-9df8bdae40a7'
pnconfig.secret_key = 'sec-c-MzVlZDVmMzUtZjU3OC00YjgzLTg2ZWEtN2NlZWIyNWEwNGQ3'  
pnconfig.uuid ='Baby-device'

pubnub =PubNub(pnconfig)

# granting access to post to channel

def grant_access():
    pubnub.grant()\
        .channels("New-channel")\
        .read(True)\
        .write(True)\
        .manage(True)\
        .sync()

grant_access()

SPORTS = ["Basketball", "Badminton","Volleyball"]
REGISTRANTS = {}

@app.route("/", methods=["GET","POST"])
def index():
    return render_template("index.html", sports=SPORTS)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Password requirements check
        if not re.fullmatch(r'^(?=.*[A-Z])(?=.*\d).{8,}$', password):
            flash('Password must be at least 8 characters long, contain at least one digit, and one uppercase letter.', 'danger')
            return render_template('signup.html')
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Check if username already exists
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", [username])
        existing_user = cur.fetchone()
        if existing_user:
            flash('Username already taken. Please choose a different username.', 'danger')
            return render_template('signup.html')
        
        # Save user to database
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(username, password) VALUES(%s, %s)", (username, hashed_password))
        mysql.connection.commit()
        cur.close()
        
        flash('You have successfully signed up!', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Fetch user from database
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username=%s", [username])
        user = cur.fetchone()
        cur.close()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
            session['username'] = user[1]
            flash('Login successful!', 'success')
            return redirect(url_for('loggedin'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')


@app.route('/loggedin')
def loggedin():
    if 'username' in session:
        return f'Welcome {session["username"]}!'
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